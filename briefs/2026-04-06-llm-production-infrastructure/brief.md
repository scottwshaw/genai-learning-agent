# LLM Production Infrastructure — Research Brief (2026-04-06)

## Key Developments

- **Gemma 4's Apache 2.0 license and day-zero serving support change the cost calculus for self-hosted production workloads**
  - **What changed:** Google DeepMind released Gemma 4 on April 2 under Apache 2.0, with day-zero support across vLLM, SGLang, and llama.cpp on both NVIDIA and AMD hardware.
  - **Why it matters:** Unrestricted commercial licensing combined with a 26B MoE variant (3.8B active parameters) makes fine-tuned, sovereign LLM deployment materially cheaper for regulated enterprises.
  - *(Google DeepMind Blog / The Register, April 2, 2026)*

- **Langfuse v4 self-hosted migration still pending three weeks after Cloud launch, stranding data-residency-constrained teams**
  - **What changed:** As of April 6, Langfuse's v4 Observations v2 and Metrics v2 endpoints remain unavailable for self-hosted deployments; the team confirms it is still testing automated migration tooling.
  - **Why it matters:** Regulated enterprises locked to self-hosted deployments cannot access the 10x+ analytics performance gains, widening the cloud-vs-on-prem capability gap in observability.
  - *(Langfuse GitHub Discussion #12518 / v4 docs page, March–April 2026)* [Tier 2 sources only]

- **GKE Inference Gateway + llm-d now pair KV-cache-aware routing with Gemma 4 at GA, establishing a production reference pattern for Kubernetes-native serving**
  - **What changed:** Google Cloud paired Gemma 4's April 2 release with updated GKE tutorials integrating the GA Inference Gateway and llm-d's predicted-latency-based scheduling over vLLM.
  - **Why it matters:** KV-cache-utilization-based autoscaling and prefix-aware routing are now available as a fully supported, cloud-native stack — reducing the need for bespoke serving infrastructure.
  - *(Google Cloud Blog, April 2–3, 2026)*

- **OTel GenAI semantic conventions add evaluation events and agent span guidance, incrementally closing the standardisation gap for production observability**
  - **What changed:** Recent OTel semantic-convention releases introduced a formal `gen_ai.evaluation` event type capturing score labels and a clarified `invoke_agent` span kind with CLIENT/INTERNAL guidance.
  - **Why it matters:** Standardised evaluation events in trace data mean observability platforms can align eval results with traces without custom attribute schemas, reducing instrumentation lock-in.
  - *(OpenTelemetry Semantic Conventions GitHub / opentelemetry.io, March–April 2026)*

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Gemma 4 (E2B, E4B, 26B MoE, 31B Dense) | Apr 2, 2026 | [Google DeepMind](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) | Apache 2.0; 256K context (large models), 128K (edge); native function calling, structured JSON output, vision/audio; day-zero vLLM + SGLang support |
| Gemma 4 on Google Cloud / GKE | Apr 2–3, 2026 | [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/gemma-4-available-on-google-cloud) | Vertex AI, Cloud Run, GKE deployment guides; GKE Agent Sandbox for code/tool call isolation; Sovereign Cloud availability |
| Langfuse Python SDK v4.0.6 | Apr 1, 2026 | [PyPI](https://pypi.org/project/langfuse/) | SDK v4.0.6 is latest; self-hosted users warned not to use new default `api.observations` or `api.metrics` endpoints; legacy v1 endpoints still required for OSS |
| Langfuse v4 Cloud rollout (ongoing) | Mar–Apr 2026 | [Langfuse GitHub Releases](https://github.com/langfuse/langfuse/releases) | Active fix cycle on v4 queries (session truncation, image rendering, categorical filter exports, v4 search); self-hosted migration tooling still in development |
| OTel Semantic Conventions: Evaluation Event (`gen_ai.evaluation`) | Mar–Apr 2026 | [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/) | New event type to capture evaluation scores with `gen_ai.evaluation.score.label`; parented to GenAI operation span; agent span kind (CLIENT/INTERNAL) clarified |
| Gemma 4 AMD ROCm deployment (vLLM + SGLang) | Apr 2, 2026 | [MayhemCode](https://www.mayhemcode.com/2026/04/gemma-4-amd-gpu-support-vllm-sglang.html) | Day-zero AMD Instinct (MI300X/MI325X/MI35X) and Radeon support; Triton backend required for bidirectional image-token attention |
| Langfuse v4 architecture blog | Mar 10, 2026 | [Langfuse Blog](https://langfuse.com/blog/2026-03-10-simplify-langfuse-for-scale) | Technical explanation of observation-centric data model: immutable ClickHouse table, 10x+ dashboard load improvement, OpenTelemetry-driven immutability |
| OTel GenAI Agent Spans: `invoke_agent` guidance | Mar–Apr 2026 | [OTel Semantic Conventions GitHub](https://github.com/open-telemetry/semantic-conventions/releases) | `invoke_agent` spans now include CLIENT kind for remote agents (AWS Bedrock, OpenAI Assistants), INTERNAL for in-process (LangChain, CrewAI); MCP tool execution tracing called out |

## Technical Deep-Dive

### Gemma 4's Serving Architecture: What the MoE + Apache 2.0 Combination Means Operationally

Google DeepMind's Gemma 4 launch on April 2, 2026 is operationally significant for enterprise serving teams in a way that separates it from typical open-weight model releases. The combination of Apache 2.0 licensing and a purpose-built MoE inference profile changes the self-hosting economics in a measurable way.

The standout deployment target is the 26B-A4B MoE variant. 
Despite 25.2 billion total parameters, only 3.8 billion activate per token during inference, meaning self-hosting it requires significantly less VRAM than a comparable dense model — closer to running a 4B model than a 26B one.
 That memory profile means a single A100 80GB or H100 SXM — hardware many regulated enterprises already have — can serve the model at production request loads. For comparison, Llama 4 Maverick (also MoE) requires the same active parameter count but has 400B total parameters. Gemma 4's much smaller "cold" footprint matters for fleet economics.

The Gemma 4 MoE architecture does diverge from the DeepSeek/Qwen pattern. 
Gemma adds MoE blocks as separate layers alongside standard MLP blocks and sums their outputs, rather than replacing MLP blocks with sparse experts — an unusual design choice that trades some efficiency for architectural simplicity.
 This means inference kernels optimised for DeepSeek-style MoE routing may not transfer directly; teams should validate vLLM or SGLang throughput numbers on their own hardware rather than inferring from prior MoE benchmarks.

The serving infrastructure context is equally important. 
Google confirmed day-one support for vLLM, SGLang, llama.cpp, MLX, Ollama, NVIDIA NIM and NeMo, LM Studio, Unsloth, Hugging Face Transformers, and more.
 This level of ecosystem coordination — with AMD publishing verified Docker images for Instinct hardware the same day, and Red Hat AI Inference Server offering a technology preview — signals a deliberate effort to eliminate the "wait for framework support" delay that historically added weeks to production readiness for new open-weight models. 
The Triton backend is required — not optional — because of the bidirectional image-token attention Gemma 4 uses for multimodal input processing; AMD published this explicitly rather than burying it in a compatibility matrix.


For enterprises deploying on Kubernetes, Google paired the launch with updated GKE tutorials using the GA Inference Gateway. 
Pairing Gemma 4's multi-step planning capabilities with the new GKE Agent Sandbox, developers can safely execute LLM-generated code and tool calls within highly isolated, Kubernetes-native environments with sub-second cold starts; by leveraging the GKE Inference Gateway and advanced distributed inference features in llm-d like predicted-latency-based scheduling, these complex workflows benefit from intelligent routing that dynamically balances cache reuse and server load.


The Apache 2.0 licensing change is the less-discussed but strategically important element. Previous Gemma generations shipped under a custom usage policy that barred commercial use above certain scale thresholds. Apache 2.0 removes those restrictions entirely. For procurement teams in regulated industries, this eliminates a compliance review step that previously added friction to deploying Gemma variants as base models for domain-specific fine-tunes.

The key limitation for enterprise adoption is context window asymmetry: edge models (E2B/E4B) support 128K tokens while the larger models support 256K. 
The models feature context windows up to 256K, native vision and audio processing, and fluency in over 140 languages.
 At 256K, Gemma 4's larger variants have roughly a quarter of Llama 4 Scout's 1M-token context window — sufficient for most enterprise document workflows but insufficient for the "fit the entire codebase in context" pattern that 1M+ token windows enable.

## Landscape Trends

- **Apache 2.0 is becoming the de facto commercial license floor for enterprise-grade open-weight models.** Gemma 4 joins Llama 4 (custom but commercially permissive), Mistral, and Qwen in signalling that meaningful enterprise adoption requires unrestricted commercial use. The Gemma shift specifically — from a restrictive custom license to Apache 2.0 — suggests Google's strategy has shifted from protecting model usage to maximising deployment surface as a lever for GCP platform adoption. Teams evaluating open-weight models for regulated deployments should now filter primarily on licence + serving efficiency rather than capability headline numbers.

- **The Langfuse v4 cloud-vs-self-hosted gap is a leading indicator of a broader pattern in LLM observability tooling.** 
The March 10 launch was for Langfuse Cloud; the team is working through automated migration tooling and validating the dual-write setup for open-source ClickHouse deployments, with migration guides and a V4 release for self-hosters to follow in coming weeks.
 Three weeks later, the OSS release remains pending. This cloud-first rollout strategy is structurally rational for a vendor validating a major architecture change, but it creates a real operational disparity: the teams most likely to be running self-hosted (regulated enterprises with data-residency constraints) are precisely those who cannot access the v4 performance gains. As more observability vendors follow ClickHouse's acquisition playbook of deep database coupling, this tension will recur.

- **KV-cache-aware routing is consolidating from a research concept into expected Kubernetes infrastructure.** The GKE Inference Gateway (GA since September 2025) pairing with llm-d and vLLM for Gemma 4 deployments represents a pattern now documented by multiple sources: autoscaling on `inference_pool_average_kv_cache_utilization` rather than CPU, prefix-cache-aware load balancing to reduce redundant prefill computation, and disaggregated prefill/decode scheduling. The March 29 brief covered the Gartner inference cost forecast (90% drop by 2030 offset by 5–30x more tokens per agentic task); KV-cache-aware routing and intelligent model selection are the operational levers that will determine whether enterprise teams capture that cost reduction or see it consumed by workload growth.

- **OpenTelemetry GenAI semantic conventions are incrementally gaining production coverage, but remain experimental.** 
As of March 2026, most GenAI semantic conventions are in experimental status; for production adoption, the `OTEL_SEMCONV_STABILITY_OPT_IN` environment variable allows dual-emission of both legacy and new attribute names, maintaining compatibility during version transitions.
 The recent addition of `gen_ai.evaluation` events and the `invoke_agent` span kind clarification extend coverage toward the two areas enterprise teams care most about — eval integration and agent tracing. However, the absence of stable status means instrumentation authors must hedge with dual-emission, and tool vendors (Langfuse, Arize, Braintrust) continue to ship proprietary attribute schemas alongside OTel support. Stabilisation of GenAI conventions is the single change that would most accelerate vendor-portable observability for enterprise teams.

- **Gemma 4's multimodal-from-day-one architecture reflects a broader production shift: multimodal inference is no longer a special case.** All four Gemma 4 variants natively accept image and video; the E2B/E4B variants additionally support audio. 
Every Gemma 4 model accepts text, image, and video input out of the box; the two smallest variants (E2B and E4B) go further by supporting audio input, making them well suited for speech-aware applications without requiring a separate model.
 This affects serving infrastructure planning: vLLM's GPU-less multimodal preprocessing (introduced in v0.18.0, covered in the March 24 brief) and Gemma 4's configurable token-budget vision encoder together enable more granular tradeoffs between accuracy and GPU cost for multimodal workloads. Teams that built separate vision and text serving pipelines should now evaluate whether a single Gemma 4 deployment reduces operational complexity.

## Vendor Landscape

| Vendor | Event | Date | Details |
|--------|-------|------|---------|
| Google DeepMind | Gemma 4 released under Apache 2.0 | Apr 2, 2026 | Four model sizes (E2B, E4B, 26B MoE, 31B Dense); 256K context (large models); native multimodal; day-zero vLLM/SGLang/llama.cpp support; Sovereign Cloud availability |
| Google Cloud | GKE Inference Gateway + llm-d Gemma 4 tutorials | Apr 2–3, 2026 | Updated GKE deployment guides; GKE Agent Sandbox (sub-second cold starts, 300 sandboxes/sec); Inference Quickstart for tailored GPU/accelerator recommendations |
| Langfuse / ClickHouse | v4 Cloud beta continues; OSS migration pending | Mar–Apr 2026 | Active query-fix releases (v3.16x); v4 self-hosted migration tooling not yet shipped; Python SDK at v4.0.6 |
| OpenTelemetry GenAI SIG | Evaluation event + agent span conventions added | Mar–Apr 2026 | `gen_ai.evaluation` event type; `invoke_agent` CLIENT/INTERNAL span guidance; MCP tool execution tracing callouts; still experimental status |
| Red Hat | AI Inference Server Technology Preview for Gemma 4 | Apr 2, 2026 | Day-zero vLLM-based container support for Gemma 4 across NVIDIA and AMD GPU targets |

## Sources

- https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ [Tier 1 — Lab research (Google DeepMind)]
- https://cloud.google.com/blog/products/ai-machine-learning/gemma-4-available-on-google-cloud [Tier 1 — Lab research (Google Cloud)]
- https://www.theregister.com/2026/04/02/googles_gemma_4_open_weights/ [Tier 1 — Independent journalism (The Register)]
- https://vllm.ai/blog/gemma4 [Tier 2 — Vendor announcement (vLLM)]
- https://www.mayhemcode.com/2026/04/gemma-4-amd-gpu-support-vllm-sglang.html [Tier 2 — Tech news]
- https://developers.redhat.com/articles/2026/04/02/run-gemma-4-red-hat-ai-day-0-step-step-guide [Tier 2 — Vendor announcement (Red Hat)]
- https://docs.cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm [Tier 1 — Lab research (Google)]
- https://github.com/kubernetes-sigs/gateway-api-inference-extension [Tier 2 — GitHub (CNCF / Kubernetes SIG)]
- https://langfuse.com/blog/2026-03-10-simplify-langfuse-for-scale [Tier 2 — Vendor announcement]
- https://langfuse.com/docs/v4 [Tier 2 — Vendor docs]
- https://github.com/orgs/langfuse/discussions/12518 [Tier 2 — GitHub discussion]
- https://langfuse.com/docs/observability/sdk/upgrade-path/python-v3-to-v4 [Tier 2 — Vendor docs]
- https://pypi.org/project/langfuse/ [Tier 2 — GitHub/package registry]
- https://github.com/langfuse/langfuse/releases [Tier 2 — GitHub]
- https://opentelemetry.io/docs/specs/semconv/gen-ai/ [Tier 1 — Independent standards (OpenTelemetry)]
- https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-events/ [Tier 1 — Independent standards (OpenTelemetry)]
- https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/ [Tier 1 — Independent standards (OpenTelemetry)]
- https://github.com/open-telemetry/semantic-conventions/releases [Tier 2 — GitHub (OpenTelemetry)]
- https://dev.to/x4nent/opentelemetry-genai-semantic-conventions-the-standard-for-llm-observability-1o2a [Tier 2 — Tech news]
