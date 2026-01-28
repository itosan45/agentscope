"""
Traces API endpoints
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlmodel import Session, select
import json
import uuid

from app.db.database import get_session
from app.models.trace import Trace, Span, Project
from pydantic import BaseModel

router = APIRouter()


async def verify_api_key(
    project_id: str,
    api_key: str,
    session: Session
):
    """プロジェクトIDとAPIキーの整合性を検証"""
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).first()
    
    if not project:
        # プロジェクトが存在しない場合は自動作成（開発者の利便性のため）
        new_project = Project(id=project_id, name=project_id, api_key=api_key)
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        project = new_project
        
    if project.api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return project


# ===== Request/Response Schemas =====

class SpanCreate(BaseModel):
    id: str
    parent_span_id: Optional[str] = None
    name: str
    span_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    status: str = "success"
    error_message: Optional[str] = None


class TraceCreate(BaseModel):
    id: str
    project_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None
    extra_metadata: Optional[dict] = None
    spans: List[SpanCreate] = []


class SpanResponse(BaseModel):
    id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    span_type: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    model: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    cost_usd: Optional[float]
    input_data: Optional[dict]
    output_data: Optional[dict]
    status: str
    error_message: Optional[str]


class TraceResponse(BaseModel):
    id: str
    project_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: str
    error_message: Optional[str]
    total_tokens: Optional[int]
    total_cost_usd: Optional[float]
    span_count: int
    created_at: datetime


class TraceDetailResponse(TraceResponse):
    spans: List[SpanResponse]
    metadata: Optional[dict]


# ===== API Endpoints =====

@router.post("/traces", response_model=TraceResponse)
async def create_trace(
    trace_data: TraceCreate, 
    session: Session = Depends(get_session),
    x_api_key: str = Header(...)
):
    # APIキーの検証
    await verify_api_key(trace_data.project_id, x_api_key, session)
    """新しいトレースを作成"""
    # トレースを作成
    trace = Trace(
        id=trace_data.id,
        project_id=trace_data.project_id,
        name=trace_data.name,
        start_time=trace_data.start_time,
        end_time=trace_data.end_time,
        duration_ms=trace_data.duration_ms,
        status=trace_data.status,
        error_message=trace_data.error_message,
        extra_metadata=json.dumps(trace_data.extra_metadata) if trace_data.extra_metadata else None,
        span_count=len(trace_data.spans)
    )
    
    # 集計値を計算
    total_tokens = 0
    total_cost = 0.0
    
    for span_data in trace_data.spans:
        span = Span(
            id=span_data.id,
            trace_id=trace.id,
            parent_span_id=span_data.parent_span_id,
            name=span_data.name,
            span_type=span_data.span_type,
            start_time=span_data.start_time,
            end_time=span_data.end_time,
            duration_ms=span_data.duration_ms,
            model=span_data.model,
            input_tokens=span_data.input_tokens,
            output_tokens=span_data.output_tokens,
            cost_usd=span_data.cost_usd,
            input_data=json.dumps(span_data.input_data) if span_data.input_data else None,
            output_data=json.dumps(span_data.output_data) if span_data.output_data else None,
            status=span_data.status,
            error_message=span_data.error_message
        )
        session.add(span)
        
        if span_data.input_tokens:
            total_tokens += span_data.input_tokens
        if span_data.output_tokens:
            total_tokens += span_data.output_tokens
        if span_data.cost_usd:
            total_cost += span_data.cost_usd
    
    trace.total_tokens = total_tokens if total_tokens > 0 else None
    trace.total_cost_usd = total_cost if total_cost > 0 else None
    
    session.add(trace)
    session.commit()
    session.refresh(trace)
    
    return trace


@router.get("/traces", response_model=List[TraceResponse])
async def list_traces(
    project_id: str = Query(..., description="プロジェクトID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="ステータスでフィルタ"),
    session: Session = Depends(get_session),
    # project: Project = Depends(verify_api_key) # フロントエンドからの取得は一旦パススルーか、別の認証にするが、MVPでは簡易化
):
    """トレース一覧を取得"""
    query = select(Trace).where(Trace.project_id == project_id)
    
    if status:
        query = query.where(Trace.status == status)
    
    query = query.order_by(Trace.created_at.desc()).offset(offset).limit(limit)
    traces = session.exec(query).all()
    
    return traces


@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
async def get_trace(
    trace_id: str,
    session: Session = Depends(get_session),
    # project: Project = Depends(verify_api_key) # フロントエンドからの取得は一旦パススルーか、別の認証にするが、MVPでは簡易化
):
    """トレース詳細を取得（スパン含む）"""
    trace = session.get(Trace, trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    # スパンを取得
    spans_query = select(Span).where(Span.trace_id == trace_id).order_by(Span.start_time)
    spans = session.exec(spans_query).all()
    
    # レスポンス構築
    spans_response = []
    for span in spans:
        spans_response.append(SpanResponse(
            id=span.id,
            trace_id=span.trace_id,
            parent_span_id=span.parent_span_id,
            name=span.name,
            span_type=span.span_type,
            start_time=span.start_time,
            end_time=span.end_time,
            duration_ms=span.duration_ms,
            model=span.model,
            input_tokens=span.input_tokens,
            output_tokens=span.output_tokens,
            cost_usd=span.cost_usd,
            input_data=json.loads(span.input_data) if span.input_data else None,
            output_data=json.loads(span.output_data) if span.output_data else None,
            status=span.status,
            error_message=span.error_message
        ))
    
    return TraceDetailResponse(
        id=trace.id,
        project_id=trace.project_id,
        name=trace.name,
        start_time=trace.start_time,
        end_time=trace.end_time,
        duration_ms=trace.duration_ms,
        status=trace.status,
        error_message=trace.error_message,
        total_tokens=trace.total_tokens,
        total_cost_usd=trace.total_cost_usd,
        span_count=trace.span_count,
        created_at=trace.created_at,
        spans=spans_response,
        extra_metadata=json.loads(trace.extra_metadata) if trace.extra_metadata else None
    )
