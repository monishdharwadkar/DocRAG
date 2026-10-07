from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import health_router, chat_router
from app.db.session import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables automatically if needed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Enable CORS for local dev
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
