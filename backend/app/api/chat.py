import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from sqlalchemy.future import select

from app.graph import doc_rag_graph
from app.db.session import AsyncSessionLocal
from app.db.models import ChatSession, ChatMessage, AgentTrace

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SourceItem(BaseModel):
    source_path: str
    heading: str
    chunk_id: str
    score: Optional[float] = None
    text: Optional[str] = None

class TraceItem(BaseModel):
    node_name: str
    input_summary: str
    output_summary: str
    metadata: Optional[dict] = None

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    sources: List[SourceItem] = []
    traces: List[TraceItem] = []
    low_confidence: bool = False

@router.post("/chat", response_model=ChatResponse)
async def chat_agentic_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    message_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        # Ensure ChatSession exists
        session_obj = await db.get(ChatSession, session_id)
        if not session_obj:
            session_obj = ChatSession(id=session_id, title=request.message[:40])
            db.add(session_obj)

        # Store user message
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        await db.commit()

        # Fetch recent chat history
        res = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        history_msgs = res.scalars().all()
        chat_history = [{"role": m.role, "content": m.content} for m in history_msgs]

    # Initialize GraphState
    initial_state = {
        "question": request.message,
        "chat_history": chat_history,
        "retrieved_chunks": [],
        "draft_answer": "",
        "validation_result": {},
        "final_answer": "",
        "retry_count": 0,
        "session_id": session_id,
        "message_id": message_id,
        "low_confidence": False,
        "traces": []
    }

    # Execute LangGraph multi-agent flow
    final_state = await doc_rag_graph.ainvoke(initial_state)

    answer = final_state.get("draft_answer", "No answer generated.")
    chunks = final_state.get("retrieved_chunks", [])
    val_res = final_state.get("validation_result", {})
    traces = final_state.get("traces", [])
    retry_count = final_state.get("retry_count", 0)

    # Determine low confidence flag (if validation failed after max retries)
    low_confidence = not val_res.get("passed", False) if retry_count >= 2 else False

    sources = [
        SourceItem(
            source_path=c.get("source_path", "unknown"),
            heading=c.get("heading", "General"),
            chunk_id=c.get("chunk_id", ""),
            score=c.get("score", 0.0),
            text=c.get("text", "")
        )
        for c in chunks
    ]

    trace_items = [
        TraceItem(
            node_name=t["node_name"],
            input_summary=t["input_summary"],
            output_summary=t["output_summary"],
            metadata=t.get("metadata", {})
        )
        for t in traces
    ]

    # Store assistant message in DB
    async with AsyncSessionLocal() as db:
        assistant_msg = ChatMessage(
            id=message_id,
            session_id=session_id,
            role="assistant",
            content=answer,
            sources=[s.dict() for s in sources]
        )
        db.add(assistant_msg)
        await db.commit()

    return ChatResponse(
        session_id=session_id,
        message_id=message_id,
        answer=answer,
        sources=sources,
        traces=trace_items,
        low_confidence=low_confidence
    )

@router.websocket("/chat/ws")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        req_data = json.loads(data)
        message = req_data.get("message", "")
        session_id = req_data.get("session_id") or str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        await websocket.send_json({
            "type": "init",
            "session_id": session_id,
            "message_id": message_id
        })

        initial_state = {
            "question": message,
            "chat_history": [],
            "retrieved_chunks": [],
            "draft_answer": "",
            "validation_result": {},
            "final_answer": "",
            "retry_count": 0,
            "session_id": session_id,
            "message_id": message_id,
            "low_confidence": False,
            "traces": []
        }

        # Stream LangGraph state updates
        async for event in doc_rag_graph.astream(initial_state):
            for node_name, node_output in event.items():
                await websocket.send_json({
                    "type": "trace_step",
                    "node_name": node_name,
                    "output": {
                        "draft_answer": node_output.get("draft_answer"),
                        "validation_result": node_output.get("validation_result"),
                        "retry_count": node_output.get("retry_count", 0),
                        "chunk_count": len(node_output.get("retrieved_chunks", []))
                    }
                })

        # Final answer yield
        final_state = await doc_rag_graph.ainvoke(initial_state)
        answer = final_state.get("draft_answer", "")
        chunks = final_state.get("retrieved_chunks", [])
        traces = final_state.get("traces", [])
        
        sources = [
            {
                "source_path": c.get("source_path", "unknown"),
                "heading": c.get("heading", "General"),
                "chunk_id": c.get("chunk_id", ""),
                "score": c.get("score", 0.0),
                "text": c.get("text", "")
            }
            for c in chunks
        ]

        await websocket.send_json({
            "type": "complete",
            "answer": answer,
            "sources": sources,
            "traces": traces,
            "low_confidence": final_state.get("retry_count", 0) >= 2 and not final_state.get("validation_result", {}).get("passed", False)
        })

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        await websocket.close()
