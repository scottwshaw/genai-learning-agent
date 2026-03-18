# Inference Optimization — Research Brief (2026-03-18)

## Key Developments

- **NVIDIA Dynamo 1.0 enters production (Mar 16, 2026):** NVIDIA released Dynamo 1.0, an open-source "inference operating system" for AI factories that disaggregates prefill and decode phases across GPU clusters, delivering up to 7x throughput improvement on Blackwell GPUs (SemiAnalysis InferenceX benchmark, DeepSeek R1-0528, FP4, 1k/1k tokens). Adopted in production by Baseten, ByteDance, Cursor, Perplexity, and major cloud providers (AWS, Azure, Google Cloud, OCI).
- **P-EAGLE parallel speculative decoding ships in vLLM (Mar 13, 2026):** AWS researchers integrated P-EAGLE into vLLM v0.16.0, replacing EAGLE-3's sequential draft generation with a single parallel forward pass for all K draft tokens. Achieves 1.05×–1.69× speedup over vanilla EAGLE-3 on B200 GPUs across MT-Bench, HumanEval, and SpeedBench. Pre-trained drafter heads now on HuggingFace for GPT-OSS 120B/20B and Qwen3-Coder 30B.
- **MIT Attention Matching compacts KV cache 50x without training (Feb 18 paper, covered Mar 2026):** Researchers published arXiv:2602.16284 describing a fast KV compaction method that constructs compact keys and values to reproduce per-head attention outputs using only a set of reference queries — no GPU fine-tuning required. Outperforms token eviction, SVD, and quantization-based compression at high reduction ratios.
- **NVFP4 quantization matures for Blackwell (Mar 2026):** TensorRT-LLM 0.17+ ships native NVFP4 support for B200/B300/RTX 5090 GPUs; vLLM and SGLang now also support NVFP4 models. FP4 tensor cores deliver roughly 2× the TFLOPS of FP8 on the same Blackwell silicon, with Microsoft's Azure team validating this on DeepSeek-V3.2 at rack scale (GB200 NVL72).
- **Disaggregated inference hits 70% throughput gains in production (Mar 17, 2026):** AWS's open-source llm-d framework, alongside Dynamo, is reporting ~70% throughput improvements by routing prefill-heavy and decode-heavy traffic to separately scaled GPU pools, marking disaggregated inference's formal transition from research to production architecture.

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| NVIDIA Dynamo 1.0 | Mar 16, 2026 | [NVIDIA GlobeNewswire](https://www.globenewswire.com/news-release/2026/03/16/3256759/0/en/NVIDIA-Enters-Production-With-Dynamo-the-Broadly-Adopted-Inference-Operating-System-for-AI-Factories.html) | Open-source distributed inference OS; disaggregated prefill/decode, KVBM memory manager, NIXL GPU-to-GPU transfer, Grove scaling orchestrator; 7x Blackwell throughput gains |
| P-EAGLE: Parallel Speculative Decoding | Mar 13, 2026 | [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/p-eagle-faster-llm-inference-with-parallel-speculative-decoding-in-vllm/) / [arXiv:2602.01469](https://arxiv.org/abs/2602.01469) | Converts EAGLE's autoregressive draft head to a single-pass parallel generator; now in vLLM v0.16.0 |
| Fast KV Compaction via Attention Matching | Feb 18, 2026 | [arXiv:2602.16284](https://arxiv.org/abs/2602.16284) (MIT, affiliated) | Training-free KV cache compression; 50x reduction with minimal accuracy loss; solves ultra-long-context memory bottleneck |
| NVFP4 on Blackwell (TensorRT-LLM 0.17) | Mar 2026 | [NVIDIA Dev Blog](https://developer.nvidia.com/blog/3-ways-nvfp4-accelerates-ai-training-and-inference/) | Hardware-native 4-bit float format; 2× throughput over FP8; supported in TRT-LLM, vLLM, SGLang |
| KV Cache Transform Coding (KVTC) | Nov 2025 (resurface Mar 2026) | [arXiv:2511.01815](https://arxiv.org/abs/2511.01815) | Transform coding for compact KV storage; outperforms eviction, quantization, and SVD baselines |
| SGLang vs vLLM vs LMDeploy benchmark | Feb 2026 | [PremAI Blog](https://blog.premai.io/vllm-vs-sglang-vs-lmdeploy-fastest-llm-inference-engine-in-2026/) | SGLang and LMDeploy reach ~16,200 tok/s on H100; vLLM at ~12,500 tok/s (29% gap); vLLM leads on multi-LoRA and speculative decoding |

## Technical Deep-Dive

**NVIDIA Dynamo 1.0: Disaggregated Inference as Infrastructure Primitive**

Dynamo 1.0's central architectural insight is that the two phases of LLM inference — prefill and decode — have fundamentally different compute profiles and should not compete on the same GPUs. Prefill (processing the input prompt) is compute-bound: the transformer runs one full forward pass over potentially thousands of input tokens, generating the KV cache. Decode (generating one output token per step) is memory-bandwidth-bound: it performs a full pass over all model weights and the entire KV cache per token, but produces only a single output. Co-locating both on the same GPU means each phase degrades the other.

Dynamo makes disaggregation operational by solving three hard sub-problems. First, **NIXL** (NVIDIA Inference Transfer Library) provides fast GPU-to-GPU and GPU-to-storage KV cache movement, which is mandatory once prefill workers hand off their computed KV caches to decode workers. On GB200 NVL72 systems, NVLink fabric enables this transfer at terabytes-per-second bandwidth. Second, **KVBM** (KV Block Manager) tracks KV cache blocks across the cluster so that requests sharing common prefixes (e.g., repeated system prompts, tool definitions) can reuse already-computed cache rather than recompute from scratch — a form of distributed prefix caching. Third, **Grove** is the orchestrator that handles routing, request scheduling, and dynamic scaling of prefill vs. decode worker pools, acting as a cluster-level load balancer aware of which GPU has which cached context.

In SemiAnalysis's March 2026 InferenceX benchmark, Dynamo on GB200 NVL72 with disaggregated serving and wide expert parallelism achieved a 7× improvement in served requests per second for DeepSeek R1-0528 at FP4 precision (1k input / 1k output tokens, ~50 tok/sec per-user interactivity constraint). AWS's own llm-d framework, following the same disaggregation pattern with EFA-based data movement, reports ~70% throughput gains. The limitation worth noting: disaggregated inference adds operational complexity — two separate scaling policies, two GPU pools, and a transfer layer to manage. It pays off at scale but adds overhead for small deployments.

## Implications & Trends

- **Disaggregated inference is the new default at scale:** Dynamo's production graduation means the prefill/decode split is no longer an experimental trick — it's becoming the baseline architecture for cloud-scale inference. Organizations still running monolithic serving will face increasing cost disadvantage as Blackwell deployments scale.
- **FP4 is Blackwell's killer feature, but verification is mandatory:** NVFP4's 2× throughput advantage over FP8 is compelling, but the quality regression is measurable for tasks requiring fine numeric precision (arithmetic reasoning, structured data extraction). The emerging pattern is tiered quantization — FP4 for high-volume, latency-tolerant routes and FP8/BF16 reserved for precision-sensitive requests within the same serving stack.
- **KV cache compression moves from memory management to context architecture:** Attention Matching's 50x compression ratio, combined with KVBM's block-level caching, signals that KV cache is becoming a first-class architectural primitive rather than an implementation detail — enabling multi-session continuity, cross-request sharing, and ultra-long-context serving that were previously GPU-memory-limited.

## Sources

- https://www.globenewswire.com/news-release/2026/03/16/3256759/0/en/NVIDIA-Enters-Production-With-Dynamo-the-Broadly-Adopted-Inference-Operating-System-for-AI-Factories.html [Official announcement]
- https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/ [Lab blog]
- https://aws.amazon.com/blogs/machine-learning/p-eagle-faster-llm-inference-with-parallel-speculative-decoding-in-vllm/ [Lab blog]
- https://arxiv.org/abs/2602.01469 [arXiv - affiliated (Amazon)]
- https://arxiv.org/abs/2602.16284 [arXiv - affiliated (MIT)]
- https://venturebeat.com/orchestration/new-kv-cache-compaction-technique-cuts-llm-memory-50x-without-accuracy-loss [News]
- https://developer.nvidia.com/blog/3-ways-nvfp4-accelerates-ai-training-and-inference/ [Lab blog]
- https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/unlocking-high-performance-inference-for-deepseek-with-nvfp4-on-nvidia-blackwell/4497936 [Lab blog]
- https://www.spheron.network/blog/fp4-quantization-blackwell-gpu-cost/ [News]
- https://blog.premai.io/vllm-vs-sglang-vs-lmdeploy-fastest-llm-inference-engine-in-2026/ [News]
- https://arxiv.org/abs/2511.01815 [arXiv - affiliated]
- https://ai-infra.jimmysong.io/brief/2026-03-17/ [News]
