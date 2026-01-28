"""
AgentScope Backend
AI Agent monitoring and observability platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import traces, metrics
from app.db.database import create_db_and_tables

app = FastAPI(
    title="AgentScope API",
    description="AI Agent Tracing and Monitoring Platform",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """サーバー起動時にDBテーブルを作成"""
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "AgentScope API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ルーター登録
app.include_router(traces.router, prefix="/api/v1", tags=["traces"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
