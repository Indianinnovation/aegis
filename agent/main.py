import os, uuid, json, yaml
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_core.tools import tool
from core.security import secrets, memory_store, audit

cfg = yaml.safe_load(Path("/app/config.yaml").read_text())

app = FastAPI(title="Aegis Agent API")
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
            output += f"{i}. **{r.get('title','')}**\n"
            output += f"   {r.get('body','')}\n"
            output += f"   Source: {r.get('href','')}\n\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def get_current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime
    import pytz
    tz = pytz.timezone(cfg.get("agent", {}).get("timezone", "America/New_York"))
    now = datetime.now(tz)
    return now.strftime("Today is %A, %B %d, %Y. Time: %I:%M %p %Z")

@tool
def remember_this(content: str) -> str:
    """Save an important fact to memory."""
    memory_store.save("default_user", content)
    return f"Remembered: {content}"

@tool
def recall_memories() -> str:
    """Recall recent memories about the user."""
    mems = memory_store.recall("default_user", limit=5)
    if not mems:
        return "No memories stored yet."
    return "I remember:\n" + "\n".join(f"- {m}" for m in mems)

tools = [web_search, get_current_time, remember_this, recall_memories]

api_key = secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")

llm = ChatAnthropic(
    model=cfg.get("agent", {}).get("model", "claude-sonnet-4-5"),
    anthropic_api_key=api_key,
    max_tokens=1024,
)
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str
    user_id: str

def agent_node(state: AgentState):
    mems = memory_store.recall(state["user_id"], limit=3)
    mem_ctx = "\n".join(mems) if mems else "No prior context."
    name = cfg.get("agent", {}).get("name", "Aegis Assistant")
    user = cfg.get("agent", {}).get("user", "User")
    system = f"""You are {name}, a secure personal AI assistant for {user}.
You have web search, time, and memory tools available.
Be concise and helpful.

Memory context:
{mem_ctx}
"""
    response = llm_with_tools.invoke([SystemMessage(content=system)] + state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

checkpointer = MemorySaver()
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
compiled = graph.compile(checkpointer=checkpointer)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": cfg.get("agent", {}).get("name", "Aegis"),
        "model": cfg.get("agent", {}).get("model", "unknown"),
        "api_key": "loaded" if api_key else "MISSING"
    }

@app.post("/chat")
async def chat(payload: dict):
    message = payload.get("message", "").strip()
    user_id = payload.get("user_id", "default_user")
    session_id = payload.get("session_id", str(uuid.uuid4()))
    if not message:
        raise HTTPException(400, "message is required")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")
    config = {"configurable": {"thread_id": f"{user_id}_{session_id}"}}
    try:
        result = compiled.invoke({
            "messages": [HumanMessage(content=message)],
            "session_id": session_id,
            "user_id": user_id,
        }, config=config)
        reply = result["messages"][-1].content
        audit.log(user_id, "chat", "approved", "ok", "success", "api", session_id)
        memory_store.save(user_id, f"User asked: {message[:150]}")
        return {"reply": reply, "session_id": session_id}
    except Exception as e:
        raise HTTPException(500, f"Agent error: {str(e)}")

@app.get("/audit")
async def get_audit(limit: int = 20):
    path = Path("/app/data/audit.jsonl")
    if not path.exists():
        return {"entries": []}
    entries = []
    for line in path.read_text().strip().split("\n")[-limit:]:
        try:
            entries.append(json.loads(line))
        except Exception:
            pass
    return {"entries": list(reversed(entries))}

@app.get("/memories")
async def get_memories(user_id: str = "default_user"):
    return {"memories": memory_store.recall(user_id, limit=20)}

@app.delete("/memories")
async def purge_memories(user_id: str = "default_user"):
    memory_store.purge(user_id)
    return {"status": "purged"}

if __name__ == "__main__":
    print(f"Starting Aegis — {cfg.get('agent',{}).get('name','Agent')}")
    print(f"Model: {cfg.get('agent',{}).get('model','claude-sonnet-4-5')}")
    print(f"API Key: {'loaded' if api_key else 'MISSING'}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")