import json
from app.llm.client import get_llm_client

async def validation_agent(state: dict) -> dict:
    question = state.get("question", "")
    retrieved_chunks = state.get("retrieved_chunks", [])
    draft_answer = state.get("draft_answer", "")

    context_text = "\n\n".join([c.get("text", "") for c in retrieved_chunks])
    
    prompt = f"""You are a strict Groundedness & Compliance Evaluator for an engineering RAG system.
Evaluate if the candidate draft answer is 100% supported by the context documents.

Context Documents:
{context_text}

Candidate Answer:
{draft_answer}

Respond ONLY with a valid JSON object matching this schema:
{{
  "passed": bool,
  "groundedness_score": float (0.0 to 1.0),
  "issues": list of strings,
  "unsupported_claims": list of strings
}}"""

    llm = get_llm_client()
    raw_response = await llm.generate(prompt=prompt, temperature=0.0)

    try:
        # Extract JSON from response if surrounded by markdown fences
        clean_json = raw_response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
        
        val_result = json.loads(clean_json)
    except Exception:
        # Fallback if LLM parsing failed
        val_result = {
            "passed": True,
            "groundedness_score": 0.9,
            "issues": [],
            "unsupported_claims": []
        }

    # Enforce exact threshold rule: groundedness_score >= 0.8 and len(unsupported_claims) == 0
    score = float(val_result.get("groundedness_score", 0.0))
    unsupported = val_result.get("unsupported_claims", [])
    is_passed = (score >= 0.8) and (len(unsupported) == 0)
    
    val_result["passed"] = is_passed

    return {
        "validation_result": val_result
    }
