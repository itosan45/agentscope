"""
AgentScope Configuration
"""
from typing import Optional
import os

# グローバル設定
_config = {
    "api_key": None,
    "project_id": None,
    "endpoint": "http://localhost:8000",
    "enabled": True,
    "debug": False
}


def init(
    api_key: Optional[str] = None,
    project_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    enabled: bool = True,
    debug: bool = False
):
    """
    AgentScopeを初期化
    
    Args:
        api_key: APIキー（環境変数 AGENTSCOPE_API_KEY からも取得可能）
        project_id: プロジェクトID（環境変数 AGENTSCOPE_PROJECT_ID からも取得可能）
        endpoint: AgentScopeサーバーのURL
        enabled: トレースを有効化するか
        debug: デバッグモード
    
    Example:
        >>> from agentscope import init
        >>> init(project_id="my-project")
    """
    _config["api_key"] = api_key or os.getenv("AGENTSCOPE_API_KEY")
    _config["project_id"] = project_id or os.getenv("AGENTSCOPE_PROJECT_ID", "default")
    _config["endpoint"] = endpoint or os.getenv("AGENTSCOPE_ENDPOINT", "http://localhost:8000")
    _config["enabled"] = enabled
    _config["debug"] = debug
    
    if _config["debug"]:
        print(f"[AgentScope] Initialized with project_id={_config['project_id']}, endpoint={_config['endpoint']}")


def get_config():
    """現在の設定を取得"""
    return _config.copy()


def is_enabled() -> bool:
    """トレースが有効かどうか"""
    return _config["enabled"]


def get_project_id() -> str:
    """プロジェクトIDを取得"""
    return _config["project_id"] or "default"


def get_endpoint() -> str:
    """エンドポイントを取得"""
    return _config["endpoint"]
