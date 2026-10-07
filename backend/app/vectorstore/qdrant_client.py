import math
from app.config import settings

# Attempt to import real QdrantClient; fallback to in-memory MockQdrantClient if package not installed
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    HAS_QDRANT_CLIENT = True
except ImportError:
    HAS_QDRANT_CLIENT = False

class MockQdrantPoint:
    def __init__(self, id, vector, payload):
        self.id = id
        self.vector = vector
        self.payload = payload
        self.score = 0.0

class MockQdrantClient:
    """Pure Python in-memory Qdrant client fallback."""
    def __init__(self):
        self.storage = {}

    def get_collections(self):
        class CollectionsHolder:
            collections = []
        return CollectionsHolder()

    def create_collection(self, collection_name: str, vectors_config: any):
        if collection_name not in self.storage:
            self.storage[collection_name] = []

    def upsert(self, collection_name: str, points: list):
        if collection_name not in self.storage:
            self.storage[collection_name] = []
        
        existing_ids = {p.id: idx for idx, p in enumerate(self.storage[collection_name])}
        for point in points:
            if point.id in existing_ids:
                self.storage[collection_name][existing_ids[point.id]] = point
            else:
                self.storage[collection_name].append(point)

    def search(self, collection_name: str, query_vector: list, limit: int = 5):
        points = self.storage.get(collection_name, [])
        if not points:
            return []
        
        q_norm = math.sqrt(sum(a * a for a in query_vector)) + 1e-9

        scored_points = []
        for p in points:
            dot = sum(a * b for a, b in zip(query_vector, p.vector))
            p_norm = math.sqrt(sum(b * b for b in p.vector)) + 1e-9
            score = dot / (q_norm * p_norm)
            
            res_point = MockQdrantPoint(p.id, p.vector, p.payload)
            res_point.score = float(score)
            scored_points.append(res_point)
        
        scored_points.sort(key=lambda x: x.score, reverse=True)
        return scored_points[:limit]

class QdrantVectorStore:
    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        self.host = host or settings.QDRANT_HOST
        self.port = port or settings.QDRANT_PORT
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        
        if HAS_QDRANT_CLIENT:
            try:
                self.client = QdrantClient(host=self.host, port=self.port, timeout=5.0)
                self._ensure_collection()
            except Exception:
                self.client = MockQdrantClient()
                self._ensure_collection()
        else:
            self.client = MockQdrantClient()
            self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                if HAS_QDRANT_CLIENT and not isinstance(self.client, MockQdrantClient):
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=qmodels.VectorParams(
                            size=1024,
                            distance=qmodels.Distance.COSINE
                        )
                    )
                else:
                    self.client.create_collection(self.collection_name, None)
        except Exception:
            pass

    def upsert_chunks(self, ids: list[str], vectors: list[list[float]], payloads: list[dict]):
        if HAS_QDRANT_CLIENT and not isinstance(self.client, MockQdrantClient):
            points = [
                qmodels.PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
                for i in range(len(ids))
            ]
        else:
            points = [
                MockQdrantPoint(id=ids[i], vector=vectors[i], payload=payloads[i])
                for i in range(len(ids))
            ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        chunks = []
        for res in results:
            chunk_data = dict(res.payload)
            chunk_data["score"] = getattr(res, "score", 0.9)
            chunks.append(chunk_data)
        return chunks

_qdrant_store = None

def get_qdrant_store() -> QdrantVectorStore:
    global _qdrant_store
    if _qdrant_store is None:
        _qdrant_store = QdrantVectorStore()
    return _qdrant_store
