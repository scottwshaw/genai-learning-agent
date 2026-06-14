# Frontier Research — Research Brief (2026-03-16)

## Key Developments

- **GPT-5.4 released (Mar 5)**: OpenAI's first model with native computer-use capabilities, achieving 75.0% on OSWorld-Verified (surpassing 72.4% human baseline) and 83.0% on GDPVal with a 1M-token context window. ([OpenAI](https://openai.com/index/introducing-gpt-5-4/))
- **Gemini 3.1 Pro dominates benchmarks (Feb 19)**: Google DeepMind's latest flagship scores 77.1% on ARC-AGI-2 (2x+ over Gemini 3 Pro), leads 12 of 18 tracked benchmarks, and ships at the same price as its predecessor. ([Google Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/))
- **DeepSeek V4 imminent (~Mar 3–16)**: Trillion-parameter MoE model with Engram Conditional Memory architecture, tiered KV cache cutting memory 40%, and native multimodality (text/image/video/audio). Independent benchmarks pending. ([NxCode](https://www.nxcode.io/resources/news/deepseek-v4-release-specs-benchmarks-2026))
- **Llama 4 Scout & Maverick available**: Meta's open-source MoE models ship with an industry-leading 10M-token context window (Scout) and 1M tokens (Maverick), with 17B active parameters each. ([Meta AI Blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/))
- **OpenAI Codex Security launched (Mar 6)**: AI security agent that scanned 1.2M commits in beta, flagging 10,561 high-severity and 792 critical vulnerabilities with validated patch suggestions. ([OpenAI](https://openai.com/index/codex-security-now-in-research-preview/))

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| GPT-5.4 + GPT-5.4 Thinking | Mar 5 | OpenAI | First general-purpose model with native computer use; 1M context, 128K output; 75% OSWorld, 83% GDPVal |
| Gemini 3.1 Pro | Feb 19 | Google DeepMind | 77.1% ARC-AGI-2, 1M context / 65K output; #1 on 12/18 benchmarks at $2/$12 per M tokens |
| Gemini 3.1 Flash-Lite | Feb–Mar | Google DeepMind | 2.5× faster responses, 45% faster output gen, $0.25/M input tokens |
| Claude Opus 4.6 | Feb 5 | Anthropic | 75.6% SWE-bench, 1M context (beta), 128K output; memory features rolled out to all users in early March |
| Claude Sonnet 4.6 | Feb 17 | Anthropic | Improved coding capabilities, 1M context (beta) |
| DeepSeek V4 | ~Mar 3 | DeepSeek | 1T params MoE, 32B active; Engram memory, Sparse FP8 decoding (1.8× speedup), 1M context, native multimodal |
| Llama 4 Scout | Feb–Mar | Meta | 109B MoE / 17B active, 10M-token context, 95%+ retrieval accuracy to 8M tokens |
| Llama 4 Maverick | Feb–Mar | Meta | 400B MoE / 17B active, 128 experts, 1M context, natively multimodal |
| Mistral Large 3 | Feb–Mar | Mistral AI | 675B MoE, 92% of GPT-5.2 performance at ~15% of the cost |
| Ministral 3 | Feb–Mar | Mistral AI | Dense models at 3B/8B/14B params with base, instruct, and reasoning variants for edge deployment |
| Codex Security | Mar 6 | OpenAI | AI security agent: threat modeling → vulnerability detection → sandboxed validation → patch generation |
| AI in Nuclear Crisis Simulations | Feb | arXiv (2602.14740) | Study of GPT-5.2, Claude Sonnet 4, Gemini 3 Flash reasoning in simulated nuclear escalation scenarios |

## Technical Deep-Dive

### GPT-5.4: Native Computer Use at Superhuman Desktop Performance

The most technically significant release this cycle is OpenAI's GPT-5.4, which is the first general-purpose frontier model to ship with built-in computer-use capabilities — the ability to interact with software through screenshots, mouse movements, clicks, and keyboard inputs as a native modality rather than a bolted-on agent wrapper. On the OSWorld-Verified benchmark, which simulates real desktop productivity tasks across applications like browsers, file managers, and office suites, GPT-5.4 scores 75.0% — a massive jump from GPT-5.2's 47.3% and, critically, the first time any model has exceeded the human baseline of 72.4% on this benchmark.

The architecture integrates computer-use perception and action directly into the model's inference loop rather than routing through external tool-calling frameworks. This means the model reasons about screen state, plans multi-step UI interactions, and executes them in a unified forward pass. The 1.05M-token context window (922K input + 128K output) enables the model to maintain coherent state across long, complex workflows. On the GDPVal benchmark — which measures performance on economically valuable professional tasks — GPT-5.4 Thinking scores 83.0%, up from 70.9% for GPT-5.2, placing it at or above human-expert level. Hallucination rates are also significantly improved: 33% fewer false claims and 18% fewer error-containing responses versus GPT-5.2.

The competitive context matters: Gemini 3.1 Pro's 77.1% ARC-AGI-2 score represents superior abstract reasoning, while Claude Opus 4.6's 75.6% SWE-bench leads in real-world software engineering. GPT-5.4's differentiator is the computer-use modality — no other frontier model currently matches its ability to autonomously operate desktop software. The limitation is that OSWorld tasks are still constrained simulations; real-world desktop environments introduce far more variability, latency, and failure modes. Whether the 75% benchmark score translates to reliable production use remains to be validated.

## Implications & Trends

- **Benchmark convergence at the frontier**: GPT-5.4, Claude Opus 4.6, and Gemini 3.1 Pro now score within a few percentage points of each other across most evaluations, signaling that raw model intelligence is commoditizing while differentiation shifts to modalities (computer use, long context, multimodal) and ecosystem integration.
- **Context windows as a competitive axis**: The jump to 1M tokens is now table stakes (GPT-5.4, Claude 4.6, Gemini 3.1, Maverick), while Meta's Llama 4 Scout pushes to 10M tokens — suggesting that retrieval-augmented generation may give way to "just fit it in context" approaches for many enterprise use cases.
- **Open-source MoE parity closing fast**: Mistral Large 3 (675B MoE) at 92% of GPT-5.2 performance and Llama 4's 17B-active-parameter models demonstrate that the cost/performance gap between proprietary and open models continues to narrow, driven by mixture-of-experts efficiency gains.

## Sources

- [OpenAI — Introducing GPT-5.4](https://openai.com/index/introducing-gpt-5-4/)
- [TechCrunch — OpenAI launches GPT-5.4](https://techcrunch.com/2026/03/05/openai-launches-gpt-5-4-with-pro-and-thinking-versions/)
- [Google Blog — Gemini 3.1 Pro](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/)
- [VentureBeat — Gemini 3.1 Pro retaking AI crown](https://venturebeat.com/technology/google-launches-gemini-3-1-pro-retaking-ai-crown-with-2x-reasoning)
- [Google DeepMind — Gemini 3.1 Pro Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
- [Medium — Gemini 3.1 Pro ARC-AGI-2 Analysis](https://medium.com/@rogt.x1997/gemini-3-1-pro-scores-77-1-on-arc-agi-2-and-quietly-rewrites-enterprise-ai-9941ad1b2082)
- [Meta AI Blog — Llama 4](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
- [VentureBeat — Meta Llama 4 launch](https://venturebeat.com/ai/metas-answer-to-deepseek-is-here-llama-4-launches-with-long-context-scout-and-maverick-models-and-2t-parameter-behemoth-on-the-way)
- [NxCode — DeepSeek V4 specs & benchmarks](https://www.nxcode.io/resources/news/deepseek-v4-release-specs-benchmarks-2026)
- [DeepSeekV4.app — Complete Guide](https://deepseekv4.app/news/deepseek-v4-complete-guide)
- [OpenAI — Codex Security](https://openai.com/index/codex-security-now-in-research-preview/)
- [The Hacker News — Codex Security 1.2M commits scanned](https://thehackernews.com/2026/03/openai-codex-security-scanned-12.html)
- [eWeek — Mistral 3 Launch](https://www.eweek.com/news/mistral-3-launch/)
- [arXiv 2602.14740 — AI in Nuclear Crisis Simulations](https://arxiv.org/html/2602.14740v1)
- [Medium — Nobody Wins the AI Crown in March 2026](https://medium.com/ai-in-plain-english/nobody-wins-the-ai-crown-in-march-2026-not-even-gpt-5-4-b5db7043c762)
- [DeepLearning.ai — Gemini 3.1 Pro tops Intelligence Index](https://www.deeplearning.ai/the-batch/google-releases-gemini-3-1-pro-in-preview-tops-intelligence-index-at-same-price/)
- [BuildFastWithAI — GPT-5.4 Review](https://www.buildfastwithai.com/blogs/gpt-5-4-review-benchmarks-2026)
- [LLM-Stats — March 2026 AI Model Releases](https://llm-stats.com/llm-updates)
