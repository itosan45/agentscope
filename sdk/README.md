# AgentScope Python SDK

AIエージェントのトレースと監視のためのPython SDK

## インストール

```bash
pip install agentscope-sdk
```

## クイックスタート

```python
from agentscope import init, trace

# 初期化
init(project_id="my-project")

# 関数をトレース
@trace
def my_agent(query: str) -> str:
    # あなたのエージェントコード
    response = call_llm(query)
    return response

# 実行
result = my_agent("Hello, world!")
```

## OpenAI自動計装

```python
from agentscope import init
from agentscope.integrations import patch_openai
import openai

init(project_id="my-project")
patch_openai()

# これ以降のOpenAI呼び出しは自動でトレースされる
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## コンテキストマネージャ

```python
from agentscope import start_trace

with start_trace("my_operation"):
    # このブロック内の操作がトレースされる
    do_something()
```
