"""
AgentScope Tracing
Core tracing functionality with @trace decorator
"""
from typing import Optional, Callable, Any, Dict, List
from datetime import datetime, timezone
from functools import wraps
from contextlib import contextmanager
import uuid
import time
import json
import threading
import atexit

from agentscope.config import get_project_id, is_enabled, get_config
from agentscope.client import get_client


# スレッドローカルでトレースコンテキストを管理
_trace_context = threading.local()


def _get_current_trace() -> Optional[Dict]:
    """現在のトレースを取得"""
    return getattr(_trace_context, 'current_trace', None)


def _set_current_trace(trace: Optional[Dict]):
    """現在のトレースを設定"""
    _trace_context.current_trace = trace


def _get_current_span() -> Optional[Dict]:
    """現在のスパンを取得"""
    return getattr(_trace_context, 'current_span', None)


def _set_current_span(span: Optional[Dict]):
    """現在のスパンを設定"""
    _trace_context.current_span = span


class TraceContext:
    """トレースコンテキストを管理するクラス"""
    
    def __init__(self, name: str, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.name = name
        self.start_time = datetime.now(timezone.utc)
        self.spans: List[Dict] = []
        self.status = "running"
        self.error_message = None
        self.metadata = {}
    
    def add_span(self, span: Dict):
        """スパンを追加"""
        self.spans.append(span)
    
    def finish(self, status: str = "success", error_message: Optional[str] = None):
        """トレースを終了"""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
        self.status = status
        self.error_message = error_message
    
    def to_dict(self) -> Dict:
        """辞書に変換"""
        return {
            "id": self.trace_id,
            "project_id": get_project_id(),
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": getattr(self, 'end_time', datetime.now(timezone.utc)).isoformat(),
            "duration_ms": getattr(self, 'duration_ms', None),
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata if self.metadata else None,
            "spans": self.spans
        }


class SpanContext:
    """スパンコンテキストを管理するクラス"""
    
    def __init__(
        self,
        name: str,
        span_type: str = "function",
        parent_span_id: Optional[str] = None
    ):
        self.span_id = str(uuid.uuid4())
        self.name = name
        self.span_type = span_type
        self.parent_span_id = parent_span_id
        self.start_time = datetime.now(timezone.utc)
        self.model = None
        self.input_tokens = None
        self.output_tokens = None
        self.cost_usd = None
        self.input_data = None
        self.output_data = None
        self.status = "running"
        self.error_message = None
    
    def set_llm_info(
        self,
        model: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None
    ):
        """LLM情報を設定"""
        self.span_type = "llm"
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cost_usd = cost_usd
    
    def set_input(self, data: Any):
        """入力データを設定"""
        try:
            self.input_data = data if isinstance(data, dict) else {"value": str(data)[:1000]}
        except:
            self.input_data = None
    
    def set_output(self, data: Any):
        """出力データを設定"""
        try:
            self.output_data = data if isinstance(data, dict) else {"value": str(data)[:1000]}
        except:
            self.output_data = None
    
    def finish(self, status: str = "success", error_message: Optional[str] = None):
        """スパンを終了"""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
        self.status = status
        self.error_message = error_message
    
    def to_dict(self) -> Dict:
        """辞書に変換"""
        return {
            "id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "span_type": self.span_type,
            "start_time": self.start_time.isoformat(),
            "end_time": getattr(self, 'end_time', datetime.now(timezone.utc)).isoformat(),
            "duration_ms": getattr(self, 'duration_ms', None),
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
            "error_message": self.error_message
        }


def trace(
    name: Optional[str] = None,
    span_type: str = "function"
) -> Callable:
    """
    関数をトレースするデコレータ
    
    Args:
        name: トレース/スパンの名前（デフォルトは関数名）
        span_type: スパンのタイプ（"function", "llm", "tool", "agent"）
    
    Example:
        >>> @trace
        ... def my_function(x):
        ...     return x * 2
        
        >>> @trace("custom_name", span_type="agent")
        ... def my_agent(query):
        ...     return process(query)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_enabled():
                return func(*args, **kwargs)
            
            trace_name = name or func.__name__
            current_trace = _get_current_trace()
            parent_span = _get_current_span()
            
            # 新しいトレースを開始するか、既存のトレースにスパンを追加
            if current_trace is None:
                # 新しいトレースを開始
                trace_ctx = TraceContext(name=trace_name)
                _set_current_trace(trace_ctx)
                is_root_trace = True
            else:
                trace_ctx = current_trace
                is_root_trace = False
            
            # スパンを作成
            span_ctx = SpanContext(
                name=trace_name,
                span_type=span_type,
                parent_span_id=parent_span.span_id if parent_span else None
            )
            
            # 入力を記録
            try:
                if args:
                    span_ctx.set_input({"args": [str(a)[:500] for a in args]})
                if kwargs:
                    span_ctx.set_input({"kwargs": {k: str(v)[:500] for k, v in kwargs.items()}})
            except:
                pass
            
            _set_current_span(span_ctx)
            
            try:
                result = func(*args, **kwargs)
                
                # 出力を記録
                try:
                    span_ctx.set_output({"result": str(result)[:1000]})
                except:
                    pass
                
                span_ctx.finish(status="success")
                return result
                
            except Exception as e:
                span_ctx.finish(status="error", error_message=str(e))
                raise
                
            finally:
                # スパンをトレースに追加
                trace_ctx.add_span(span_ctx.to_dict())
                
                # 親スパンに戻す
                _set_current_span(parent_span)
                
                # ルートトレースの場合は送信
                if is_root_trace:
                    trace_ctx.finish(status=span_ctx.status, error_message=span_ctx.error_message)
                    _send_trace(trace_ctx)
                    _set_current_trace(None)
        
        return wrapper
    
    # @trace と @trace() の両方をサポート
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator


@contextmanager
def start_trace(name: str):
    """
    トレースをコンテキストマネージャとして開始
    
    Example:
        >>> with start_trace("my_operation"):
        ...     do_something()
    """
    if not is_enabled():
        yield
        return
    
    trace_ctx = TraceContext(name=name)
    _set_current_trace(trace_ctx)
    
    try:
        yield trace_ctx
        trace_ctx.finish(status="success")
    except Exception as e:
        trace_ctx.finish(status="error", error_message=str(e))
        raise
    finally:
        _send_trace(trace_ctx)
        _set_current_trace(None)


def end_trace():
    """現在のトレースを終了して送信"""
    trace_ctx = _get_current_trace()
    if trace_ctx:
        trace_ctx.finish(status="success")
        _send_trace(trace_ctx)
        _set_current_trace(None)


def add_span(
    name: str,
    span_type: str = "custom",
    model: Optional[str] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    cost_usd: Optional[float] = None,
    input_data: Optional[Dict] = None,
    output_data: Optional[Dict] = None,
    duration_ms: Optional[int] = None
):
    """
    現在のトレースにスパンを手動で追加
    
    Example:
        >>> add_span(
        ...     name="openai_call",
        ...     span_type="llm",
        ...     model="gpt-4",
        ...     input_tokens=100,
        ...     output_tokens=50
        ... )
    """
    trace_ctx = _get_current_trace()
    if not trace_ctx:
        return
    
    parent_span = _get_current_span()
    span = SpanContext(
        name=name,
        span_type=span_type,
        parent_span_id=parent_span.span_id if parent_span else None
    )
    
    if model:
        span.set_llm_info(model, input_tokens, output_tokens, cost_usd)
    if input_data:
        span.set_input(input_data)
    if output_data:
        span.set_output(output_data)
    
    span.finish(status="success")
    if duration_ms:
        span.duration_ms = duration_ms
    
    trace_ctx.add_span(span.to_dict())


def _send_trace(trace_ctx: TraceContext):
    """トレースをサーバーに送信"""
    if not is_enabled():
        return
    
    config = get_config()
    if config.get("debug"):
        print(f"[AgentScope] Sending trace: {trace_ctx.name}")
        print(f"  Spans: {len(trace_ctx.spans)}")
        print(f"  Duration: {getattr(trace_ctx, 'duration_ms', 'N/A')}ms")
    
    try:
        client = get_client()
        client.send_trace(trace_ctx.to_dict())
    except Exception as e:
        if config.get("debug"):
            print(f"[AgentScope] Failed to send trace: {e}")
