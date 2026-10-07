import json
import asyncio
from app.config import settings

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    AsyncOpenAI = None

class LLMClient:
    def __init__(self):
        self.use_mock = settings.USE_MOCK_LLM or not HAS_OPENAI
        if not self.use_mock and HAS_OPENAI:
            self.client = AsyncOpenAI(
                base_url=settings.LLM_BASE_URL,
                api_key=settings.LLM_API_KEY
            )
            self.model = settings.LLM_MODEL
        else:
            self.client = None
            self.model = "mock-qwen3-8b"

    async def generate(self, prompt: str, temperature: float = 0.2, response_format: dict = None) -> str:
        if self.use_mock or self.client is None:
            return await self._mock_generate(prompt)
        
        try:
            kwargs = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLMClient Error] vLLM request failed: {e}. Falling back to mock output.")
            return await self._mock_generate(prompt)

    async def _mock_generate(self, prompt: str) -> str:
        await asyncio.sleep(0.01)
        
        # Check if the prompt is asking for validation / structured evaluation output
        if "groundedness_score" in prompt or "validation" in prompt.lower() or "unsupported_claims" in prompt:
            if "[FORCE_FAIL]" in prompt or "unsupported_claim_test" in prompt:
                return json.dumps({
                    "passed": False,
                    "groundedness_score": 0.4,
                    "issues": ["Contains ungrounded statement regarding non-existent cluster parameter."],
                    "unsupported_claims": ["The HPA automatically provisions hardware nodes."]
                })
            return json.dumps({
                "passed": True,
                "groundedness_score": 0.95,
                "issues": [],
                "unsupported_claims": []
            })
        
        # Check if prompt is a question rewriting task (retrieval agent)
        if "condense follow-up" in prompt.lower() or "standalone question" in prompt.lower():
            lines = [l.strip() for l in prompt.split("\n") if l.strip()]
            return lines[-1] if lines else "What is the engineering procedure?"

        # Default mock response generator based on context in prompt
        if "Context:" in prompt or "context" in prompt.lower():
            sources = []
            if "[Source: " in prompt:
                import re
                matches = re.findall(r'\[Source:\s*([^\]]+)\]', prompt)
                sources = list(set(matches))
            
            citation_str = f" [Source: {sources[0]}]" if sources else " [Source: docs_sample/k8s_hpa_runbook.md#HPA Configuration]"
            
            if "correction" in prompt.lower() or "previously flagged" in prompt.lower():
                return f"Based strictly on the verified documentation, here is the corrected response.{citation_str} All metrics and procedures follow the documented standard guidelines."

            return f"According to the internal engineering documentation, the system follows standard operating procedures.{citation_str} Ensure all health checks and configurations match the deployment specification."
        
        return "DocRAG standard mock response: The requested engineering documentation specifies standard system operations and guidelines."

_llm_client = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
