"""Web search skill using DDGS."""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for current information."""
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(r)
        if not results:
            return f"No results for: {query}"
        output = f"Web search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            output += f"{i}. **{r.get('title', '')}**\n"
            output += f"   {r.get('body', '')}\n"
            output += f"   Source: {r.get('href', '')}\n\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"
