from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

from app.agents.retrieval import retrieval_agent
from app.agents.generation import generation_node
from app.agents.validation import validation_agent
from app.agents.correction import correction_agent
from app.db.session import AsyncSessionLocal
from app.db.models import AgentTrace

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    END = "__end__"

class GraphState(TypedDict, total=False):
    question: str
    chat_history: list
    retrieved_chunks: list
    draft_answer: str
    validation_result: dict
    final_answer: str
    retry_count: int
    session_id: str
    message_id: str
    low_confidence: bool
    traces: list

async def log_trace(session_id: str, message_id: str, node_name: str, input_sum: str, output_sum: str, meta: dict = None):
    if not session_id:
        return
    try:
        async with AsyncSessionLocal() as db:
            trace = AgentTrace(
                session_id=session_id,
                message_id=message_id,
                node_name=node_name,
                input_summary=input_sum[:500] if input_sum else "",
                output_summary=output_sum[:500] if output_sum else "",
                metadata_json=meta or {},
                created_at=datetime.utcnow()
            )
            db.add(trace)
            await db.commit()
    except Exception:
        pass

async def wrapped_retrieve(state: GraphState) -> GraphState:
    res = await retrieval_agent(state)
    chunks = res.get("retrieved_chunks", [])
    question = res.get("question", state.get("question", ""))
    
    traces = list(state.get("traces", []))
    trace_item = {
        "node_name": "retrieve",
        "input_summary": f"Question: {question}",
        "output_summary": f"Retrieved {len(chunks)} chunks from vector store.",
        "metadata": {"chunk_count": len(chunks)}
    }
    traces.append(trace_item)

    await log_trace(
        session_id=state.get("session_id"),
        message_id=state.get("message_id"),
        node_name="retrieve",
        input_sum=trace_item["input_summary"],
        output_sum=trace_item["output_summary"],
        meta=trace_item["metadata"]
    )
    return {**state, "retrieved_chunks": chunks, "question": question, "traces": traces}

async def wrapped_generate(state: GraphState) -> GraphState:
    res = await generation_node(state)
    draft = res.get("draft_answer", "")
    
    traces = list(state.get("traces", []))
    trace_item = {
        "node_name": "generate",
        "input_summary": f"Context chunks: {len(state.get('retrieved_chunks', []))}",
        "output_summary": f"Draft generated ({len(draft)} chars).",
        "metadata": {"draft_snippet": draft[:100]}
    }
    traces.append(trace_item)

    await log_trace(
        session_id=state.get("session_id"),
        message_id=state.get("message_id"),
        node_name="generate",
        input_sum=trace_item["input_summary"],
        output_sum=trace_item["output_summary"],
        meta=trace_item["metadata"]
    )
    return {**state, "draft_answer": draft, "traces": traces}

async def wrapped_validate(state: GraphState) -> GraphState:
    res = await validation_agent(state)
    val_res = res.get("validation_result", {})
    
    traces = list(state.get("traces", []))
    passed = val_res.get("passed", False)
    score = val_res.get("groundedness_score", 0.0)
    trace_item = {
        "node_name": "validate",
        "input_summary": f"Evaluating draft answer against context.",
        "output_summary": f"Validation Passed: {passed} (Score: {score}).",
        "metadata": val_res
    }
    traces.append(trace_item)

    await log_trace(
        session_id=state.get("session_id"),
        message_id=state.get("message_id"),
        node_name="validate",
        input_sum=trace_item["input_summary"],
        output_sum=trace_item["output_summary"],
        meta=val_res
    )
    return {**state, "validation_result": val_res, "traces": traces}

async def wrapped_correct(state: GraphState) -> GraphState:
    res = await correction_agent(state)
    draft = res.get("draft_answer", "")
    retry_count = res.get("retry_count", state.get("retry_count", 0) + 1)
    
    traces = list(state.get("traces", []))
    trace_item = {
        "node_name": "correct",
        "input_summary": f"Retry #{retry_count} triggered.",
        "output_summary": f"Corrected draft generated ({len(draft)} chars).",
        "metadata": {"retry_count": retry_count}
    }
    traces.append(trace_item)

    await log_trace(
        session_id=state.get("session_id"),
        message_id=state.get("message_id"),
        node_name="correct",
        input_sum=trace_item["input_summary"],
        output_sum=trace_item["output_summary"],
        meta=trace_item["metadata"]
    )
    return {**state, "draft_answer": draft, "retry_count": retry_count, "traces": traces}

def route_on_validation(state: GraphState) -> str:
    val_res = state.get("validation_result", {})
    passed = val_res.get("passed", False)
    retry_count = state.get("retry_count", 0)

    if passed:
        return "pass"
    elif retry_count < 2:
        return "retry"
    else:
        return "escalate"

class DocRAGFallbackGraph:
    """Fallback state graph runner when langgraph library is not installed."""
    async def ainvoke(self, initial_state: GraphState) -> GraphState:
        state = dict(initial_state)
        state = await wrapped_retrieve(state)
        state = await wrapped_generate(state)
        
        while True:
            state = await wrapped_validate(state)
            route = route_on_validation(state)
            if route == "pass":
                break
            elif route == "retry":
                state = await wrapped_correct(state)
            else: # escalate
                state["low_confidence"] = True
                break
        return state

    async def astream(self, initial_state: GraphState):
        state = dict(initial_state)
        
        state = await wrapped_retrieve(state)
        yield {"retrieve": state}

        state = await wrapped_generate(state)
        yield {"generate": state}

        while True:
            state = await wrapped_validate(state)
            yield {"validate": state}
            route = route_on_validation(state)
            if route == "pass":
                break
            elif route == "retry":
                state = await wrapped_correct(state)
                yield {"correct": state}
            else:
                state["low_confidence"] = True
                break

if HAS_LANGGRAPH:
    builder = StateGraph(GraphState)
    builder.add_node("retrieve", wrapped_retrieve)
    builder.add_node("generate", wrapped_generate)
    builder.add_node("validate", wrapped_validate)
    builder.add_node("correct", wrapped_correct)

    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", "validate")

    builder.add_conditional_edges(
        "validate",
        route_on_validation,
        {
            "pass": END,
            "retry": "correct",
            "escalate": END
        }
    )
    builder.add_edge("correct", "validate")

    doc_rag_graph = builder.compile()
else:
    doc_rag_graph = DocRAGFallbackGraph()
