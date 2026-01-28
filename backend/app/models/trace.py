"""
Database Models - Trace
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Span(SQLModel, table=True):
    """トレース内の個別操作（LLM呼び出し、ツール実行など）"""
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    trace_id: str = Field(foreign_key="trace.id", index=True)
    parent_span_id: Optional[str] = None
    
    name: str  # "llm_call", "tool_execution" など
    span_type: str  # "llm", "tool", "chain", "agent"
    
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    # LLM固有フィールド
    model: Optional[str] = None  # "gpt-4", "claude-3" など
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    
    # 入出力（JSON文字列として保存）
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    
    # エラー情報
    status: str = "running"  # "running", "success", "error"
    error_message: Optional[str] = None
    
    # リレーション
    trace: Optional["Trace"] = Relationship(back_populates="spans")


class Trace(SQLModel, table=True):
    """エージェント実行の1回分のトレース"""
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    project_id: str = Field(index=True)
    
    name: str  # "chat_completion", "agent_run" など
    
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    
    status: str = "running"  # "running", "success", "error"
    error_message: Optional[str] = None
    
    # 集計フィールド
    total_tokens: Optional[int] = None
    total_cost_usd: Optional[float] = None
    span_count: int = 0
    
    # メタデータ
    extra_metadata: Optional[str] = None  # JSON文字列
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーション
    spans: List[Span] = Relationship(back_populates="trace")


class Project(SQLModel, table=True):
    """プロジェクト（API Key単位）"""
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    name: str
    api_key: str = Field(default_factory=lambda: f"sk_{uuid.uuid4().hex[:16]}", unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Slack通知設定
    slack_webhook_url: Optional[str] = None
    alert_on_error: bool = True
