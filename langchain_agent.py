import json
import os
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


def ensure_ollama_server() -> str:
    """Start Ollama if needed and verify the model endpoint is responding."""
    last_error = None

    for attempt in range(2):
        try:
            with urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                available_models = [model.get("name") for model in payload.get("models", [])]

                if OLLAMA_MODEL in available_models:
                    return OLLAMA_BASE_URL

                last_error = RuntimeError(
                    f"Ollama model '{OLLAMA_MODEL}' is not installed. Run: ollama pull {OLLAMA_MODEL}"
                )
        except Exception as exc:  # pragma: no cover - this is runtime environment handling
            last_error = exc

        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            time.sleep(3)
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama is not installed or not on PATH. Install Ollama and start it with `ollama serve`."
            ) from last_error

    if last_error is not None:
        raise RuntimeError(
            f"Ollama is not responding at {OLLAMA_BASE_URL}. Start it with `ollama serve` and ensure the model '{OLLAMA_MODEL}' exists."
        ) from last_error

    raise RuntimeError(
        f"Ollama is not available. Start it with `ollama serve` and ensure the model '{OLLAMA_MODEL}' exists."
    )


# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Initialize vector store using the repo's local Chroma database
vector_store = Chroma(
    collection_name=os.getenv("PINECONE_INDEX_NAME", "langchain-docs-index"),
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)


# Create retriever
retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 5
    }
)


# Retrieval tool
@tool
def retrieve_relevant_chunks(user_query: str) -> str:
    """Retrieve relevant chunks from the LangChain documentation."""

    docs = retriever.invoke(user_query)

    if not docs:
        return "No relevant documentation was found."

    chunks = []

    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        chunks.append(f"Source: {source}\n{doc.page_content}")

    return "\n\n---\n\n".join(chunks)


# Create agent
def create_langchain_agent():
    ensure_ollama_server()

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    system_prompt = """
You are an AI documentation assistant.

When the user asks a question about LangChain:

1. Always use the retrieve_relevant_chunks tool.
2. Use the retrieved documentation as your primary source.
3. Answer the user's question clearly and directly.
4. Do not invent information that is not supported by the retrieved documentation.
5. If the tool returns no relevant information, tell the user that you could not find relevant information in the documentation.
"""

    agent = create_agent(
        model=llm,
        tools=[retrieve_relevant_chunks],
        system_prompt=system_prompt,
    )

    return agent


agent = create_langchain_agent()


# ============== Ask Agent a question (exported function) ==============
def ask_agent(messages: list[dict]):
    response = agent.invoke({
        "messages": messages
    })

    return response["messages"][-1].content