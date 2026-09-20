# 📚 AI Documentation Assistant — Agentic RAG & MCP Retrieval Assistant

> A lightweight **agentic RAG-style** chatbot and **Model Context Protocol (MCP)** server that answers questions about **LangChain** using local vector retrieval, real-time `llms.txt` document resolution, and Corrective RAG (CRAG) context quality evaluation. Built with LangChain, Chroma, Ollama, FastMCP, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.4%2B-green.svg)](https://www.langchain.com/)
[![MCP](https://img.shields.io/badge/MCP-1.30%2B-blueviolet.svg)](https://modelcontextprotocol.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63%2B-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-purple.svg)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Overview

**AI Documentation Assistant** is a production-ready implementation of an **agentic retrieval-augmented generation (RAG)** workflow and an open **Model Context Protocol (MCP) server**.

It features an intelligent **Corrective RAG (CRAG)** pattern:
- The agent queries local Chroma vector embeddings.
- An automated **Context Quality Evaluator** measures relevance scores, total character volume, and query coverage.
- If vector retrieval is `INSUFFICIENT` or low-confidence, the system automatically falls back to live documentation fetching via LangChain's official **`llms.txt` standard** and raw `.md` endpoints.

Ask it anything about LangChain — concepts, LCEL, LangGraph, agents, tools, memory, deployment, LangSmith — and get grounded, hallucination-resistant answers through a Streamlit chat UI or via MCP clients (Claude Desktop, Cursor, Antigravity, MCP Inspector).

---

## 🚀 Key Features

- 🤖 **Agentic Retrieval Flow** — LangChain `create_agent` with multi-tool grounding.
- 🎯 **Corrective RAG (CRAG) Evaluator** — Evaluates vector chunk relevance, density, and query coverage with actionable agent feedback.
- ⚡ **Model Context Protocol (MCP) Server** — Standalone `FastMCP` server (`mcp_server.py`) for external tool integration.
- 📜 **`llms.txt` Standard Support** — Fetches official LangChain `llms.txt` section indexes (`python`, `langgraph`, `deepagents`, `master`).
- 🌐 **Raw `.md` Live Doc Resolution** — Automatically resolves and fetches raw `.md` documentation endpoints served by LangChain (zero HTML clutter).
- 🛠️ **MCP Inspector Debugging** — Interactive visual debugging UI via `npx @modelcontextprotocol/inspector`.
- 📁 **Modular Tool Architecture** — Cleanly decoupled into a [`tools/`](file:///e:/OneDrive/Courses/AI%20Agentic/Practice/AI-Documentation-Assistant___Agentic-RAG/tools) package.
- 💬 **Streamlit Chat UI** — Chat history management (save/load `chat.json`, clear), spinner states, and MCP debugging drawer.
- 🦙 **Local-First LLM** — Powered by Ollama (`gpt-oss:120b-cloud` by default, configurable).
- 🕷️ **Docs Ingestion Pipeline** — Tavily Crawl → chunk → embed → persist to Chroma.

---

## 🏗️ Architecture

```text
                               ┌─────────────────────────────┐
                               │  docs.langchain.com/        │
                               │  (HTML & raw llms.txt / .md)│
                               └──────────────┬──────────────┘
                                              │ TavilyCrawl / Live Fetch
                                              ▼
┌───────────────────┐    search    ┌──────────────────────────┐    embed     ┌───────────────────┐
│ Streamlit UI /    │ ───────────► │  langchain_agent.py      │ ───────────► │ Chroma Vector DB  │
│ MCP Server        │ ◄─────────── │  (create_agent + LLM)    │ ◄─────────── │ ./chroma_db/      │
└───────────────────┘    answer    └────────────┬─────────────┘    chunks    └───────────────────┘
                                                │
                                                ▼
                               ┌──────────────────────────────┐
                               │       tools/ Package         │
                               ├──────────────────────────────┤
                               │ • retriever_tool (CRAG Eval) │
                               │ • llms_txt_tool (Index)      │
                               │ • doc_fetch_tool (Live .md)  │
                               └──────────────────────────────┘
```

### Retrieval & Corrective Flow:
1. Agent queries `retriever_tool.py` (`retrieve_relevant_chunks`).
2. Evaluator computes cosine similarity, character density, and keyword coverage.
3. If status is `SUFFICIENT`, agent synthesizes answer directly.
4. If status is `INSUFFICIENT` or `PARTIALLY_SUFFICIENT`, agent prefers `llms_txt_tool` (`fetch_llms_txt_index`) first to inspect official documentation indexes. If more detail or live web search is needed, it uses `doc_fetch_tool` (`fetch_up_to_date_doc` powered by Tavily Search) to retrieve live, up-to-date documentation before answering.

---

## 🧰 Tech Stack

| Layer                 | Technology                                             |
| --------------------- | ------------------------------------------------------ |
| Agent / Orchestration | LangChain `create_agent`, LangChain Tools              |
| Protocol              | Model Context Protocol (MCP `mcp>=1.30.0`, `FastMCP`)  |
| LLM                   | Ollama `ChatOllama` (default: `gpt-oss:120b-cloud`)    |
| Embeddings            | HuggingFace `sentence-transformers/all-MiniLM-L6-v2`   |
| Vector Store          | ChromaDB (local persistent, `./chroma_db/`)            |
| Doc Processing        | BeautifulSoup4, LangChain Text Splitters               |
| UI                    | Streamlit Chat                                         |
| Package Manager       | `uv` / `pip` (Python ≥ 3.12)                           |

---

## 📁 Project Structure

```text
.
├── main.py              # Streamlit chat UI + session state + save/load
├── langchain_agent.py   # Ollama setup, agent orchestration & ask_agent()
├── mcp_server.py        # FastMCP Server for external clients & MCP Inspector
├── tools/               # Modular tool definitions package
│   ├── __init__.py      # Re-exports all agent & MCP tools
│   ├── retriever_tool.py# Vector retriever + CRAG context quality evaluator
│   ├── doc_fetch_tool.py# Real-time web & raw .md fetch tool
│   └── llms_txt_tool.py # Official LangChain llms.txt index fetcher
├── ingestion.py         # Crawl → split → embed → store pipeline
├── get_chroma_docs.py   # Debug helper: inspect Chroma collection contents
├── chat.json            # Saved chat history (gitignored)
├── chroma_db/           # Local persistent vector DB (gitignored)
├── pyproject.toml       # Project metadata & dependencies
├── .env                 # API keys + config (gitignored)
└── README.md
```

---

## ✅ Prerequisites

1. **Python 3.12+**
2. **uv** (recommended) or `pip`:
    ```bash
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
3. **Ollama** installed and running: https://ollama.com/download
    ```bash
    ollama serve
    ollama pull gpt-oss:120b-cloud
    ```
4. **Tavily API key** (for ingestion pipeline): https://tavily.com/

---

## ⚙️ Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/Ahmed-Maher77/AI-Documentation-Assistant___Agentic-RAG-and-MCP-Retrieval-Assistant.git
cd AI-Documentation-Assistant___Agentic-RAG-and-MCP-Retrieval-Assistant

# 2. Install dependencies with uv
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env to set your keys & preferences
```

### 🔑 Environment Variables (`.env`)

```env
# Required for ingestion
TAVILY_API_KEY=tvly-...

# Vector DB collection name
PINECONE_INDEX_NAME=langchain-docs-index

# LLM configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gpt-oss:120b-cloud

# Optional: LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=ai-doc-assistant
```

---

## 📥 Ingestion Pipeline

Crawl, chunk, embed, and persist LangChain docs to ChromaDB:

```bash
uv run ingestion.py
```

Inspect stored chunks anytime:

```bash
uv run get_chroma_docs.py
```

---

## 💬 Running the Chat App

Launch the Streamlit interface:

```bash
uv run streamlit run main.py
```

Open `http://localhost:8501` to chat with the assistant.

---

## ⚡ MCP Server & MCP Inspector Debugging

### 1. Running the MCP Server
To expose the RAG tools to external AI tools (Cursor, Claude Desktop, Antigravity):

```bash
uv run python mcp_server.py
```

**Exposed MCP Tools:**
- `search_langchain_docs(query)` — Vector search with CRAG evaluation headers.
- `fetch_langchain_llms_txt_index(section)` — Fetches official `llms.txt` indexes (`python`, `langgraph`, `deepagents`, `master`). Preferred first.
- `fetch_up_to_date_documentation(query)` — Searches and fetches real-time web documentation via Tavily Search.
- `ask_documentation_assistant(user_question)` — Full agent response synthesis.

### 2. Debugging with MCP Inspector 🛠️
Visually inspect, test, and debug MCP tools in an interactive web browser:

```bash
npx @modelcontextprotocol/inspector uv run python mcp_server.py
```

1. Open `http://localhost:5173` in your browser.
2. Click **Connect** to link via stdio transport.
3. Test tool calls, inspect JSON schemas, view execution logs, and monitor response latency.

---

## 🧠 How the Agent Works (`langchain_agent.py`)

```python
from tools import retrieve_relevant_chunks, fetch_llms_txt_index, fetch_up_to_date_doc

def create_langchain_agent():
    ensure_ollama_server()
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

    system_prompt = """
You are an AI documentation assistant.
1. Always start by using retrieve_relevant_chunks to query local vector index.
2. Read the [RETRIEVAL EVALUATION] header returned by retrieve_relevant_chunks.
3. If status is INSUFFICIENT or PARTIALLY_SUFFICIENT:
   - Prefer calling fetch_llms_txt_index first to check official index.
   - If insufficient or specific live web search is needed, call fetch_up_to_date_doc.
4. Synthesize final answer based strictly on retrieved documentation.
"""
    return create_agent(model=llm, tools=[retrieve_relevant_chunks, fetch_llms_txt_index, fetch_up_to_date_doc], system_prompt=system_prompt)
```

---

## 📄 License

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Ahmed Maher** — [Portfolio](https://ahmedmaher-portfolio.vercel.app/)

> If you found this repository useful, please consider giving it a ⭐ star!
