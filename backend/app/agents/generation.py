from app.llm.client import get_llm_client

async def generation_node(state: dict) -> dict:
    question = state.get("question", "")
    retrieved_chunks = state.get("retrieved_chunks", [])
    
    context_blocks = []
    for chunk in retrieved_chunks:
        source_path = chunk.get("source_path", "unknown")
        heading = chunk.get("heading", "General")
        text = chunk.get("text", "")
        context_blocks.append(f"[Source: {source_path}#{heading}]\n{text}")

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."
    
    prompt = f"""You are DocRAG, an internal engineering assistant. Answer the user's question using ONLY the provided documentation context below.
Requirements:
1. Include inline citations for every factual statement using [Source: file#heading].
2. Do NOT invent facts or claim details not present in the context.

Context:
{context_str}

User Question: {question}

Draft Answer:"""

    llm = get_llm_client()
    draft_answer = await llm.generate(prompt=prompt, temperature=0.2)

    return {
        "draft_answer": draft_answer
    }
