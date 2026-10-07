from app.llm.client import get_llm_client

async def correction_agent(state: dict) -> dict:
    question = state.get("question", "")
    retrieved_chunks = state.get("retrieved_chunks", [])
    draft_answer = state.get("draft_answer", "")
    val_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)

    issues = val_result.get("issues", [])
    unsupported = val_result.get("unsupported_claims", [])
    
    context_blocks = []
    for chunk in retrieved_chunks:
        source_path = chunk.get("source_path", "unknown")
        heading = chunk.get("heading", "General")
        text = chunk.get("text", "")
        context_blocks.append(f"[Source: {source_path}#{heading}]\n{text}")

    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are DocRAG Correction Agent.
The previous draft answer failed validation because it contained unsupported claims or low groundedness score.

Context Documents:
{context_str}

Previous Draft Answer:
{draft_answer}

Flagged Issues:
{issues}

Unsupported Claims to Remove/Fix:
{unsupported}

Rewrite the answer to strictly rely ONLY on the verified context documents. Remove any ungrounded assertions. Retain proper inline citations [Source: file#heading].

Corrected Answer:"""

    llm = get_llm_client()
    corrected_answer = await llm.generate(prompt=prompt, temperature=0.1)

    return {
        "draft_answer": corrected_answer,
        "retry_count": retry_count + 1
    }
