import math
import random
from app.config import settings

class Embedder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None
        self.vector_dim = 1024

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                self._model = "mock"
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        if model != "mock":
            embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            return embeddings.tolist()
        
        # Pure Python deterministic vector generator (no numpy required)
        vectors = []
        for text in texts:
            seed = sum(ord(c) for c in text) % 100000
            rng = random.Random(seed)
            raw_vec = [rng.gauss(0, 1) for _ in range(self.vector_dim)]
            norm = math.sqrt(sum(x * x for x in raw_vec)) + 1e-9
            normalized = [x / norm for x in raw_vec]
            vectors.append(normalized)
        return vectors

_embedder_instance = None

def get_embedder() -> Embedder:
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance
