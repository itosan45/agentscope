"""
AgentScope API Client
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
import json

from agentscope.config import get_endpoint, get_project_id, is_enabled, get_api_key


class AgentScopeClient:
    """AgentScope APIクライアント"""
    
    def __init__(self, endpoint: Optional[str] = None, project_id: Optional[str] = None):
        self.endpoint = endpoint or get_endpoint()
        self.project_id = project_id or get_project_id()
        self._client = httpx.Client(timeout=10.0)
    
    def send_trace(self, trace_data: Dict[str, Any]) -> bool:
        """
        トレースをサーバーに送信
        
        Args:
            trace_data: トレースデータ
            
        Returns:
            送信成功したかどうか
        """
        if not is_enabled():
            return False
        
        try:
            response = self._client.post(
                f"{self.endpoint}/api/v1/traces",
                json=trace_data,
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": get_api_key()
                }
            )
            return response.status_code == 200
        except Exception as e:
            # エラーがあってもアプリケーションは止めない
            print(f"[AgentScope] Failed to send trace: {e}")
            return False
    
    def get_traces(self, limit: int = 50, status: Optional[str] = None) -> List[Dict]:
        """
        トレース一覧を取得
        """
        params = {
            "project_id": self.project_id,
            "limit": limit
        }
        if status:
            params["status"] = status
        
        try:
            response = self._client.get(
                f"{self.endpoint}/api/v1/traces",
                params=params
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[AgentScope] Failed to get traces: {e}")
        
        return []
    
    def get_metrics(self, period: str = "24h") -> Optional[Dict]:
        """
        メトリクスを取得
        """
        try:
            response = self._client.get(
                f"{self.endpoint}/api/v1/metrics",
                params={
                    "project_id": self.project_id,
                    "period": period
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[AgentScope] Failed to get metrics: {e}")
        
        return None
    
    def close(self):
        """クライアントを閉じる"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# シングルトンクライアント
_client: Optional[AgentScopeClient] = None


def get_client() -> AgentScopeClient:
    """グローバルクライアントを取得"""
    global _client
    if _client is None:
        _client = AgentScopeClient()
    return _client
