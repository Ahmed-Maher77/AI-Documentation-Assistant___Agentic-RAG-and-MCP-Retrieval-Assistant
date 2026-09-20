import json
import os
import subprocess
import time
from urllib.request import urlopen

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from tools import retrieve_relevant_chunks, fetch_llms_txt_index, fetch_up_to_date_doc

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
        except Exception as exc:
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


def create_langchain_agent():
    """Create and configure the LangChain documentation assistant agent."""
    ensure_ollama_server()

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    system_prompt = """
You are an AI documentation assistant.

When the user asks a question about LangChain:

1. Always start by using the `retrieve_relevant_chunks` tool to query the local vector index.
2. Read the `[RETRIEVAL EVALUATION]` header returned by `retrieve_relevant_chunks`.
3. If the evaluation status is `INSUFFICIENT` or `PARTIALLY_SUFFICIENT`:
   - PREFER to first call `fetch_llms_txt_index` to inspect the official LangChain llms.txt index.
   - If `fetch_llms_txt_index` does not provide sufficient details or if a specific live web search is required, call `fetch_up_to_date_doc`.
4. Synthesize your final answer based strictly on the retrieved documentation chunks and fetched live content.
5. Do not invent information that is not supported by the retrieved documentation.
6. If no relevant documentation can be found after checking live sources, inform the user clearly.
"""

    return create_agent(
        model=llm,
        tools=[retrieve_relevant_chunks, fetch_llms_txt_index, fetch_up_to_date_doc],
        system_prompt=system_prompt,
    )


_agent = None


def get_agent():
    """Lazy initializer for the LangChain agent."""
    global _agent
    if _agent is None:
        _agent = create_langchain_agent()
    return _agent


# ============== Ask Agent a question (exported function) ==============
def ask_agent(messages: list[dict]):
    """Query the LangChain documentation agent with a list of message dicts."""
    agent_instance = get_agent()
    response = agent_instance.invoke({
        "messages": messages
    })

    return response["messages"][-1].content