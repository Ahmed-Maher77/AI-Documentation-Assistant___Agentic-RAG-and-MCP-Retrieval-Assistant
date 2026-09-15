# 📚 AI Documentation Assistant — Agentic RAG-Style Retrieval Assistant

> A lightweight **agentic RAG-style** chatbot that answers questions about **LangChain** using retrieved documentation as the primary source. Built with LangChain, Chroma, Ollama, and Streamlit.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.4%2B-green.svg)](https://www.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63%2B-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-purple.svg)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Overview

**AI Documentation Assistant** is a practical implementation of a **minimal, tool-using LangChain agent** for retrieval-augmented generation.

This project is best described as an **agentic RAG-style workflow**:

- the model is created as a LangChain agent,
- it is given a custom `retrieve_relevant_chunks` tool,
- and it uses that tool to ground its answer in the LangChain documentation before responding.

This is not a full-scale multi-agent system or autonomous planner. It is a focused, single-tool retrieval workflow with strong grounding and tool-based reasoning.

Ask it anything about LangChain — concepts, LCEL, LangGraph, agents, tools, memory, deployment, LangSmith — and get grounded, hallucination-resistant answers through a Streamlit chat UI.

### Is this “agentic RAG”?

Yes, in the practical sense that the model acts like an agent and calls a document-retrieval tool before answering. But this is a **lightweight agentic retrieval pattern**, not a broad multi-agent orchestration system.

| Classic RAG                       | This project                          |
| --------------------------------- | ------------------------------------- |
| Fixed retrieve-then-generate flow | Tool-using agent with retrieval step  |
| Retrieval is usually pre-scripted | LLM decides to use the retrieval tool |
| Limited flexibility               | Easy to extend with more tools        |
| One-shot context injection        | Single-tool grounding workflow        |

---

## 🚀 Features

- 🤖 **Agentic retrieval flow** — LangChain `create_agent` + custom retrieval tool
- 📖 **Grounded answers** — responses sourced from `https://docs.langchain.com/`
- 🔍 **Semantic search** — `all-MiniLM-L6-v2` embeddings + Chroma vector store
- 💬 **Chat UI** — Streamlit chat with history, clear / save / load (`chat.json`)
- 🦙 **Local-first LLM** — Ollama (`gpt-oss:120b-cloud` by default, configurable)
- 🕷️ **Docs ingestion pipeline** — Tavily Crawl → chunk → embed → persist
- 📎 **Source attribution** — retrieved chunks include `Source: <url>`
- 🛡️ **Anti-hallucination guardrails** — "don't invent, say when not found" system prompt
- 🔭 **LangSmith-ready** — tracing support via `.env`

---

## 🏗️ Architecture

```text
┌─────────────────┐       TavilyCrawl       ┌──────────────────┐
│ docs.langchain  │ ──────────────────────► │   ingestion.py   │
│     .com/       │   raw_content + URL     │ split (1000/200) │
└─────────────────┘                         │ embed MiniLM-L6  │
                                            └────────┬─────────┘
                                                     │ persist
                                                     ▼
                                            ┌──────────────────┐
                                            │  ChromaDB        │
                                            │  ./chroma_db/    │
                                            └────────┬─────────┘
                                                     │ retriever k=5
                                                     ▼
┌──────────┐   question   ┌──────────────────────┐   tool   ┌──────────────┐
│  User    │ ───────────► │  Streamlit (main.py) │ ───────► │ LangChain    │
│ (browser)│ ◄─────────── │  ask_agent()         │ ◄─────── │ Agent +      │
└──────────┘   markdown   └──────────────────────┘  answer  │ Ollama LLM   │
                                                            └──────────────┘
```

**Flow:**

1. `ingestion.py` crawls LangChain docs, chunks with `RecursiveCharacterTextSplitter`, embeds, and stores them in Chroma.
2. `langchain_agent.py` exposes a `retrieve_relevant_chunks` tool over a Chroma retriever (`k=5`).
3. `main.py` (Streamlit) maintains chat history and calls `ask_agent(messages)`.
4. The LangChain agent uses the retrieval tool as a grounding step before answering. If nothing relevant is found, it says so.

This is a minimal agentic workflow: an agent with one retrieval tool, not a broad multi-agent orchestration system.

---

## 🧰 Tech Stack

| Layer                 | Technology                                             |
| --------------------- | ------------------------------------------------------ |
| Agent / Orchestration | LangChain `create_agent`, LangChain Tools              |
| LLM                   | Ollama `ChatOllama` (default: `gpt-oss:120b-cloud`)    |
| Embeddings            | HuggingFace `sentence-transformers/all-MiniLM-L6-v2`   |
| Vector Store          | ChromaDB (local persistent, `./chroma_db/`)            |
| Doc Crawler           | Tavily `TavilyCrawl` (`max_depth=2`, `max_breadth=10`) |
| UI                    | Streamlit Chat                                         |
| Observability         | LangSmith Tracing (optional)                           |
| Package Manager       | `uv` / `pip` (Python ≥ 3.12)                           |

---

## 📁 Project Structure

```text
.
├── main.py              # Streamlit chat UI + session state + save/load
├── langchain_agent.py   # Ollama setup, Chroma retriever, tool + agent, ask_agent()
├── ingestion.py         # Crawl → split → embed → store pipeline
├── get_chroma_docs.py   # Debug helper: inspect Chroma collection contents
├── chat.json            # Saved chat history (gitignored, created on Save)
├── chroma_db/           # Local persistent vector DB (gitignored)
├── pyproject.toml       # Dependencies (uv / pip)
├── .env                 # API keys + config (gitignored, see below)
└── README.md
```

---

## ✅ Prerequisites

1. **Python 3.12+**
2. **uv** (recommended) or `pip`
    ```bash
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
3. **Ollama** installed and running: https://ollama.com/download
    ```bash
    ollama serve
    ollama pull gpt-oss:120b-cloud
    ```
    > You can use any Ollama chat model (e.g. `llama3.1`, `qwen2.5`, `mistral`). Just set `OLLAMA_MODEL` in `.env`.
4. **Tavily API key** (for ingestion only): https://tavily.com/

---

## ⚙️ Installation

```bash
# 1. Clone
git clone https://github.com/Ahmed-Maher77/AI-Documentation-Assistant___Agentic-RAG-Style-Retrieval-Assistant.git
cd AI-Documentation-Assistant___Agentic-RAG-Style-Retrieval-Assistant

# 2. Install dependencies (uv)
uv sync

# Or with pip:
# pip install -e .

# 3. Configure environment
cp .env.example .env
# then edit .env (see table below)

# 4. Start Ollama (separate terminal)
ollama serve
ollama pull gpt-oss:120b-cloud
```

### 🔑 Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
# Required for ingestion (crawling docs)
TAVILY_API_KEY=tvly-...

# Vector DB collection name (used as Chroma collection_name)
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

| Variable              | Required          | Description                                                          |
| --------------------- | ----------------- | -------------------------------------------------------------------- |
| `TAVILY_API_KEY`      | Yes (ingest only) | Crawls `docs.langchain.com`                                          |
| `PINECONE_INDEX_NAME` | Yes               | Chroma collection name (legacy Pinecone name kept for compatibility) |
| `OLLAMA_BASE_URL`     | No                | Defaults to `http://127.0.0.1:11434`                                 |
| `OLLAMA_MODEL`        | No                | Defaults to `gpt-oss:120b-cloud`                                     |
| `LANGSMITH_*`         | No                | Enables tracing in LangSmith                                         |

> **Note:** `PINECONE_API_KEY` / `PINECONE_ENVIRONMENT` appear in older `.env` files but are no longer used — the project uses local ChromaDB. You can safely remove them.

---

## 📥 Step 1 — Ingest Documentation

Crawl, chunk, embed, and persist LangChain docs (run once, or whenever docs update):

```bash
uv run ingestion.py
# or: python ingestion.py
```

Expected output:

```text
Crawled documents: ~XX
Created chunks: ~XXX
Data successfully stored in Chroma!
```

This creates `./chroma_db/`. Verify contents anytime with:

```bash
uv run get_chroma_docs.py
```

**Ingestion details (`ingestion.py`):**

- Crawler: `TavilyCrawl(url=https://docs.langchain.com/, max_depth=2, max_breadth=10)`
- Chunking: `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Store: `Chroma(collection_name, persist_directory="./chroma_db")`

---

## 💬 Step 2 — Run the Chat App

```bash
uv run streamlit run main.py
# or: streamlit run main.py
```

Open http://localhost:8501 and ask:

- `What is LangChain?`
- `How do I build an agent with LangChain?`
- `What is LCEL and how do I use it?`
- `How does memory work in LangChain?`
- `Explain LangGraph in simple terms`

Sidebar actions:

- 🗑️ **Clear Chat** — reset conversation
- 💾 **Save Chat** — persist to `chat.json`
- 📂 **Load Chat** — restore from `chat.json`

---

## 🧠 How the Agent Works (`langchain_agent.py`)

```python
@tool
def retrieve_relevant_chunks(user_query: str) -> str:
    """Retrieve relevant chunks from the LangChain documentation."""
    docs = retriever.invoke(user_query)  # Chroma, k=5
    ...
    return "\n\n---\n\n".join(f"Source: {url}\n{content}" ...)

agent = create_agent(
    model=ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL),
    tools=[retrieve_relevant_chunks],
    system_prompt="Always use the tool. Answer only from retrieved docs. Don't invent...",
)

