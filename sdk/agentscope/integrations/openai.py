"""
OpenAI Integration for AgentScope
Automatic instrumentation for OpenAI API calls
"""
from typing import Optional, Any
from functools import wraps
import time

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from agentscope.trace import _get_current_trace, SpanContext, add_span
from agentscope.config import is_enabled, get_config


# OpenAIの料金表（概算、2024年1月時点）
OPENAI_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """トークン数からコストを計算"""
    pricing = OPENAI_PRICING.get(model, {"input": 0.01, "output": 0.03})
    cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
    return round(cost, 6)


def patch_openai():
    """
    OpenAI APIを自動計装
    
    Example:
        >>> from agentscope.integrations.openai import patch_openai
        >>> patch_openai()
        >>> 
        >>> # これ以降のOpenAI呼び出しは自動でトレースされる
        >>> response = openai.chat.completions.create(...)
    """
    if not HAS_OPENAI:
        print("[AgentScope] OpenAI not installed, skipping patch")
        return
    
    _patch_chat_completions()
    
    config = get_config()
    if config.get("debug"):
        print("[AgentScope] OpenAI patched successfully")


def _patch_chat_completions():
    """Chat Completions APIをパッチ"""
    if not HAS_OPENAI:
        return
    
    original_create = openai.resources.chat.Completions.create
    
    @wraps(original_create)
    def patched_create(self, *args, **kwargs):
        if not is_enabled():
            return original_create(self, *args, **kwargs)
        
        start_time = time.time()
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        
        try:
            response = original_create(self, *args, **kwargs)
            
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            
            # トークン数を取得
            usage = getattr(response, 'usage', None)
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None
            
            # コストを計算
            cost = None
            if input_tokens and output_tokens:
                cost = calculate_cost(model, input_tokens, output_tokens)
            
            # 出力を取得
            output_content = None
            if response.choices:
                output_content = response.choices[0].message.content
            
            # スパンを追加
            add_span(
                name="openai.chat.completions.create",
                span_type="llm",
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                input_data={"messages": [{"role": m.get("role"), "content": m.get("content", "")[:200]} for m in messages[:3]]},
                output_data={"content": output_content[:500] if output_content else None},
                duration_ms=duration_ms
            )
            
            return response
            
        except Exception as e:
            add_span(
                name="openai.chat.completions.create",
                span_type="llm",
                model=model,
                input_data={"messages": [{"role": m.get("role")} for m in messages[:3]]},
                output_data={"error": str(e)}
            )
            raise
    
    openai.resources.chat.Completions.create = patched_create
