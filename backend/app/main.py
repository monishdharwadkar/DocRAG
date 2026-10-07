import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health_router, chat_router
from app.db.session import engine, Base
from app.vectorstore.qdrant_client import get_qdrant_store
from ingestion.ingest import run_ingestion

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables automatically if needed
    if engine is not None:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"[Lifespan DB Warning] {e}")

    # Auto-seed sample engineering docs into vector store if empty
    try:
        possible_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs_sample")),
            os.path.abspath("docs_sample"),
            "/var/task/docs_sample"
        ]
        for sample_dir in possible_paths:
            if os.path.exists(sample_dir):
                run_ingestion(sample_dir)
                break
    except Exception as e:
        print(f"[Lifespan Ingestion Warning] {e}")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to DocRAG API"}
