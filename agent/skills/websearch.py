"""Web search skill using DDGS."""

import html
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for current information."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        if not results:
            return f"No results for: {html.escape(query)}"
        output = f"Web search results for '{html.escape(query)}':\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. **{html.escape(r.get('title', ''))}**\n"
            output += f"   {html.escape(r.get('body', ''))}\n"
            output += f"   Source: {r.get('href', '')}\n\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"
