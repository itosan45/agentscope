# AgentScope

AIエージェント監視ツール - LLMアプリケーションのトレース・可視化プラットフォーム

## 機能

- 🔍 **トレース収集**: OpenAI, LangChain等の自動計装
- 📊 **ダッシュボード**: リアルタイムでエージェント動作を可視化
- ⚡ **メトリクス**: レイテンシ、コスト、エラー率の追跡
- 🔔 **アラート**: Slack通知によるエラー検知

## クイックスタート

### 1. サーバー起動

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. SDK インストール

```bash
pip install agentscope-sdk
```

### 3. トレース開始

```python
from agentscope import trace, init

init(api_key="your-api-key", project="my-project")

@trace
def my_agent(query):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content
```

## プロジェクト構成

```
agentscope/
├── backend/     # FastAPI バックエンド
├── frontend/    # React ダッシュボード
└── sdk/         # Python SDK
```

## ライセンス

MIT
