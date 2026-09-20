"""
MCP Server for AI Documentation Assistant
Allows external clients (Claude Desktop, Cursor, Antigravity, MCP Inspector)
to search indexed documentation, fetch live web docs, and query the RAG agent over Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP
from langchain_agent import ask_agent
from tools import (
    retrieve_relevant_chunks,
    fetch_up_to_date_doc,
    fetch_llms_txt_index,
)

# Initialize FastMCP Server
mcp = FastMCP("langchain-doc-assistant")


@mcp.tool()
def search_langchain_docs(query: str) -> str:
    """Search the local indexed Chroma vector database for LangChain documentation chunks matching the query."""
    return retrieve_relevant_chunks.invoke({"user_query": query})


@mcp.tool()
def fetch_langchain_llms_txt_index(section: str = "python") -> str:
    """Fetch official LangChain llms.txt documentation index (sections: master, python, langgraph, deepagents)."""
    return fetch_llms_txt_index.invoke({"section": section})


@mcp.tool()
def fetch_up_to_date_documentation(url: str) -> str:
    """Fetch real-time, up-to-date documentation content directly from a live web URL or raw .md via llms.txt endpoint."""
    return fetch_up_to_date_doc.invoke({"url": url})


@mcp.tool()
def ask_documentation_assistant(user_question: str) -> str:
    """Query the full LangChain RAG agent with a question to get a synthesized answer based on documentation."""
    messages = [{"role": "user", "content": user_question}]
    return ask_agent(messages)


if __name__ == "__main__":
    mcp.run()
