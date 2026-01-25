"""
LINE通知設定API統合テスト
実データを使用したテスト（モック禁止）
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime

# FastAPIアプリケーションのインポート
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.main import app
from src.database.config import database, connect_db, disconnect_db


@pytest.fixture(scope="module")
def event_loop():
    """イベントループのフィクスチャ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    """データベース接続のセットアップ"""
    await connect_db()
    yield
    await disconnect_db()


@pytest.mark.asyncio
async def test_get_line_notification_config_success():
    """
    LINE通知設定取得API - 正常系テスト

    シナリオ:
    1. GET /api/notifications/line を呼び出す
    2. レスポンスが200で返ってくることを確認
    3. レスポンスの構造が正しいことを確認
    4. トークンがマスキングされていることを確認
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # API呼び出し
        response = await client.get("/api/notifications/line")

        # ステータスコード確認
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # レスポンスボディ確認
        data = response.json()

        # 必須フィールドの存在確認（キャメルケース）
        assert "isConnected" in data, "isConnected field is missing"
        assert "token" in data, "token field is missing"
        assert "status" in data, "status field is missing"

        # 型の確認
        assert isinstance(data["isConnected"], bool), "isConnected must be boolean"
        assert isinstance(data["token"], str), "token must be string"
        assert isinstance(data["status"], str), "status must be string"

        # ステータスの値が正しいことを確認
        valid_statuses = ["connected", "disconnected", "error"]
        assert data["status"] in valid_statuses, f"Invalid status: {data['status']}"

        # トークンがマスキングされていることを確認
        if data["token"]:
            assert "***masked***" in data["token"] or data["token"] == "", \
                "Token must be masked or empty"

        # オプショナルフィールドの型確認（キャメルケース）
        if "lastNotificationAt" in data and data["lastNotificationAt"] is not None:
            assert isinstance(data["lastNotificationAt"], str), \
                "lastNotificationAt must be string (ISO format)"

        if "notificationCount" in data and data["notificationCount"] is not None:
            assert isinstance(data["notificationCount"], int), \
                "notificationCount must be integer"

        if "errorCount" in data and data["errorCount"] is not None:
            assert isinstance(data["errorCount"], int), \
                "errorCount must be integer"

        print(f"✅ LINE通知設定取得APIテスト成功")
        print(f"   - isConnected: {data['isConnected']}")
        print(f"   - status: {data['status']}")
        print(f"   - token: {data['token']}")


@pytest.mark.asyncio
async def test_get_line_notification_config_token_masking():
    """
    LINE通知設定取得API - トークンマスキングテスト

    シナリオ:
    1. GET /api/notifications/line を呼び出す
    2. トークンが完全にマスキングされていることを確認
    3. 先頭4文字のみ表示されていることを確認（トークンが設定されている場合）
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/notifications/line")

        assert response.status_code == 200
        data = response.json()

        token = data["token"]

        if token and token != "":
            # トークンが設定されている場合
            # 先頭4文字以外は必ずマスキングされていること
            assert "***masked***" in token, "Token must contain masked section"

            # トークン全体が "***masked***" だけではないこと（先頭文字が表示されていること）
            if len(token) > len("***masked***"):
                prefix = token.split("***masked***")[0]
                assert len(prefix) == 4, f"Token prefix must be exactly 4 characters, got {len(prefix)}"
                assert prefix.isalnum() or '-' in prefix or '_' in prefix, \
                    "Token prefix must be alphanumeric or contain - or _"

        print(f"✅ トークンマスキングテスト成功")
        print(f"   - masked_token: {token}")


@pytest.mark.asyncio
async def test_get_line_notification_config_consistency():
    """
    LINE通知設定取得API - 一貫性テスト

    シナリオ:
    1. GET /api/notifications/line を2回呼び出す
    2. レスポンスが一貫していることを確認
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1回目の呼び出し
        response1 = await client.get("/api/notifications/line")
        assert response1.status_code == 200
        data1 = response1.json()

        # 2回目の呼び出し
        response2 = await client.get("/api/notifications/line")
        assert response2.status_code == 200
        data2 = response2.json()

        # 一貫性の確認（キャメルケース）
        assert data1["isConnected"] == data2["isConnected"], \
            "isConnected must be consistent across calls"
        assert data1["status"] == data2["status"], \
            "status must be consistent across calls"
        assert data1["token"] == data2["token"], \
            "token must be consistent across calls"

        print(f"✅ 一貫性テスト成功")
        print(f"   - データは2回の呼び出しで一貫しています")


@pytest.mark.asyncio
async def test_get_line_notification_config_response_time():
    """
    LINE通知設定取得API - レスポンスタイムテスト

    シナリオ:
    1. GET /api/notifications/line を呼び出す
    2. レスポンスタイムが1秒以内であることを確認
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        start_time = datetime.now()

        response = await client.get("/api/notifications/line")

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert elapsed_time < 1.0, f"Response time too slow: {elapsed_time}s"

        print(f"✅ レスポンスタイムテスト成功")
        print(f"   - elapsed_time: {elapsed_time:.3f}秒")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
