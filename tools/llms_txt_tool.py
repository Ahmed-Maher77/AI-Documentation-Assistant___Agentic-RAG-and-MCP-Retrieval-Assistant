import urllib.request
from langchain.tools import tool


@tool
def fetch_llms_txt_index(section: str = "python") -> str:
    """Fetch the official llms.txt documentation index from LangChain (sections: master, python, langgraph, deepagents).
    This is the PREFERRED first-choice live tool to check when local documentation chunks are insufficient before falling back to web search.
    """
    urls = {
        "master": "https://python.langchain.com/llms.txt",
        "python": "https://docs.langchain.com/oss/python/langchain/llms.txt",
        "langgraph": "https://docs.langchain.com/oss/python/langgraph/llms.txt",
        "deepagents": "https://docs.langchain.com/oss/python/deepagents/llms.txt",
    }
    target_url = urls.get(section.lower().strip(), urls["python"])
    try:
        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            return f"LangChain llms.txt Index ({section}):\n{target_url}\n\n{content[:4000]}"
    except Exception as exc:
        return f"Failed to fetch llms.txt index: {exc}"
