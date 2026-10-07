from app.vectorstore.qdrant_client import get_qdrant_store
from ingestion.embedder import get_embedder
from app.llm.client import get_llm_client

async def retrieval_agent(state: dict) -> dict:
    question = state.get("question", "")
    chat_history = state.get("chat_history", [])
    
    standalone_question = question
    if chat_history:
        # Condense follow-up question using chat history
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-4:]])
        prompt = f"""Given the following conversation history and follow-up question, rephrase the follow-up question into a standalone engineering query.

History:
{history_str}

Follow-up Question: {question}

Standalone Question:"""
        llm = get_llm_client()
        standalone_question = await llm.generate(prompt=prompt, temperature=0.1)

    # Hybrid / vector search top-8 chunks from Qdrant
    embedder = get_embedder()
    query_vector = embedder.encode([standalone_question])[0]
    
    vectorstore = get_qdrant_store()
    retrieved_chunks = vectorstore.search(query_vector=query_vector, top_k=8)

    return {
        "retrieved_chunks": retrieved_chunks,
        "question": standalone_question
    }