def ask_agent(messages: list[dict]):
    return agent.invoke({"messages": messages})["messages"][-1].content
```

Key behaviors:

- Auto-starts `ollama serve` if the server isn't responding and validates the model is installed.
- Retriever returns top-5 chunks with source URLs for citation.
- System prompt enforces grounding and graceful fallback (`No relevant documentation was found`).

---

## 🛠️ Customization

- **Change LLM:** set `OLLAMA_MODEL=llama3.1:8b` (or any `ollama pull`-able model) in `.env`.
- **Tune retrieval:** edit `search_kwargs={"k": 5}` in `langchain_agent.py`.
- **Tune chunking:** edit `chunk_size` / `chunk_overlap` in `ingestion.py`, then re-run ingestion.
- **Index other docs:** change the `url` in `get_langchain_docs()` to any documentation site, delete `./chroma_db/`, and re-ingest.
- **Add tools:** append new `@tool` functions (e.g. Tavily web search, calculator) to the `tools=[...]` list in `create_langchain_agent()`.

---

## ⚠️ Limitations

- Ingestion is a one-shot crawl (`max_depth=2`); very deep or JS-heavy doc pages may be missed.
- Local embeddings + Chroma run on CPU by default — first run downloads ~90 MB model.
- Answer quality depends on the Ollama model; smaller local models may be less precise than cloud LLMs.
- No streaming tokens yet (single `st.markdown` render per turn) and no auth/multi-user isolation.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit (`git commit -m "feat: add my feature"`)
4. Push and open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

Documentation content retrieved at runtime belongs to its respective owners (LangChain).

---

## 👨‍💻 Author

**Ahmed Maher** — [Portfolio](https://ahmedmaher-portfolio.vercel.app/)

> If you found this useful, please ⭐ star the repo!
