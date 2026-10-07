# DocRAG Architectural Decisions & Assumptions

## Architecture Overview
DocRAG is a self-healing multi-agent RAG system for internal engineering documentation built with FastAPI, LangGraph, Qdrant, PostgreSQL, Redis, and React + TypeScript + Tailwind.

## Key Decisions & Assumptions
1. **LLM Client & Mocking**: Uses `openai.AsyncOpenAI` targeting a vLLM OpenAI-compatible endpoint. Defaults to `USE_MOCK_LLM=true` when running without a GPU. The mock client returns deterministic context-grounded responses and structured JSON validation payloads.
2. **Embeddings**: `BAAI/bge-large-en-v1.5` produces 1024-dimensional vectors. Run via local `sentence-transformers`.
3. **Vector DB**: Qdrant collection named `docrag_docs` with Cosine distance, payload indexing on `source_path` and `heading`.
4. **Relational DB**: Async PostgreSQL via `sqlalchemy.ext.asyncio` and `asyncpg`. Stores chat sessions, chat messages, and node execution agent traces.
5. **Agent Orchestration**: LangGraph graph with 4 nodes: `retrieve`, `generate`, `validate`, and `correct`. Groundedness threshold is 0.8 with max 2 retry attempts before low-confidence escalation.
6. **Streaming & API**: WebSocket `/api/chat/ws` for real-time trace updates and token streaming, plus REST `/api/chat` for simple non-agentic baseline or REST integration.
