import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()

_tavily_search = None


def get_tavily_tool() -> TavilySearch:
    """Lazy loader for TavilySearch tool."""
    global _tavily_search
    if _tavily_search is None:
        _tavily_search = TavilySearch(
            max_results=4,
            topic="general",
            include_answer=True,
        )
    return _tavily_search


@tool
def fetch_up_to_date_doc(query: str) -> str:
    """Search and fetch real-time, up-to-date documentation and web results using Tavily Search.
    Use this when `fetch_llms_txt_index` does not provide sufficient detail, or when searching for specific up-to-date topics, APIs, or error solutions.
    """
    try:
        tavily = get_tavily_tool()
        results_data = tavily.invoke({"query": query})

        if isinstance(results_data, str):
            return f"Tavily Search Results for '{query}':\n\n{results_data}"

        output_parts = []
        if results_data.get("answer"):
            output_parts.append(f"Summary:\n{results_data['answer']}\n")

        results = results_data.get("results", [])
        if not results:
            return f"No live search results found for query: '{query}'."

        for idx, item in enumerate(results, 1):
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            content = item.get("content", "").strip()
            score = item.get("score")
            score_info = f" (Score: {score:.2f})" if score is not None else ""
            output_parts.append(
                f"--- Result #{idx}: {title}{score_info} ---\nSource: {url}\n{content}"
            )

        return f"Tavily Search Results for '{query}':\n\n" + "\n\n".join(output_parts)
    except Exception as exc:
        return f"Failed to search up-to-date docs with Tavily for '{query}': {exc}"
