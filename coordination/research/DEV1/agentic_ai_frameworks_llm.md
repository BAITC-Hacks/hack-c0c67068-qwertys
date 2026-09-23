# Agentic AI frameworks, LLM access without evaluators' keys, and prior art for agentic time-series / energy / weather forecasting (state as of 2026-09-23)

Method note: package versions, dates, licences, Python requirements, core-dependency lists and wheel sizes were pulled live from the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`) and GitHub REST API on 2026-09-23; each is cited to the package's PyPI page. "Core deps" = `requires_dist` entries without `extra ==` markers; "wheel" = size of the first wheel file for the latest version (a proxy for install size, NOT total footprint).

## 1. Agent frameworks in 2026: versions, maturity, licence, footprint, Windows, workflow-vs-agent, state, observability

### Takeaway
The field has consolidated: LangGraph (1.2.x, MIT, 6 core deps) is the lightest stable choice for an explicit stateful graph with SQLite checkpointing; Microsoft Agent Framework (1.x, MIT) has replaced AutoGen and Semantic Kernel (both now in maintenance mode); PydanticAI (2.x, MIT) is light and has built-in no-LLM test models. CrewAI, Google ADK and the Claude Agent SDK are heavy or tied to a provider. The Claude Agent SDK and OpenAI Agents SDK's default tracing assume vendor keys. Several older projects have been archived or renamed (ControlFlow, Burr, Hamilton).

### Cited Findings

**Snapshot table (PyPI, fetched 2026-09-23)**

| Framework | pip package | Latest (date) | Licence | Python | Core deps / wheel | Maturity signal |
|---|---|---|---|---|---|---|
| LangGraph | `langgraph` | 1.2.12 (2026-09-21) | MIT | >=3.10 | 6 (langchain-core, langgraph-checkpoint, langgraph-prebuilt, langgraph-sdk, pydantic, xxhash) / 244 KB | "Production/Stable" classifier — [PyPI](https://pypi.org/project/langgraph/) |
| LangChain | `langchain` | 1.4.2 (2026-09-18) | MIT | >=3.10,<4 | — | [PyPI](https://pypi.org/project/langchain/) |
| LangChain–Ollama | `langchain-ollama` | 1.1.0 (2026-04-07) | MIT | >=3.10 | — | [PyPI](https://pypi.org/project/langchain-ollama/) |
| LangGraph SQLite checkpointer | `langgraph-checkpoint-sqlite` | 3.1.1 (2026-07-30) | MIT | >=3.10 | — | [PyPI](https://pypi.org/project/langgraph-checkpoint-sqlite/) |
| CrewAI | `crewai` | 1.15.22 (2026-09-16) | licence field empty on PyPI | >=3.10,<3.14 | 31 (incl. chromadb, lancedb, tokenizers, pdfplumber, openpyxl, opentelemetry-sdk, instructor, mcp, openai) / 1.16 MB | [PyPI](https://pypi.org/project/crewai/) |
| Microsoft Agent Framework | `agent-framework` (meta) / `agent-framework-core` | 1.19.0 (2026-09-18) | MIT | >=3.10 | core: 6 (msgspec, pydantic, python-dotenv, opentelemetry-api, pyyaml, typing-extensions) / 746 KB | "Production/Stable" — [PyPI](https://pypi.org/project/agent-framework-core/) |
| Semantic Kernel (legacy) | `semantic-kernel` | 1.44.1 (2026-08-06) | — | >=3.10 | — | [PyPI](https://pypi.org/project/semantic-kernel/) |
| AutoGen (legacy) | `autogen-agentchat` | 0.7.5 (2025-09-30) — no release in ~12 months | MIT | >=3.10 | — | [PyPI](https://pypi.org/project/autogen-agentchat/) |
| AG2 | `ag2` | 1.0.6 (2026-09-21) | Apache-2.0 | >=3.10 | 5 / 1.07 MB | "Production/Stable" — [PyPI](https://pypi.org/project/ag2/) |
| OpenAI Agents SDK | `openai-agents` | 0.22.3 (2026-09-17) | MIT | >=3.10 | 12 (incl. openai, mcp, starlette, websockets) / 1.12 MB | pre-1.0 — [PyPI](https://pypi.org/project/openai-agents/) |
| Claude Agent SDK | `claude-agent-sdk` | 0.2.158 (2026-09-23) | MIT | >=3.10 | 5 (anyio, jsonschema, mcp, sniffio, typing-extensions) / **~88 MB wheel** | "Development Status :: 3 - Alpha" — [PyPI](https://pypi.org/project/claude-agent-sdk/) |
| smolagents | `smolagents` | 1.26.0 (2026-05-29) | — | >=3.10 | 6 (huggingface-hub, requests, rich, jinja2, pillow, python-dotenv) / 158 KB | [PyPI](https://pypi.org/project/smolagents/) |
| PydanticAI | `pydantic-ai` / `pydantic-ai-slim` | 2.48.0 (2026-09-23) | MIT | >=3.10 | slim: 9 (incl. pydantic-graph, opentelemetry-api, httpx2, genai-prices) / 1.8 MB | "Production/Stable" — [PyPI](https://pypi.org/project/pydantic-ai-slim/) |
| LlamaIndex Workflows | `llama-index-workflows` | 2.24.1 (2026-09-20) | MIT | >=3.10 | 3 / 165 KB; "event-driven, async-first, step-based" | [PyPI](https://pypi.org/project/llama-index-workflows/) |
| LlamaIndex core | `llama-index-core` | 0.14.25 (2026-09-21) | MIT | >=3.10,<4 | — | [PyPI](https://pypi.org/project/llama-index-core/) |
| Google ADK | `google-adk` | 2.9.2 (2026-09-18) | Apache-2.0 | >=3.10 | 23 (incl. fastapi, uvicorn, google-genai, google-auth, graphviz, opentelemetry-sdk, watchdog) / 4.5 MB | [PyPI](https://pypi.org/project/google-adk/) |
| Agno (ex-phidata) | `agno` | 3.0.10 (2026-09-16) | Apache-2.0 | >=3.9,<4 | 10 / 3.9 MB | "Production/Stable" — [PyPI](https://pypi.org/project/agno/) |
| DSPy | `dspy` | 3.3.1 (2026-08-21) | MIT | >=3.10,<3.15 | 14 (incl. litellm, openai, diskcache, gepa) / 411 KB | "Alpha" classifier — [PyPI](https://pypi.org/project/dspy/) |
| Haystack | `haystack-ai` | 3.1.1 (2026-09-03) | Apache-2.0 | >=3.10 | 18 (incl. numpy, networkx, openai, **posthog**) / 697 KB | "Production/Stable" — [PyPI](https://pypi.org/project/haystack-ai/) |
| Marvin | `marvin` | 3.2.7 (2026-03-04) | Apache-2.0 | >=3.10 | — | [PyPI](https://pypi.org/project/marvin/) |
| ControlFlow | `controlflow` | 0.12.1 (2025-02-06) — **archived** | — | >=3.9 | — | [PyPI](https://pypi.org/project/controlflow/) |
| Burr | `burr` → **`apache-burr`** | burr 0.42.0 says "moved to apache-burr"; apache-burr 0.43.0 (Beta) | Apache-2.0 | >=3.9 | — | [PyPI burr](https://pypi.org/project/burr/), [PyPI apache-burr](https://pypi.org/project/apache-burr/) |
| Hamilton | `sf-hamilton` → `apache-hamilton` | sf-hamilton 1.90.0 says "moved to apache-hamilton" | Apache-2.0 | — | — | [PyPI](https://pypi.org/project/sf-hamilton/) |
| Temporal | `temporalio` | 1.33.0 (2026-09-15) | MIT | >=3.10 | — | [PyPI](https://pypi.org/project/temporalio/) |
| Prefect | `prefect` | 3.8.6 (2026-09-15) | Apache-2.0 | >=3.10,<3.15 | — | [PyPI](https://pypi.org/project/prefect/) |
| Dagster | `dagster` | 1.13.24 (2026-09-21) | Apache-2.0 | >=3.10,<3.15 | — | [PyPI](https://pypi.org/project/dagster/) |
| LiteLLM (provider router) | `litellm` | 1.102.1 (2026-09-23) | MIT | >=3.10,<3.15 | 14 (incl. boto3, tiktoken, tokenizers, aiohttp) / **~26 MB wheel** | [PyPI](https://pypi.org/project/litellm/) |
| Instructor (structured output) | `instructor` | 1.17.0 (2026-09-09) | MIT | >=3.9,<4 | — | [PyPI](https://pypi.org/project/instructor/) |

**LangGraph (+LangChain)**
- Describes itself as "a low-level orchestration framework for building, managing, and deploying long-running, stateful agents" and lists durable execution, streaming, human-in-the-loop, persistence and memory as its core features — [PyPI langgraph](https://pypi.org/project/langgraph/)
- Persistence: checkpointers `InMemorySaver` (`langgraph.checkpoint.memory`), `SqliteSaver` (local file, dev), `PostgresSaver`/`AsyncPostgresSaver` (prod). State is saved per `thread_id` and supports human-in-the-loop, time travel (replay from a checkpoint) and fault tolerance. Usage: `graph = builder.compile(checkpointer=InMemorySaver()); graph.invoke({...}, {"configurable": {"thread_id": "thread-1"}})` — [LangGraph persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence)
- Official docs cover six patterns: prompt chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer, and agents. Each has examples in both the **Graph API** (nodes and edges) and the **Functional API** (decorated tasks). The examples page uses Anthropic models by default — [LangGraph workflows & agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

**Microsoft Agent Framework (MAF) — successor to AutoGen and Semantic Kernel**
- Python install: `pip install agent-framework`. Four areas: Agents (tools, MCP servers; providers "Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and more"), Harness Agent (planning/todo tracking, context compaction, memory, tool approval, observability), Workflows ("Functional and graph-based workflows… explicit execution paths"), and Integrations. It does **not** auto-load `.env` files; call `load_dotenv()` yourself — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- Microsoft's own rule of thumb: use an agent for open-ended tasks that need "autonomous tool use and planning", and a workflow when the "process has well-defined steps". Also: "If you can write a function to handle the task, do that instead of using an AI agent." — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)
- Timeline: public preview Oct 2025 → Release Candidate 19 Feb 2026 → 1.0 on 3 Apr 2026 with stable APIs and LTS. AutoGen went into maintenance mode in Oct 2025; Semantic Kernel followed at MAF 1.0 — [Atlan (secondary)](https://atlan.com/know/ai-agent/microsoft/agent-framework/); for the RC see [MS DevBlogs migration post](https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/)
- AutoGen README: "AutoGen is now in maintenance mode. It will not receive new features or enhancements and is community managed going forward… New users should start with Microsoft Agent Framework." — [github.com/microsoft/autogen](https://github.com/microsoft/autogen). The repo is not archived; last push 2026-04-15 (GitHub API).
- A Go SDK exists (public preview) — [Microsoft Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/)

**CrewAI**
- Ollama through LiteLLM: `LLM(model="ollama/<model>", base_url="http://localhost:11434")`, installed with `crewai[litellm]`. The docs recommend **Flows** for "deterministic, predictable workflows" and **Crews** for autonomous agents — [CrewAI LLM docs](https://docs.crewai.com/en/concepts/llms)
- Requires Python <3.14, and its core install pulls in vector DBs (chromadb, lancedb) and tokenizers — [PyPI crewai](https://pypi.org/project/crewai/)

**OpenAI Agents SDK**
- Non-OpenAI models: pass `AsyncOpenAI(base_url="http://localhost:11434/v1", api_key=...)` to `OpenAIChatCompletionsModel`, or install `openai-agents[litellm]` and use `LitellmModel`. **Tracing uploads to OpenAI by default**; without an OpenAI key, call `set_tracing_disabled(True)` or plug in a custom trace processor. Caveats: many providers lack the Responses API (use `set_default_openai_api("chat_completions")`), some lack structured outputs, and tool-call streaming may need `buffer_streamed_tool_calls=True` — [OpenAI Agents SDK models docs](https://openai.github.io/openai-agents-python/models/)

**Claude Agent SDK (Python)**
- "A library that runs the Claude Code binary" and provides its built-in tools, hooks, subagents, MCP, permissions and sessions. It needs **API-key authentication**. The docs also state: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products." Use is governed by Anthropic Commercial Terms — [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- The wheel is ~88 MB (the bundled CLI binary) and the package is classified Alpha — [PyPI](https://pypi.org/project/claude-agent-sdk/)

**Hugging Face smolagents**
- `CodeAgent` writes its actions as Python code, while `ToolCallingAgent` uses JSON tool calls. Sandboxed code execution is available via Modal, Blaxel, E2B or Docker. It is model-agnostic: HF Inference Providers, LiteLLM (`smolagents[litellm]`), local Transformers (`smolagents[transformers]`) or Ollama. It can load tools from MCP servers and LangChain. The core is "~thousand lines of code" — [smolagents docs](https://huggingface.co/docs/smolagents/index)

**PydanticAI**
- `TestModel` runs an agent with no LLM. It "calls all tools" and generates schema-valid arguments, which "is just plain old procedural Python code". `FunctionModel(fn)` swaps the LLM for your own function that decides which tools to call. `models.ALLOW_MODEL_REQUESTS = False` blocks real API calls, and `capture_run_messages()` lets you inspect them. Use via `agent.override(model=TestModel())` — [PydanticAI testing guide](https://pydantic.dev/docs/ai/guides/testing/)
- It depends on `pydantic-graph` (graph/state machine) and `opentelemetry-api` — [PyPI](https://pypi.org/project/pydantic-ai-slim/)

**Google ADK**
- Local models via model connectors (Ollama, vLLM, LiteRT-LM) and the LiteLLM wrapper. It has built-in workflow agents: Sequential, Loop, Parallel and custom. The docs mention a separate "tool limitations" page for local models. Docs moved to adk.dev — [ADK models docs](https://adk.dev/agents/models/)

**MCP (Model Context Protocol)**
- The current spec version is **2026-07-28**. Every request declares its version in `_meta` or the `MCP-Protocol-Version` header, and a new mandatory `server/discover` RPC exists. Handshake-based revisions are **2025-11-25 and earlier** (backward-compat section) — [MCP versioning](https://modelcontextprotocol.io/specification/versioning)
- The official Python SDK is `mcp` 2.2.0 (2026-09-07, MIT, Production/Stable; deps include uvicorn, starlette, sse-starlette, and pywin32 on Windows) — [PyPI mcp](https://pypi.org/project/mcp/)
- FastMCP 4.0.5 (2026-09-17, Apache-2.0; `fastmcp` → `fastmcp-slim`). It is a standalone framework that "created the high-level Python API incorporated into the official MCP Python SDK in 2024". Define tools with `@mcp.tool` on a typed function with a docstring and run with `mcp.run()`; the client is `async with Client(url) as c: await c.call_tool(...)` — [FastMCP docs](https://gofastmcp.com/getting-started/welcome), [PyPI](https://pypi.org/project/fastmcp/)
- Ready-made Open-Meteo MCP servers (no API key needed): [cmer81/open-meteo-mcp](https://github.com/cmer81/open-meteo-mcp), [gbrigandi/mcp-server-openmeteo](https://mcpservers.org/servers/gbrigandi/mcp-server-openmeteo), [JeremyMorgan/Weather-MCP-Server](https://github.com/jeremymorgan/weather-mcp-server)

**A2A (Agent2Agent)**
- A Linux Foundation open-source project contributed by Google. A2A covers agent-to-agent collaboration and complements MCP, which covers agent-to-tool integration. Python SDK: `pip install a2a-sdk` — [github.com/a2aproject/A2A](https://github.com/a2aproject/A2A); `a2a-sdk` 1.1.5 (2026-09-21, Apache-2.0) — [PyPI](https://pypi.org/project/a2a-sdk/)

**Deprecated / moved (flag)**
- ControlFlow was archived on 2026-03-19. README: "next-generation ControlFlow engine was merged into the Marvin agentic framework, and this repo has been archived." — [github.com/PrefectHQ/ControlFlow](https://github.com/PrefectHQ/ControlFlow)
- AutoGen is in maintenance mode (see above). Semantic Kernel is in maintenance mode after MAF 1.0 — [Atlan (secondary)](https://atlan.com/know/ai-agent/microsoft/semantic-kernel/)
- `burr` → `apache-burr` and `sf-hamilton` → `apache-hamilton`, per the PyPI summaries — [PyPI burr](https://pypi.org/project/burr/), [PyPI sf-hamilton](https://pypi.org/project/sf-hamilton/)

### Inferences
- For a ~4 h Windows/Python 3.12 build, the lowest-risk stacks are: (a) LangGraph + `langgraph-checkpoint-sqlite` (explicit graph, SQLite state, replay/time-travel built in, 6 core deps), or (b) PydanticAI (light, typed tools, `FunctionModel`/`TestModel` for a no-LLM mode), or (c) plain Python plus the `ollama` client's function-calling loop. MAF is mature but its examples are Azure/Foundry-centric. CrewAI and Google ADK pull in heavy dependencies (vector DBs, FastAPI/Google auth). The Claude Agent SDK and OpenAI Agents SDK default to vendor keys or tracing, which clashes with the "no personal accounts" rule.
- Everything in the table is pure Python with a >=3.10 requirement, so Python 3.12 on Windows should work. The main Windows risk is native dependencies (chromadb/lancedb/tokenizers in CrewAI, llama-cpp-python compilation). This was not tested.
- Learning curve (subjective): plain function-calling loop < PydanticAI ≈ smolagents < LangGraph < MAF ≈ CrewAI < ADK/Temporal. Temporal also needs a server process, which is overkill for a hackathon.
- MCP adds credibility (tools like "fetch weather" and "run model" exposed as MCP) but also an extra process. FastMCP in stdio mode keeps it single-machine and key-less.

### Gaps
- No measured on-disk install size per framework (only wheel sizes and dependency lists). A `pip install` into a clean venv would give real numbers.
- Licence fields are empty on PyPI for CrewAI, smolagents, Google ADK (ADK shows an Apache classifier), MAF (MIT classifier) and Semantic Kernel. Repo LICENSE files were not checked.
- AG2's lineage (community continuation of AutoGen 0.2) was not re-verified this session. PyPI only confirms `ag2` 1.0.6, Apache-2.0, Production/Stable.
- No independent 2026 comparison of the frameworks was fetched. The blog posts found were aggregator-quality.

## 2. LLM access that works WITHOUT evaluators' personal accounts/keys

### Takeaway
The only options that need no account at all are local models: Ollama (Windows installer, no admin, OpenAI-compatible `localhost:11434/v1`), LM Studio or llama.cpp. The practical sweet spot on a CPU laptop with 8–16 GB is Qwen3 4B/8B (2.5 GB/5.2 GB). Every hosted "free tier" still needs a personal account and token, and their daily caps are small (e.g., OpenRouter `:free` models 50 requests/day). GitHub Models was retired on 2026-07-30. The robust setup is therefore: an LLM that is optional, configured by environment variables, plus a deterministic rule-based fallback.

### Cited Findings

**Ollama (local, key-less)**
- Latest releases: v0.34.3 (2026-09-19), v0.34.4-rc0 (2026-09-23) — [GitHub releases API](https://github.com/ollama/ollama/releases)
- Windows: `OllamaSetup.exe`; needs "Windows 10 22H2 or newer"; **no admin rights** (installs to the user's home); ≥4 GB for the binaries plus model space; `OLLAMA_MODELS` relocates model storage; API at `http://localhost:11434` — [Ollama Windows docs](https://docs.ollama.com/windows)
- OpenAI compatibility: `base_url='http://localhost:11434/v1/'`, `api_key='ollama'` (required but ignored). `/v1/chat/completions` supports streaming, JSON mode, reproducible outputs and tools, and `/v1/responses` supports function calling. No logprobs — [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)
- Tool calling: pass a `tools` array, or, with the Python SDK, "directly pass the function" (docstrings are parsed into a schema). Parallel tool calls and streaming are supported, and the docs show an agent loop that runs until no more `tool_calls` come back. All examples use `qwen3` — [Ollama tool-calling docs](https://docs.ollama.com/capabilities/tool-calling). Python client: `ollama` 0.6.2 (MIT, deps: httpx, pydantic) — [PyPI](https://pypi.org/project/ollama/)
- Qwen3 tags: `qwen3:0.6b` 523 MB, `1.7b` 1.4 GB, `4b` 2.5 GB (256K ctx), `8b` 5.2 GB (40K), `14b` 9.3 GB, `30b` 19 GB — [ollama.com/library/qwen3](https://ollama.com/library/qwen3)
- Qwen3.5 tags (text+image): `0.8b` 1.0 GB, `2b` 2.7 GB, `4b` 3.4 GB, `9b` 6.6 GB, `27b` 17 GB, `35b` 24 GB; 256K context — [ollama.com/library/qwen3.5](https://ollama.com/library/qwen3.5)
- Small models tagged with the "tools" capability in the library include `granite4.1` (3b, 8b, 30b) and `ornith` (9b). The popular tools list is dominated by 27B+ and cloud models (qwen3.6/3.8 27–35B, glm-5.x, deepseek-v4, kimi-k2.x) — [ollama.com/search?c=tools](https://ollama.com/search?c=tools&o=popular)
- Tool-calling accuracy (Docker evaluation, 2025-06-30; 21 models, 3,570 test cases; MacBook M4 Max 128 GB):

  | Model | F1 |
  |---|---|
  | Qwen3 14B Q4_K_M | 0.971 (~142 s latency) |
  | Qwen3 8B F16 | 0.933 (~84 s) |
  | Qwen3 8B Q4_K_M | 0.919 |
  | Llama3.1 8B F16 | 0.835 |
  | Llama3.1 8B Q4_K_M | 0.793 |
  | Qwen2.5 7B Q4_K_M | 0.753 |
  | Gemma3 4B | 0.733 |
  | Llama3.2 3B | 0.727 |

  Quantization made "no significant difference" to tool-calling accuracy — [Docker blog](https://www.docker.com/blog/local-llm-tool-calling-a-practical-evaluation/)
- A 2026 guide (updated 2026-07-15) names Qwen 3.5 9B as the current 8 GB-tier pick for function calling. Failure modes it lists: eager or unnecessary tool calls, hallucinated function names, "bad-state" loops that repeat failed calls, and a Qwen 3.6 template issue that silently rejects JSON with unusual spacing — [InsiderLLM](https://insiderllm.com/guides/function-calling-local-llms/)
- CPU-only speed (secondary sources, unverified): Qwen3 8B Q4_K_M ≈ 8–15 tok/s on a 16 GB machine with no GPU; Qwen3 4B ≈ 16.5 tok/s on an Intel Core Ultra 5 125H — [PromptQuorum](https://www.promptquorum.com/local-llms/fastest-local-llms-low-end-pcs), [Markaicode](https://markaicode.com/benchmarks/tool-cpu-benchmark/)

**Other local runtimes**
- llama.cpp: latest build b11122 (2026-09-23) — [GitHub](https://github.com/ggml-org/llama.cpp/releases)
- `llama-cpp-python` 0.3.35 (2026-08-17, MIT) — [PyPI](https://pypi.org/project/llama-cpp-python/). Features: prebuilt CPU wheels for Windows from a custom index (otherwise a compiler is needed), an OpenAI-compatible server, JSON-schema-constrained output, and function calling via the `functionary` / `chatml-function-calling` chat formats — [GitHub README](https://github.com/abetlen/llama-cpp-python)
- LM Studio: OpenAI-compatible server (`lms server start --port 1234`), a `lms` CLI, and the `llmster` headless daemon for servers and CI. Windows installs through PowerShell `irm`. Supports tool calling and MCP — [LM Studio developer docs](https://lmstudio.ai/docs/developer)
- smolagents `TransformersModel` runs HF models in-process — [smolagents docs](https://huggingface.co/docs/smolagents/index)

**Hosted free tiers (all require the user's own account/token)**
- **Google Gemini**: the official rate-limit page no longer lists numbers. It says limits "can be viewed in Google AI Studio" and are "not guaranteed" — [ai.google.dev rate limits](https://ai.google.dev/gemini-api/docs/rate-limits). Secondary sources give ~5–15 RPM and 100–1,000 RPD by model, and say Pro models left the free tier in April 2026 — [TinkerLLM](https://tinkerllm.com/blog/gemini-api-free-tier-limits-rate-quotas/), [PE Collective](https://pecollective.com/tools/gemini-free-tier-guide/). Terms for Unpaid Services: content is used to "provide, improve, and develop Google products", human reviewers may read it, users must be 18+, and API clients serving EEA/Switzerland/UK users must use Paid Services only — [Gemini API terms](https://ai.google.dev/gemini-api/terms)
- **Groq** free plan:
  - `openai/gpt-oss-120b`, `openai/gpt-oss-20b` and `qwen/qwen3.8-27b`: 30 RPM, 1K RPD, 8K TPM, 200K TPD — [Groq rate limits](https://console.groq.com/docs/rate-limits)
  - "All models hosted on Groq support tool use". Parallel tool calls work on Qwen/MiniMax/Llama but not on the gpt-oss models — [Groq tool use](https://console.groq.com/docs/tool-use/overview)
  - Discrepancy: the tool-use page lists `llama-3.3-70b-versatile` and `llama-3.1-8b-instant`, but the free-plan rate-limit table (fetched the same day) does not.
- **OpenRouter** `:free` models: 20 RPM and **50 requests/day** without purchased credits; 1,000/day after buying ≥$10 of credits — [OpenRouter limits](https://openrouter.ai/docs/api-reference/limits)
- **Cerebras** free trial: `gpt-oss-120b`, `qwen-3.8-27b`; 5 RPM, 30K uncached TPM, 1M tokens/day. The $5 of free credits require "adding a verified payment method" and expire after 30 days — [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits)
- **GitHub Models**: "As of July 30, 2026, GitHub Models has been fully retired" (playground, catalog, inference API and BYOK) — [GitHub Docs](https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models)
- **Hugging Face Inference Providers**: free users get **$0.10/month** in credits (PRO $2.00). OpenAI-compatible router at `https://router.huggingface.co/v1` with an `HF_TOKEN` — [HF pricing docs](https://huggingface.co/docs/inference-providers/pricing)
- **Mistral**: a free "Experiment" plan exists — [Mistral Help Center](https://help.mistral.ai/en/articles/455206-how-can-i-try-the-api-for-free-with-the-experiment-plan). Exact limits are no longer published (check the Admin Console). Secondary sources cite ~1 req/s and ~1B tokens/month — [yangmao.ai](https://yangmao.ai/en/deals/mistral-la-plateforme-free-tier/), [CostBench](https://costbench.com/software/llm-api-providers/mistral-ai/free-plan/)
- **LiteLLM** (`litellm` 1.102.1) is a single client for all of the above, including `ollama/…` model strings. It is what CrewAI, DSPy and the OpenAI Agents SDK extras use under the hood — [PyPI](https://pypi.org/project/litellm/), [CrewAI docs](https://docs.crewai.com/en/concepts/llms)

### Inferences
- **The demo key in the README is risky and weak.** Shared free keys have tiny daily caps (OpenRouter 50 RPD is shared by every evaluator plus anyone who scrapes the repo). Gemini's free tier is legally barred for EEA/UK/CH-facing clients and uses the data for training. Cerebras needs a card. GitHub Models no longer exists. A key committed to a public repo can be revoked or exhausted at any time.
- Recommended configuration pattern (inference, not verified by any single source):
  - `LLM_PROVIDER=none|ollama|openai_compat` plus `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` in `.env` (ship `.env.example`, git-ignore `.env`, and call `load_dotenv()` explicitly — MAF notes it does not auto-load).
  - Default `none` gives a rule-based "agent" that makes the same decisions from thresholds and templated explanations.
  - `ollama` with `qwen3:4b` or `qwen3:8b` enables LLM reasoning and reports.
  - Any OpenAI-compatible endpoint then works through one `openai` client, because Ollama, LM Studio, llama-cpp-python, Groq, OpenRouter and HF all expose `/v1/chat/completions`.
- On a CPU laptop, ~8–16 tok/s means a 300-token analysis takes ~20–40 s. Replaying 28 February days with the LLM on every day could take 10–20+ minutes. Consider caching LLM outputs, or running the LLM only on anomalies or the final summary.
- Qwen3 models "think" by default. For speed, a no-think setting or small `num_predict` values may be needed; the exact Ollama flag was not verified this session.

### Gaps
- No primary Google table of current Gemini free-tier numbers (moved into the AI Studio UI); only secondary sources.
- No primary CPU-only benchmark for Qwen3 4B/8B on a typical Windows laptop; figures come from aggregator sites.
- vLLM's Windows status was not fetched this session. It is generally Linux/GPU-oriented; verify before relying on it.
- LM Studio's licence terms for work/commercial use were not found on the developer page.
- The exact Ollama parameter to disable Qwen3 thinking (e.g., `think=False`) was not confirmed in the docs fetched.

## 3. Prior art: LLM agents for time-series, energy and weather forecasting

### Takeaway
2025–2026 literature converges on one view. LLM agents rarely produce the numeric forecast themselves. They act as planner, curator and critic around proper forecasting models (statistical, ML, time-series foundation models), and add data diagnostics, model selection, reflection/memory and natural-language reports. Energy-domain reviews explicitly position LLM agents for explanation, uncertainty communication and operator guidance, and flag hallucination/physics-grounding as open problems.

### Cited Findings

**Agentic time-series forecasting (general)**
- **Position: Agentic Time Series Forecasting** (Cheng, Tao, Liu, Guo, Chen; arXiv 2602.01776, Feb 2026, revised Mar 2026). Reframes forecasting from a static single pass into an agentic process with perception, planning, action, reflection and memory. Three paradigms: workflow-based, agentic RL, and hybrid agentic workflow. Forecasting should be "an agentic workflow that can interact with tools, incorporate feedback" — [arXiv](https://arxiv.org/abs/2602.01776)
- **TimeSeriesScientist** (Zhao et al., arXiv 2510.01538, Oct 2025). Four agents:
  - Curator: LLM-guided diagnostics plus tools to choose preprocessing
  - Planner: narrows model hypotheses
  - Forecaster: fitting, validation, adaptive ensembles
  - Reporter: transparent reports

  Across 8 benchmarks it reduces error by 10.4% on average vs statistical baselines and by 38.2% vs LLM-based baselines — [arXiv](https://arxiv.org/abs/2510.01538)
- **TimeCopilot** (arXiv 2509.00616; `pip install timecopilot`; MIT). An open-source forecasting agent that combines LLMs with 30+ models: Chronos, Moirai, TimesFM, TimeGPT, AutoARIMA, AutoETS, Theta, SeasonalNaive. Built on **Pydantic AI**; default LLM is OpenAI gpt-4o-mini, and any Pydantic-AI-supported endpoint with tool use works. CLI example: `uvx timecopilot forecast <csv>`. README claims #1 on GIFT-Eval; ~613 stars — [GitHub](https://github.com/TimeCopilot/timecopilot)
- **TimeSeriesGym** (arXiv 2505.13291; NeurIPS 2025). A benchmark for ML-engineering agents: 34 challenges, 8 problem types, 15+ domains, with integrations for AIDE, MLAgentBench and OpenHands. Finding: even SOTA agents struggle — [arXiv](https://arxiv.org/abs/2505.13291), [GitHub](https://github.com/moment-timeseries-foundation-model/TimeSeriesGym)
- **DCATS: Empowering Time Series Forecasting with LLM-Agents** (arXiv 2508.04231). A data-centric agent that uses time-series metadata to clean data while optimizing forecast accuracy (LLM agents as AutoML planners) — [arXiv](https://arxiv.org/abs/2508.04231)
- **Cast-R1** (arXiv 2602.13802). Tool-augmented sequential decision policies for forecasting — [arXiv PDF](https://arxiv.org/pdf/2602.13802)
- **TemporalBench** (arXiv 2602.13272). Benchmark for LLM agents on contextual and event-informed time-series tasks — [arXiv PDF](https://arxiv.org/pdf/2602.13272)
- **Nexus** (Das et al., arXiv 2605.14389, May 2026). Multi-agent: separates macro- and micro-level fluctuations, integrates context, then synthesizes. Combines time-series foundation models with LLM reasoning, produces interpretable reasoning traces, and matches or beats SOTA TSFMs on post-cutoff data — [arXiv](https://arxiv.org/abs/2605.14389)
- **Bridging the Last Mile of TS Forecasting with LLM Agents** (Liao et al., arXiv 2606.02497, Jun 2026). The agent keeps a unified forecast workspace and uses tools to retrieve context. It turns its reasoning into explicit forecast revisions **with structural safety constraints**, uses map-reduce decomposition for long horizons, and runs post-hoc reflection through a memory bank. Designed to be "controllable and auditable" — [arXiv](https://arxiv.org/abs/2606.02497)

**Energy / grid / weather**
- **Bridging AI and Energy Forecasting: An Autonomous Workflow with Customized Toolkit** (Wang et al., arXiv 2307.07191; revised Jul 2026). The LLM agent acts as a "virtual analyst": it analyses data characteristics, assembles the best forecasting pipeline and writes reports. Toolkit: 31 temporal architectures + 6 exogenous (meteorological) modules = 146 variants, benchmarked on 21 energy datasets including renewables with weather data — [arXiv](https://arxiv.org/abs/2307.07191)
- **LLM-Agent-Based Renewable Energy Forecasting Using Edge and IoT Data: A Review** (Manjunath & Pruefer, arXiv 2605.25141, May 2026). Six-layer taxonomy: acquisition → preprocessing → feature engineering → model inference → uncertainty estimation → natural-language reporting. LLM agents serve explanation, uncertainty communication and operator guidance rather than replacing numeric forecasting. Lists 12 open challenges, including drift, hallucination control and physics grounding — [arXiv](https://arxiv.org/abs/2605.25141)
- **LLMs and Agentic AI Systems for Smart Grids: A Tutorial** (arXiv 2607.18147). Covers typed tool interfaces, short- and long-term memory, orchestration frameworks, and tool-injection/governance risks. Wind power forecasting is one of four case studies: an LLM agent helps generate scenario trees for wind-forecast uncertainty (adjusting quantiles, interpreting error distributions) — [arXiv HTML](https://arxiv.org/html/2607.18147), with the case-study summary from search snippets
- Other energy-agent work:
  - **Grid-Mind** (arXiv 2602.20683): LLM-orchestrated connection-impact assessment — [arXiv PDF](https://arxiv.org/pdf/2602.20683)
  - **Power Systems Agent Benchmark** (arXiv 2606.20950) — [arXiv PDF](https://arxiv.org/pdf/2606.20950)
  - **Tool-augmented LLM agents on energy analytics** (arXiv 2606.26346): 243 expert-curated energy-market problems; not forecasting-focused — [arXiv](https://arxiv.org/abs/2606.26346)
  - **Can LLM Agents Balance Energy Systems?** (arXiv 2502.10557) — [arXiv HTML](https://arxiv.org/html/2502.10557v1)
  - **AgentCaster: Reasoning-Guided Tornado Forecasting** (arXiv 2510.03349) — [arXiv PDF](https://arxiv.org/pdf/2510.03349)
- **Open-Meteo Previous Runs API**: returns forecasts as issued 1–7 days before the valid time (`*_previous_day1..7`). Wind is available at 10/80/100/120/180/200 m, from 40+ models (ECMWF, GFS, ICON, ARPEGE, UKMO, JMA…). Most models are archived from **January 2024**. Endpoint: `previous-runs-api.open-meteo.com/v1/forecast` — [Open-Meteo docs](https://open-meteo.com/en/docs/previous-runs-api)

**Data-science agents (pipeline-automation prior art)**
- **DS-Agent** (arXiv 2402.17453): case-based reasoning, reusing solution patterns from human insights — [arXiv](https://arxiv.org/html/2402.17453v5)
- **Data Interpreter** (arXiv 2402.18679; ACL Findings 2025): dynamic planning with hierarchical graph structures, tool integration and incremental validation — [arXiv](https://arxiv.org/abs/2402.18679), [ACL Anthology](https://aclanthology.org/2025.findings-acl.1016.pdf)
- **AutoKaggle** (arXiv 2410.20424, Oct 2024): 6 phases; Reader/Planner/Developer/Reviewer/Summarizer agents; iterative debugging plus unit tests; validation submission rate 0.85, comprehensive score 0.82 on 8 Kaggle competitions — [arXiv](https://arxiv.org/abs/2410.20424)
- **DS-Lighting** (arXiv 2608.28590): bundles AutoKaggle, Data Interpreter and DS-Agent into one toolkit and makes agent harnesses explicit — [arXiv](https://arxiv.org/html/2608.28590)
- **ForecastBench** (arXiv 2409.19839; Forecasting Research Institute) is **not** a time-series benchmark. It covers judgmental forecasting of future events (1,000 auto-generated questions from Manifold, Metaculus, Polymarket, FRED, ACLED…). Expert forecasters still beat the best LLM (p<0.001). Low relevance to wind-power forecasting — [arXiv](https://arxiv.org/html/2409.19839v5), [FRI](https://forecastingresearch.org/research/forecastbench-a-dynamic-benchmark-of-ai-forecasting-capabilities)
- **Nixtla TimeGPT** is a time-series foundation model, not an LLM ("not based on any existing large language model"). Its SDK `nixtla` 0.9.0 needs an API key — [GitHub Nixtla/nixtla](https://github.com/Nixtla/nixtla), [PyPI](https://pypi.org/project/nixtla/). Nixtla's key-less open-source `statsforecast` is at 2.1.1 — [PyPI](https://pypi.org/project/statsforecast/)

### Inferences
- The consistent architecture in the literature gives a defensible "agentic" story for a wind case:
  - curator/diagnostics (data quality, gaps, turbine curtailment anomalies, weather forecast freshness)
  - planner/model selection
  - forecaster (a conventional ML model as a tool)
  - critic/reflection (compares against baselines or recent errors, triggers recompute)
  - reporter (NL explanation of drivers and uncertainty)

  TimeSeriesScientist, TimeCopilot and the 2307.07191 energy workflow all follow this pattern. This is a synthesis, not a prescription.
- The energy reviews' stance (LLM for explanation, not numeric prediction) supports keeping the numeric model deterministic and reproducible. The LLM layer's value is decisions and explanations. This also makes a no-LLM fallback natural.
- The Open-Meteo Previous Runs archive (from Jan 2024) covers Feb 2026, so as-of weather inputs for daily historical replay may be obtainable without keys. Confirm variable and model availability for the specific site.

### Gaps
- No public GitHub repo was found of an **agentic wind-power forecasting pipeline** (LLM + weather API + model + re-run). Prior art is mostly papers.
- No code links surfaced for TimeSeriesScientist, Nexus or Last-Mile in the arXiv abstracts fetched.
- No "TS-Agent" paper under that exact name was verified this session.
- Quantitative results for the energy-agent papers (2607.18147 wind case, 2606.26346) were not extracted beyond the abstracts.

## 4. Agentic patterns, event-driven re-runs, deterministic replay, observability — and what counts as "real" agentic behaviour

### Takeaway
Canonical definitions (Anthropic; Microsoft) separate **workflows** (predefined code paths) from **agents** (the LLM directs its own tool use). Both vendors advise using the simplest thing that works. A convincing "agentic" demo typically shows: tool use with the LLM choosing tools, planning, a self-evaluation/reflection loop, reacting to new data (re-run on update), anomaly handling, and persisted, human-readable decision logs. Deterministic replay is easiest with a checkpointed graph plus cached LLM outputs, and observability can be fully local (JSON logs/OpenTelemetry) without LangSmith keys.

### Cited Findings
- Definitions:
  - Workflows are "Systems where LLMs and tools are orchestrated through predefined code paths"
  - Agents are "Systems where LLMs dynamically direct their own processes and tool usage"

  Patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer. Agents suit open-ended problems where the number of steps can't be predicted. Advice: start with direct LLM API calls, since "many patterns can be implemented in a few lines of code" — [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- Microsoft: use a workflow when "the process has well-defined steps"/"explicit control over execution order" is needed, and an agent for "autonomous tool use and planning". MAF workflows support long-running and human-in-the-loop scenarios with state management — [Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/overview/)
- Framework-native deterministic modes:
  - CrewAI **Flows** vs Crews — [CrewAI docs](https://docs.crewai.com/en/concepts/llms)
  - ADK Sequential/Loop/Parallel workflow agents — [ADK docs](https://adk.dev/agents/models/)
  - LangGraph Graph/Functional APIs with evaluator-optimizer loops — [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
  - LlamaIndex event-driven step workflows — [PyPI](https://pypi.org/project/llama-index-workflows/)
- The agentic-forecasting components expected by researchers are perception, planning, action, reflection and memory — [arXiv 2602.01776](https://arxiv.org/abs/2602.01776). Auditable revisions with "structural safety constraints" plus a reflection memory bank — [arXiv 2606.02497](https://arxiv.org/abs/2606.02497)
- **State and replay:** LangGraph checkpointers (SQLite for local) enable time travel/replay and fault tolerance per thread — [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence). PydanticAI `FunctionModel`/`TestModel` give fully deterministic agent runs without an LLM — [PydanticAI testing](https://pydantic.dev/docs/ai/guides/testing/). Ollama's OpenAI endpoint supports "Reproducible outputs" (seed) — [Ollama OpenAI compat](https://docs.ollama.com/api/openai-compatibility)
- **Event-driven re-run / scheduling (key-less, in-process):**
  - `apscheduler` 3.11.3 (MIT; in-process cron-like scheduler) — [PyPI](https://pypi.org/project/apscheduler/)
  - `watchdog` 6.0.0 (Apache-2.0; filesystem events; last release 2024-11-01) — [PyPI](https://pypi.org/project/watchdog/)
  - `prefect` 3.8.6 (Apache-2.0) — [PyPI](https://pypi.org/project/prefect/)
  - `dagster` 1.13.24 — [PyPI](https://pypi.org/project/dagster/)
  - `temporalio` 1.33.0 — [PyPI](https://pypi.org/project/temporalio/)
- **Observability without vendor keys:**
  - OpenAI Agents SDK traces go to OpenAI unless disabled — [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/models/)
  - Langfuse self-hosting needs Postgres + ClickHouse + Redis + S3/MinIO; some enterprise features need a licence key; supports OpenTelemetry — [Langfuse self-hosting](https://langfuse.com/self-hosting). SDK `langfuse` 4.15.4 (MIT) — [PyPI](https://pypi.org/project/langfuse/)
  - Arize Phoenix `arize-phoenix` 20.15.0 is licensed **Elastic-2.0** (not OSI) — [PyPI](https://pypi.org/project/arize-phoenix/)
  - OpenInference instrumentation 0.1.65 (Apache-2.0) — [PyPI](https://pypi.org/project/openinference-instrumentation/)
  - MLflow 3.16.1 — [PyPI](https://pypi.org/project/mlflow/)
  - MAF, PydanticAI, CrewAI, ADK and MCP all depend on `opentelemetry-api`, so OTel spans can go to a local console/file exporter — [PyPI agent-framework-core](https://pypi.org/project/agent-framework-core/), [PyPI pydantic-ai-slim](https://pypi.org/project/pydantic-ai-slim/), [PyPI crewai](https://pypi.org/project/crewai/), [PyPI google-adk](https://pypi.org/project/google-adk/), [PyPI mcp](https://pypi.org/project/mcp/)
  - Haystack's core deps include `posthog` (telemetry client) — [PyPI](https://pypi.org/project/haystack-ai/)
- **Guardrails:**
  - smolagents CodeAgent executes LLM-written Python and recommends sandboxes (E2B/Docker/Modal/Blaxel) — [smolagents docs](https://huggingface.co/docs/smolagents/index)
  - Small local models tend toward eager tool calls, hallucinated tool names and failure loops, so validate tool names and args and cap iterations — [InsiderLLM](https://insiderllm.com/guides/function-calling-local-llms/)
  - Energy reviews stress physics grounding and hallucination control — [arXiv 2605.25141](https://arxiv.org/abs/2605.25141)
  - The smart-grid tutorial flags tool-injection risks — [arXiv 2607.18147](https://arxiv.org/html/2607.18147)

### Inferences
- **"Real" agentic vs scripted pipeline (synthesis):** a fixed `fetch → prep → predict → save` script is a *workflow* by Anthropic's definition. To show agency while staying reproducible, add decision points where the agent (LLM, or a rule-based policy when no LLM is available) does the following, and logs each decision as human-readable JSON/Markdown with inputs, tool calls, rationale and outcome:
  - chooses tools or branches: data-quality checks, whether weather inputs changed since the last run (hash/`issued_at` comparison → recompute)
  - picks a fallback (e.g., a different NWP model or a persistence baseline when data is missing)
  - self-evaluates (sanity checks: capacity bounds, ramp limits, comparison with the previous forecast or a climatology baseline) and retries or revises
- **Supervisor/worker vs plan-execute:** for a small single-purpose system, one supervisor or planner with a handful of typed tools (fetch_weather, prepare_features, run_model, evaluate_forecast, write_report) plus an evaluator loop is enough. Multi-agent "crews" add latency without clear value on a CPU LLM.
- **Deterministic replay for February backtests:** drive the same graph with an injected `as_of` clock, point data access at as-of snapshots (e.g., Open-Meteo Previous Runs), fix seeds, and cache LLM responses keyed by prompt hash, or use rule-based mode. Repeated runs are then bit-identical, and evaluators can run the replay without any key.
- **Observability for judges:** local JSONL run logs plus a per-run Markdown report are zero-setup. OpenTelemetry console/file export is a cheap upgrade. Self-hosted Langfuse needs four services and is overkill for a 4 h build.

### Gaps
- No primary source was found that documents what hackathon judges specifically score as "agentic". The criteria above synthesize vendor definitions and research-paper components.
- APScheduler 4.x status (it has been in pre-release for a long time) was not checked. PyPI "latest" is 3.11.3.
- No verified figures on Langfuse or Phoenix minimum resources for a laptop.
