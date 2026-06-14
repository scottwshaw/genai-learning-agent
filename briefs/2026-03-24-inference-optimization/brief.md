# Inference Optimization — Research Brief (2026-03-24)

## Key Developments

- **FP4 (NVFP4) quantization arrives as production tool on Blackwell**: TensorRT-LLM v0.17+ now includes native NVFP4 support for B200 and other Blackwell GPUs. FP4 doubles throughput over FP8 on the same hardware (and ~4x over FP16), but is **Blackwell-only** — not available on H100/H200. The recommended workflow is NVIDIA ModelOpt for PTQ calibration → TensorRT-LLM for engine build + serving. [Spheron blog, Mar 2026]
- **Microsoft Azure deploys DeepSeek-V3.2 on NVFP4/TensorRT-LLM on Blackwell**: Production deployment using NVFP4-quantized weights for DeepSeek-V3.2 via TensorRT-LLM on Blackwell GPUs — a high-profile validation that FP4 is production-ready at scale for frontier MoE models. [Microsoft Community Hub, ~Feb 26, 2026]
- **Serving engine benchmark: TensorRT-LLM > SGLang > vLLM on H100 at scale**: A fresh Spheron benchmark (vLLM v0.18.0, TRT-LLM v1.2.0, SGLang v0.5.9) on single H100 with Llama-3.3-70B-Instruct at FP8 shows TensorRT-LLM leads at every concurrency level — 2,780 tok/s at 100 concurrent requests vs vLLM's 2,400 (16% gap). TTFT edge goes to TRT-LLM (105ms p50 @ 10 req) but cold-start cost is severe (~28 min vs ~60s for vLLM/SGLang). [Spheron blog, Mar 2026]
- **SGLang and LMDeploy lead open-source throughput on H100 for most workloads**: Separate PremAI benchmarks across 13+ engines find SGLang and LMDeploy both hit ~16,200 tok/s on H100 for Llama 3.1 8B, versus vLLM's ~12,500 tok/s (29% gap). SGLang's RadixAttention gives 10-20% additional benefit on shared-prefix workloads. LMDeploy is 2.4x faster than vLLM at INT4 quantization specifically. [PremAI blog, Mar 2026]
- **Intel OpenVINO 2026 adds improved NPU handling and mixed-precision LLM inference**: OpenVINO now auto-detects attention/FFN/layernorm subgraphs and converts them to efficient kernels; a new Mixed-Precision Engine lets developers run LLM inference on NPUs and CPUs alongside GPU, expanding inference optimization beyond NVIDIA hardware. [IT's FOSS, Feb 2026]

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| NVFP4 Pretraining paper (arXiv:2509.25149 v2) | Mar 4, 2026 | NVIDIA / arXiv | Updated preprint showing NVFP4 training approach maintains quality vs FP16; used in production quantization workflows |
| TensorRT-LLM v1.2.0 | Mar 2026 | NVIDIA / Spheron benchmarks | CUDA 13.1 baseline; most mature FP4/FP8 support; 13-16% throughput lead vs vLLM at scale; 28-min engine compile trade-off |
| vLLM v0.18.0 | Mar 2026 | vllm-project/vllm | Latest stable; WebSocket Realtime API from v0.16; FP8/Blackwell improvements; multi-platform (NVIDIA, AMD ROCm, Intel XPU, TPU) |
| SGLang v0.5.9 | Mar 2026 | lm-sys/sglang | RadixAttention + shared-prefix caching; best for agentic/multi-turn workloads; matches LMDeploy at ~16,200 tok/s |
| LMDeploy (TurboMind C++ backend) | Mar 2026 | InternLM/lmdeploy | C++ TurboMind engine; best-in-class INT4 throughput (2.4x vs vLLM); lowest TTFT overall |
| KV Cache Transform Coding (arXiv:2511.01815) | Recent | arXiv [cs.CL] | Transform-coding approach to KV compression; outperforms token eviction + quantization + SVD baselines at higher compression ratios |

## Technical Deep-Dive

### FP4 (NVFP4) on Blackwell: The Precision-Performance Trade-off

NVFP4 uses the E2M1 format: 1 sign bit, 2 exponent bits, 1 mantissa bit. That floating-point representation (vs INT4's fixed-range integer format) is the key advantage — transformers have weight and activation distributions spanning many orders of magnitude, and the floating-point dynamic range of NVFP4 typically preserves more model quality than INT4 at the same 4-bit width.

The performance math is straightforward: each halving of bit width roughly doubles both the values that fit per memory access and the tensor core operations per clock. Blackwell's FP4 tensor cores deliver ~20 PFLOPS peak (vs ~10 PFLOPS FP8 on B200), and the 192 GB HBM3e at 8 TB/s bandwidth means FP4 is now **compute-bound, not memory-bound** for many transformer workloads — a regime shift from Hopper where inference was typically memory-bandwidth-limited.

**Practical constraints in March 2026:**
- FP4 is **hardware-gated to Blackwell** (B200, B300, RTX 5090, RTX PRO 6000). No fallback on H100/H200.
- B200 supply is severely constrained (3-6 month lead times for large orders as of early 2026).
- Quality tradeoffs are task-dependent. Most LLM tasks see negligible degradation; some tasks (precise arithmetic, code generation corner cases) show measurable regressions. Calibration quality matters.
- The recommended stack is NVIDIA ModelOpt (PTQ calibration) + TensorRT-LLM v0.17+ (build + serve). vLLM FP4 support for Blackwell is less mature as of this writing.

### Serving Engine Selection: The Real Decision Matrix

The Spheron benchmark exposes a key nuance often obscured in marketing comparisons: **workload profile matters more than raw throughput numbers**.

- **TensorRT-LLM** wins on throughput at scale (13-16% over vLLM, 9-13% over SGLang at 50-100 concurrent requests) but carries a brutal cold-start cost (~28 minutes to compile an engine vs ~60 seconds to load for vLLM/SGLang). This makes TRT-LLM appropriate for stable, long-running production deployments on a single fixed model — not for research workflows or teams that iterate on models frequently.
- **SGLang**'s RadixAttention advantage is **workload-conditional**. In the Spheron benchmark with unique prompts, SGLang barely edges vLLM. On shared-prefix workloads (RAG pipelines, chatbots with system prompts, multi-turn conversations), it wins by 10-20%. Agentic pipelines — where many calls share the same context prefix — see the largest benefit.
- **vLLM** remains the pragmatic default: easiest deployment, broadest model support, active ecosystem, Kubernetes/Ray integration, and the multi-platform reach (ROCm, XPU, TPU) that others lack. The 29% throughput gap vs SGLang/LMDeploy is real but translates to hardware cost, not capability.
- **LMDeploy**'s TurboMind C++ backend is under-discussed: it ties SGLang at raw H100 throughput and beats both at INT4 quantization (2.4x vs vLLM). If you're serving quantized models and don't need agentic prefix caching, LMDeploy deserves evaluation.

## Implications & Trends

- **The H100-to-Blackwell FP4 migration window is opening, not open**: FP4's 2x throughput advantage over FP8 on Blackwell is compelling on paper, but supply constraints and framework maturity gaps (especially outside TRT-LLM) mean most production deployments won't access it until late 2026. Teams should be planning FP4 evaluation now, not assuming it's available.
- **Cold-start cost is the underrated deployment variable**: The 28-minute TRT-LLM engine compile time is a real operational constraint for autoscaling, spot instance deployment, and any scenario where inference capacity needs to appear quickly. The throughput-vs-agility trade-off will push many teams toward vLLM/SGLang despite their lower ceiling.
- **INT4 quantization is having a quiet renaissance**: While FP4 gets the headlines, LMDeploy's 2.4x INT4 advantage and vLLM's AWQ/GPTQ support show that lower-precision integer quantization — available on all modern hardware — remains highly practical. For teams not on Blackwell, INT4 via LMDeploy or AWQ may be the most cost-effective optimization path available today.
- **Hardware diversity is forcing serving-layer complexity**: vLLM's support for NVIDIA, AMD ROCm, Intel XPU, and TPU in v0.16 reflects a real multi-hardware reality. The inference optimization stack increasingly needs to abstract over hardware targets, not optimize for one — except at the performance ceiling where hardware-specific kernels (FA4, NVFP4) dominate.

## Sources

- https://www.spheron.network/blog/fp4-quantization-blackwell-gpu-cost/ [News/Analysis, Mar 2026]
- https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/unlocking-high-performance-inference-for-deepseek-with-nvfp4-on-nvidia-blackwell/4497936 [Official announcement]
- https://www.spheron.network/blog/vllm-vs-tensorrt-llm-vs-sglang-benchmarks/ [Benchmarks, Mar 2026]
- https://blog.premai.io/vllm-vs-sglang-vs-lmdeploy-fastest-llm-inference-engine-in-2026/ [Benchmarks, Mar 2026]
- https://arxiv.org/abs/2509.25149 [arXiv — NVIDIA, NVFP4 pretraining]
- https://arxiv.org/abs/2511.01815 [arXiv — KV cache transform coding]
- https://itsfoss.gitlab.io/post/intel-releases-openvino-2026-with-improved-npu-handling-expanded-llm-support/ [News]
- https://dev.to/soytuber/vllm-vs-tensorrt-llm-vs-ollama-vs-llamacpp-choosing-the-right-inference-engine-on-rtx-5090-2aap [Community analysis]
