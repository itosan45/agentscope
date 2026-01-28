"""
Metrics API endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from pydantic import BaseModel

from app.db.database import get_session
from app.models.trace import Trace, Span

router = APIRouter()


class MetricsResponse(BaseModel):
    """メトリクス集計結果"""
    period_start: datetime
    period_end: datetime
    
    # トレース統計
    total_traces: int
    success_count: int
    error_count: int
    error_rate: float
    
    # パフォーマンス
    avg_duration_ms: Optional[float]
    p50_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    
    # コスト
    total_tokens: int
    total_cost_usd: float
    
    # スパン統計
    total_spans: int
    avg_spans_per_trace: float


class ModelUsageResponse(BaseModel):
    """モデル別使用状況"""
    model: str
    call_count: int
    total_tokens: int
    total_cost_usd: float
    avg_duration_ms: float


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    project_id: str = Query(..., description="プロジェクトID"),
    period: str = Query("24h", description="期間 (1h, 24h, 7d, 30d)"),
    session: Session = Depends(get_session)
):
    """メトリクスを取得"""
    # 期間を計算
    now = datetime.utcnow()
    period_map = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    delta = period_map.get(period, timedelta(hours=24))
    period_start = now - delta
    
    # トレース統計を取得
    traces_query = select(Trace).where(
        Trace.project_id == project_id,
        Trace.created_at >= period_start
    )
    traces = session.exec(traces_query).all()
    
    total_traces = len(traces)
    success_count = sum(1 for t in traces if t.status == "success")
    error_count = sum(1 for t in traces if t.status == "error")
    error_rate = (error_count / total_traces * 100) if total_traces > 0 else 0.0
    
    # パフォーマンス計算
    durations = [t.duration_ms for t in traces if t.duration_ms is not None]
    avg_duration = sum(durations) / len(durations) if durations else None
    
    # パーセンタイル計算
    sorted_durations = sorted(durations) if durations else []
    p50 = sorted_durations[len(sorted_durations) // 2] if sorted_durations else None
    p95_idx = int(len(sorted_durations) * 0.95)
    p95 = sorted_durations[p95_idx] if sorted_durations and p95_idx < len(sorted_durations) else None
    
    # コスト集計
    total_tokens = sum(t.total_tokens or 0 for t in traces)
    total_cost = sum(t.total_cost_usd or 0 for t in traces)
    
    # スパン統計
    total_spans = sum(t.span_count for t in traces)
    avg_spans = total_spans / total_traces if total_traces > 0 else 0.0
    
    return MetricsResponse(
        period_start=period_start,
        period_end=now,
        total_traces=total_traces,
        success_count=success_count,
        error_count=error_count,
        error_rate=round(error_rate, 2),
        avg_duration_ms=round(avg_duration, 2) if avg_duration else None,
        p50_duration_ms=p50,
        p95_duration_ms=p95,
        total_tokens=total_tokens,
        total_cost_usd=round(total_cost, 4),
        total_spans=total_spans,
        avg_spans_per_trace=round(avg_spans, 2)
    )


@router.get("/metrics/models", response_model=list[ModelUsageResponse])
async def get_model_usage(
    project_id: str = Query(..., description="プロジェクトID"),
    period: str = Query("24h", description="期間"),
    session: Session = Depends(get_session)
):
    """モデル別使用状況を取得"""
    now = datetime.utcnow()
    period_map = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    delta = period_map.get(period, timedelta(hours=24))
    period_start = now - delta
    
    # LLMスパンを取得
    spans_query = select(Span).join(Trace).where(
        Trace.project_id == project_id,
        Trace.created_at >= period_start,
        Span.span_type == "llm",
        Span.model != None
    )
    spans = session.exec(spans_query).all()
    
    # モデル別に集計
    model_stats = {}
    for span in spans:
        model = span.model
        if model not in model_stats:
            model_stats[model] = {
                "call_count": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "durations": []
            }
        
        stats = model_stats[model]
        stats["call_count"] += 1
        stats["total_tokens"] += (span.input_tokens or 0) + (span.output_tokens or 0)
        stats["total_cost"] += span.cost_usd or 0
        if span.duration_ms:
            stats["durations"].append(span.duration_ms)
    
    # レスポンス構築
    result = []
    for model, stats in model_stats.items():
        avg_duration = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else 0
        result.append(ModelUsageResponse(
            model=model,
            call_count=stats["call_count"],
            total_tokens=stats["total_tokens"],
            total_cost_usd=round(stats["total_cost"], 4),
            avg_duration_ms=round(avg_duration, 2)
        ))
    
    return sorted(result, key=lambda x: x.call_count, reverse=True)
