# LLM Production Infrastructure — Research Brief (2026-05-14)

## Key Developments

*Quiet week for independently verified developments in this topic. The most significant item (Red Hat AI 3.4 / llm-d) is substantiated by multiple independent technology outlets covering Red Hat Summit 2026.*

- **Red Hat productises llm-d disaggregated inference on any managed Kubernetes**
  - **What changed:** Red Hat AI 3.4 extends llm-d-powered distributed inference beyond OpenShift to CoreWeave CKS and AKS.
  - **Why it matters:** Enterprises can now procure a supported, Kubernetes-native disaggregated inference stack with documented production results.
  - *(Red Hat Summit blog / HPCwire / StorageNewsletter, May 12–13, 2026)*

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Red Hat AI 3.4 (llm-d on AKS + CoreWeave) | May 12–13, 2026 | [Red Hat Blog](https://www.redhat.com/en/blog/red-hat-ai-inference-brings-llm-d-any-managed-kubernetes-starting-coreweave-and-microsoft-azure) / [HPCwire](https://www.hpcwire.com/aiwire/2026/05/12/red-hat-learns-new-ai-tricks-at-summit-2026/) | Extends llm-d disaggregated inference, Model-as-a-Service, eval hub, and AgentOps tracing to CoreWeave CKS and AKS; validated 3x throughput and 2x TTFT improvement vs. round-robin in production (Red Hat/Tesla); eval hub uses MLflow + OCI model cards + MCP server for framework-agnostic evaluation |
| vLLM v0.20.2 | May 10, 2026 | [PyPI vllm](https://pypi.org/project/vllm/) / [GitHub](https://github.com/vllm-project/vllm/releases) | Patch release; continued DeepSeek V4 and Hopper/Blackwell stabilization; CUDA 13.0 / PyTorch 2.11 baseline maintained; CVE-2026-0994 protobuf patch included |
| vLLM v0.21.0 RC1 | May 12, 2026 | [GitHub releasealert.dev](https://releasealert.dev/github/vllm-project/vllm) | Release candidate; tagged May 12 — changelog not yet public at brief time |
| SGLang Model Gateway v0.3.0 | May 2026 | [SGLang GitHub releases](https://github.com/sgl-project/sglang/releases) | 6-layer metrics architecture; unified gateway for all router types (KV-cache-aware, prefix, OpenAI) with Kubernetes service discovery; UUID-based worker identification; WebAssembly programmable middleware; breaking change: Prometheus dashboard update required |
| SGLang v0.5.11 | May 5, 2026 | [PyPI sglang](https://pypi.org/project/sglang/) / [SGLang GitHub](https://github.com/sgl-project/sglang/releases/tag/v0.5.11) | CUDA 13 + PyTorch 2.11 default; Speculative Decoding V2 as default; Decode Radix Cache for P/D disaggregation; LoRA support for DeepSeek-V3 and Kimi-K2 MLA models; day-zero support for Gemma 4, GLM-5.1, Qwen3.6, Kimi-K2.6 |
| Cloudflare P/D-disaggregated LLM infrastructure blog | ~May 1, 2026 | [Cloudflare Blog](https://blog.cloudflare.com/high-performance-llms/) / [InfoQ](https://www.infoq.com/news/2026/05/cloudflare-llm-infrastructure/) | Documents Cloudflare's disaggregated prefill/decode stack running Kimi K2.5 on its Infire (Rust) inference engine; p90 inter-token latency dropped from ~100 ms to 20–30 ms; session-affinity caching raised cache-hit ratio from 60% to 80%; Mooncake cross-GPU KV cache sharing |
| Langfuse SDK v4.6.1 | May 8, 2026 | [PyPI langfuse](https://pypi.org/project/langfuse/) | Latest SDK release; self-hosted Observations v2 / Metrics v2 endpoints still unavailable per migration docs; OSS data schema migration path still in development as of brief date |
| Langfuse server eval API (unstable public endpoints) | May 2026 | [Langfuse GitHub releases](https://github.com/langfuse/langfuse/releases) | Active server iteration includes unstable public eval endpoints, experiment-triggered evals, and OTel/Datadog SDK upgrades; tool-call span filtering and prompt time-window metrics added |
| llm-d v0.5 production benchmark (B200) | Feb 2026, referenced May 2026 | [llm-d GitHub](https://github.com/llm-d/llm-d) / [Red Hat Summit](https://www.redhat.com/en/blog/inference-agentic-ai-scaling-enterprise-foundation-red-hat-ai-34) | v0.5 validated ~3,100 tokens/sec per B200 decode GPU and up to 50,000 output tokens/sec on 16×16 B200 P/D topology; order-of-magnitude TTFT reduction vs. round-robin; referenced extensively at Summit 2026 as production evidence |
| SkyWalker: Multi-Region Load Balancer (arXiv) | 2026 | [arXiv — candidate](https://openalex.org/W7155497146) | Proposes locality-aware cross-region LLM load balancing using diurnal traffic patterns to recover utilization from underused reserved instances; uses SLO-aware request splitting; unaffiliated preprint, unverified |

## Technical Deep-Dive

**Red Hat AI 3.4 and the llm-d enterprise commercialization: What shipped and what it means operationally**

The llm-d project (a CNCF Sandbox inference orchestration framework sitting above vLLM, donated to CNCF in March 2026) received its first enterprise-supported productization at Red Hat Summit 2026. 
At Red Hat Summit, Red Hat AI Inference expanded to run on any managed Kubernetes service, launching with validated deployment blueprints on CoreWeave Kubernetes Service (CKS) and Azure Kubernetes Service (AKS).
 
This release marks the transition from Red Hat AI Inference Server to Red Hat AI Inference, extending existing vLLM-based capabilities with llm-d-powered distributed inference orchestration.


The technical core of llm-d is inference-aware scheduling above the vLLM engine layer. 
llm-d's Endpoint Picker understands prefix cache locality — routing requests to pods that already have relevant KV cache entries — alongside model readiness, actual inference queue depth (not just TCP connections), and hardware topology.
 
The project addresses resource-utilization asymmetry between prompt processing and token generation by disaggregating these phases into independently scalable pods, and introduces hierarchical KV cache offloading across GPU, CPU, and storage tiers.
 This is architecturally distinct from NVIDIA Dynamo: 
llm-d uses standard Kubernetes networking, CRDs, and the Gateway API rather than NIXL for KV cache transfer and NVIDIA-specific hardware stacks — making it the natural path for teams managing existing Kubernetes clusters who want disaggregation without a separate proprietary control plane.


Production evidence cited at Summit 2026 is notable: 
teams using llm-d's intelligent routing have observed a 3x improvement in output throughput and a 2x reduction in time to first token compared to standard round-robin load balancing, with results documented by Red Hat and Tesla engineers serving Llama 3.1 70B at scale.
 The v0.5 benchmark on B200 hardware added further weight: 
the v0.5 release validated approximately 3,100 tokens per second per B200 decode GPU and up to 50,000 output tokens per second on a 16×16 B200 prefill/decode topology.


Red Hat AI 3.4 also ships an eval hub — a framework-agnostic evaluation control plane that deserves operational attention. 
The eval hub replaces fragmented testing with a unified REST API and Kubernetes controller offering curated and custom evaluation collections, a dashboard with embedded MLflow, and CLI/SDK access; it uses OCI model cards for governance and an MCP server for agent-discoverable evaluations, targeting reproducible benchmarking from laptops to production pipelines.
 The inclusion of an MCP server for agent-discoverable evaluations is architecturally notable: it positions evaluation metadata as a first-class agentic artifact rather than an out-of-band process. However, all these claims originate from Red Hat's own Summit materials — independent validation at production scale beyond the Red Hat/Tesla deployment reference is not yet available, and the CNCF Sandbox designation means the llm-d API surface will continue changing.

## Landscape Trends

- **[LLM Production Infrastructure × Agentic Systems]** The emergence of Red Hat AI 3.4's eval hub, Cloudflare's session-affinity KV caching for agentic traffic, and SGLang v0.5.11's decode-side radix caching for disaggregated deployments all point to a common pattern: serving and evaluation infrastructure is being redesigned around agentic workload shapes (long contexts, multi-turn sessions, shared prefixes). The operationally relevant shift is that prefix-cache hit rate — not pure token throughput — is increasingly the primary serving efficiency metric in production agentic deployments, a consequence first flagged in Cloudflare's production data showing cache-hit rate rising from 60% to 80% with session-affinity headers.

- **[LLM Production Infrastructure × Enterprise GenAI Adoption]** The llm-d productization by Red Hat and the Cloudflare public production blog both reinforce the pattern identified in prior briefs (April 10, April 24): disaggregated prefill/decode is crossing from research technique into commercial procurement option. The April 10 brief noted AKS + Dynamo benchmarks as the first independent production documentation; the May 13 brief adds a commercially supported open-source alternative (llm-d on AKS) with documented Tesla and Red Hat production evidence. The convergence of NVIDIA Dynamo (proprietary, optimized for DGX) and llm-d (CNCF, hardware-agnostic) as parallel commercially supported disaggregation stacks gives enterprise architects a genuine architectural choice for the first time.

- **The observability vendor consolidation pattern is accelerating.** Helicone (March 2026, acquired by Mintlify, now in maintenance mode) and TGI (December 2025, maintenance mode per prior briefs) represent the second and third category tools to exit active development within six months. 
Helicone's services will remain live in maintenance mode, with security updates, new models, and bug fixes continuing
, but feature development has ended. Combined with Cisco's acquisition of Galileo (April 9 brief) and Google's Gemini Enterprise Agent Platform absorbing evaluation capabilities (April 22 brief), the standalone LLM observability and evaluation tool market is consolidating faster than product-market fit has been independently validated.

- **[Prior brief callback — April 17 brief on Langfuse self-hosted gap]** The Langfuse v4 self-hosted migration gap, first flagged in the April 10 brief and re-noted in April 17, April 24, and May 8 briefs, remains unresolved at 10+ weeks post-Cloud-launch. 
The preview is currently available on Langfuse Cloud, and the team is working on the migration path for OSS deployments, sharing updates as they become available.
 Langfuse continues its rapid Cloud SDK iteration (v4.6.1 as of May 8), but the sustained absence of self-hosted Observations v2 / Metrics v2 means the gap is structurally persistent — not a temporary delay. Teams with data-residency constraints evaluating the v4 query performance improvements should continue treating this as a blocking dependency on their migration timeline.

- **[LLM Production Infrastructure × Safety, Assurance & Governance]** Red Hat AI 3.4's eval hub introduces OCI model cards and an MCP server for agent-discoverable evaluations — a pattern distinct from the standalone LLMOps eval tooling covered in prior briefs. This positions evaluation not as a workflow step but as infrastructure-layer metadata, queryable by agents and schedulers. If adopted, this would address a gap identified in the May 10 Safety brief: Anthropic's NLAs make model cognition readable, but there is no production-infrastructure mechanism for attaching evaluation results to deployed model artifacts at query time. Red Hat's eval hub is an early artifact pointing toward that capability — though it remains a vendor claim without independent adoption evidence at this stage.

## Vendor Landscape

- **Red Hat AI 3.4** (May 12, 2026): llm-d-powered distributed inference on CoreWeave CKS and AKS; Model-as-a-Service with governed model catalog; AgentOps with integrated tracing and cryptographic agent identity; eval hub with OCI model cards and MCP-discoverable evaluations. No-cost 60-day trial available. [Tier 2 — Vendor announcement]

- **Cloudflare Workers AI** (May 2026): Now serving Kimi K2.5 (1T+ parameter) via its proprietary Infire (Rust) inference engine with disaggregated prefill/decode; session-affinity KV caching; Mooncake cross-GPU KV transfer. P90 inter-token latency documented at 20–30 ms under production load. [Tier 2 — Vendor blog, independently covered by InfoQ]

- **SGLang Model Gateway v0.3.0** (May 2026): Full-fleet routing from a single gateway instance; 6-layer Prometheus metrics; WebAssembly plugin middleware; breaking change requiring dashboard updates. Production deployments running on 400,000+ GPUs worldwide claimed. [Tier 2 — GitHub, vendor claim]

- **Helicone** (maintenance mode, March 2026): Acquired by Mintlify; security and bug fixes only; 16,000+ organizations affected. Langfuse has published a migration guide. [Tier 2 — Vendor announcement]

- **Langfuse** (May 8, 2026): SDK v4.6.1 shipped; unstable public eval API endpoints added; self-hosted v4 data schema migration still pending after 10+ weeks. Active rapid Cloud iteration continues. [Tier 2 — PyPI / GitHub]

## Sources

- https://www.redhat.com/en/blog/red-hat-ai-inference-brings-llm-d-any-managed-kubernetes-starting-coreweave-and-microsoft-azure [Tier 2 — Vendor announcement]
- https://www.storagenewsletter.com/2026/05/13/red-hat-summit-2026-red-hat-unites-builders-and-operators-on-the-agentic-future-with-major-advancements-to-red-hat-ai/ [Tier 2 — Tech news]
- https://www.hpcwire.com/aiwire/2026/05/12/red-hat-learns-new-ai-tricks-at-summit-2026/ [Tier 1 — Independent journalism]
- https://www.redhat.com/en/blog/inference-agentic-ai-scaling-enterprise-foundation-red-hat-ai-34 [Tier 2 — Vendor announcement]
- https://wf.coreweave.com/blog/red-hat-ai-inference-on-cks-for-hybrid-inference [Tier 2 — Vendor announcement]
- https://ai2.work/blog/red-hat-puts-enterprise-ai-into-production-at-summit-in-atlanta [Tier 2 — Tech news]
- https://www.efficientlyconnected.com/red-hat-summit-2026-agentic-ai-governance-supply-chain-security/ [Tier 2 — Tech news]
- https://github.com/llm-d/llm-d [Tier 2 — GitHub]
- https://www.cncf.io/blog/2026/03/24/welcome-llm-d-to-the-cncf-evolving-kubernetes-into-sota-ai-infrastructure/ [Tier 1 — Independent (CNCF standards body blog)]
- https://cloud.google.com/blog/products/containers-kubernetes/llm-d-officially-a-cncf-sandbox-project [Tier 2 — Vendor announcement]
- https://blogs.oracle.com/ai-and-datascience/llm-inference-at-scale-with-llm-d-on-oci [Tier 2 — Vendor announcement]
- https://pypi.org/project/vllm/ [Tier 2 — GitHub/PyPI]
- https://github.com/vllm-project/vllm/releases [Tier 2 — GitHub]
- https://releasealert.dev/github/vllm-project/vllm [Tier 2 — Tech news]
- https://github.com/sgl-project/sglang/releases/tag/v0.5.11 [Tier 2 — GitHub]
- https://github.com/sgl-project/sglang/releases [Tier 2 — GitHub]
- https://pypi.org/project/sglang/ [Tier 2 — GitHub/PyPI]
- https://blog.cloudflare.com/high-performance-llms/ [Tier 2 — Vendor announcement]
- https://www.infoq.com/news/2026/05/cloudflare-llm-infrastructure/ [Tier 2 — Tech news]
- https://pypi.org/project/langfuse/ [Tier 2 — GitHub/PyPI]
- https://github.com/langfuse/langfuse/releases [Tier 2 — GitHub]
- https://langfuse.com/docs/v4 [Tier 2 — Vendor docs]
- https://github.com/orgs/langfuse/discussions/12518 [Tier 2 — GitHub]
- https://www.helicone.ai/blog/joining-mintlify [Tier 2 — Vendor announcement]
- https://www.mintlify.com/blog/mintlify-acquires-helicone [Tier 2 — Vendor announcement]
- https://github.com/sgl-project/sglang/issues/22949 [Tier 2 — GitHub]
