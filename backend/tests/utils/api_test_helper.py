"""
APIテスト用ヘルパー
@9統合テスト成功請負人が活用
"""

import asyncio
import json
from typing import Dict, Any, Optional
from httpx import AsyncClient

class APITestHelper:
    
    def __init__(self, base_url: str = "http://localhost:8432"):
        self.base_url = base_url
        self.client: Optional[AsyncClient] = None
    
    async def setup_client(self):
        """HTTPクライアント初期化"""
        self.client = AsyncClient(base_url=self.base_url)
    
    async def cleanup_client(self):
        """HTTPクライアント終了"""
        if self.client:
            await self.client.aclose()
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET リクエスト実行"""
        try:
            if not self.client:
                await self.setup_client()
            
            response = await self.client.get(endpoint, params=params)
            
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "json": None,
                "text": response.text
            }
            
            try:
                result["json"] = response.json()
            except json.JSONDecodeError:
                pass
            
            print(f"📤 GET {endpoint} -> {response.status_code}")
            return result
            
        except Exception as e:
            print(f"❌ GET {endpoint} エラー: {e}")
            raise
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST リクエスト実行"""
        try:
            if not self.client:
                await self.setup_client()
            
            response = await self.client.post(endpoint, json=data)
            
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "json": None,
                "text": response.text
            }
            
            try:
                result["json"] = response.json()
            except json.JSONDecodeError:
                pass
            
            print(f"📤 POST {endpoint} -> {response.status_code}")
            return result
            
        except Exception as e:
            print(f"❌ POST {endpoint} エラー: {e}")
            raise
    
    def assert_success_response(self, response: Dict[str, Any], expected_keys: list = None):
        """成功レスポンスのアサーション"""
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        assert response["json"] is not None, "Response should contain JSON"
        
        if expected_keys:
            for key in expected_keys:
                assert key in response["json"], f"Expected key '{key}' in response"
    
    def assert_error_response(self, response: Dict[str, Any], expected_status: int = 500):
        """エラーレスポンスのアサーション"""
        assert response["status_code"] == expected_status, f"Expected {expected_status}, got {response['status_code']}"