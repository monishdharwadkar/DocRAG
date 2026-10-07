# DocRAG Vercel Deployment Guide

Hosting a multi-agent RAG chatbot system like DocRAG on Vercel requires understanding the distinction between Vercel's frontend edge platform and backend service requirements.

---

## Architecture Breakdown

| Component | Vercel Compatibility | Recommended Hosting |
| :--- | :--- | :--- |
| **Frontend (React + Vite)** | 🟢 100% Native & Ideal | **Vercel** |
| **Backend (FastAPI + LangGraph)** | 🟡 Serverless via `vercel.json` (max 60s timeout) | **Render / Railway / Fly.io** |
| **WebSockets (`/api/chat/ws`)** | 🔴 Not supported in Vercel Serverless | **Render / Railway / Fly.io / AWS** |
| **Vector DB (Qdrant)** | 🔴 Requires Cloud Service | **Qdrant Cloud (Free Tier)** |
| **Database (Postgres & Redis)** | 🔴 Requires Cloud Service | **Neon Postgres / Upstash Redis** |

---

## Option 1: Recommended Hybrid Architecture (Vercel Frontend + Render/Railway Backend)

This is the **gold standard** for deploying DocRAG. It provides instant global CDN delivery for the frontend while allowing full WebSocket streaming, background agent execution, and containerized database access.

### Step 1: Deploy Backend & DBs to Render / Railway / Fly.io
1. **Database & Vector DB**:
   - Create a free Qdrant cluster on [Qdrant Cloud](https://cloud.qdrant.io).
   - Create a Postgres DB on [Neon.tech](https://neon.tech) or Render Postgres.
2. **Backend Service**:
   - Push code to GitHub.
   - On Render / Railway, create a **Web Service** from `backend/Dockerfile`.
   - Set Environment Variables:
     ```env
     QDRANT_HOST=your-cluster.qdrant.tech
     QDRANT_PORT=6333
     DATABASE_URL=postgresql+asyncpg://user:pass@ep-xyz.neon.tech/docrag
     USE_MOCK_LLM=true  # or set LLM_BASE_URL to OpenAI/vLLM endpoint
     ```
   - Note down your deployed backend URL (e.g., `https://docrag-backend.onrender.com`).

### Step 2: Deploy Frontend to Vercel
1. Update `vercel.json` in project root with your backend destination URL:
   ```json
   {
     "buildCommand": "cd frontend && npm install && npm run build",
     "outputDirectory": "frontend/dist",
     "framework": "vite",
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://docrag-backend.onrender.com/api/:path*"
       }
     ]
   }
   ```
2. Import the Git repository in [Vercel Dashboard](https://vercel.com/new).
3. Set **Root Directory** to `./` (or leave default).
4. Click **Deploy**.

---

## Option 2: Full Serverless Deployment on Vercel

If you want the entire app hosted on Vercel:

### 1. External Cloud Managed Databases Required
- **Qdrant Cloud**: [https://cloud.qdrant.io](https://cloud.qdrant.io) (Free 1GB cluster)
- **Neon Postgres**: [https://neon.tech](https://neon.tech) (Free serverless Postgres)
- **Upstash Redis**: [https://upstash.com](https://upstash.com) (Serverless Redis)
- **LLM Endpoint**: OpenAI API (`https://api.openai.com/v1`) or hosted vLLM (Groq / Together AI)

### 2. Vercel Serverless Function Configuration
Create `api/index.py` at repository root to serve FastAPI serverlessly:

```python
from backend.app.main import app

# Vercel serverless entry point
```

And set `vercel.json`:
```json
{
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" },
    { "src": "frontend/package.json", "use": "@vercel/static-build" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```

> **Note on WebSockets**: Standard HTTP REST `/api/chat` endpoints work seamlessly on Vercel Serverless. For streaming on Vercel, switch from WebSocket to Server-Sent Events (SSE).
