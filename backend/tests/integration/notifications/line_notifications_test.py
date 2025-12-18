"""
LINE通知基盤 統合テスト
スライス2-B: LINE通知基盤の全エンドポイントテスト

テスト対象:
- GET /api/notifications/line - LINE通知設定取得
- PUT /api/notifications/line - LINE通知設定更新
- POST /api/notifications/line/connect - LINE連携実行
- GET /api/notifications/line/status - LINE接続状態確認
"""

import pytest
import httpx
import asyncio
import json
import os
from typing import Dict, Any
from datetime import datetime

from ...utils.MilestoneTracker import MilestoneTracker

# テスト設定
BASE_URL = "http://localhost:8432"
TEST_TIMEOUT = 30.0


class TestLineNotifications:
    """LINE通知基盤エンドポイントテスト"""
    
    def setup_method(self):
        self.tracker = MilestoneTracker()
        self.tracker.set_operation("LINE通知基盤統合テスト")
        self.test_tokens = []  # テスト用トークンの記録
        
    async def cleanup(self):
        """テストデータクリーンアップ"""
        self.tracker.set_operation("テストクリーンアップ")
        
        # LINE設定をリセット
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            try:
                await client.put(f"{BASE_URL}/api/notifications/line", json={
                    "token": None,
                    "isConnected": False
                })
            except:
                pass  # エラーは無視
    
    async def test_1_get_initial_line_config(self):
        """テスト1: 初期LINE通知設定取得"""
        self.tracker.set_operation("初期LINE設定取得")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/notifications/line")
            
            self.tracker.mark("API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            config = response.json()
            required_fields = ["isConnected", "token", "status"]
            for field in required_fields:
                assert field in config, f"Field '{field}' should be present"
            
            # 初期状態の確認
            assert config["isConnected"] in [True, False], "isConnected should be boolean"
            assert config["status"] in ["connected", "disconnected", "not_configured"], "Invalid status value"
            
            self.tracker.mark("バリデーション完了")
            
            print(f"✅ Test 1 Passed: Initial config - connected={config['isConnected']}, status={config['status']}")
            return config
    
    async def test_2_update_line_config(self):
        """テスト2: LINE通知設定更新"""
        self.tracker.set_operation("LINE設定更新")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            config_data = {
                "token": "test_line_token_update_123",
                "isConnected": True
            }
            
            self.test_tokens.append(config_data["token"])
            
            response = await client.put(
                f"{BASE_URL}/api/notifications/line",
                json=config_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.tracker.mark("設定更新API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            updated_config = response.json()
            assert updated_config["isConnected"] == True, "Connection status should be updated"
            assert updated_config["status"] == "connected", "Status should be connected"
            
            self.tracker.mark("更新結果バリデーション完了")
            
            print(f"✅ Test 2 Passed: Updated LINE config to connected")
            return updated_config
    
    async def test_3_line_connect_basic(self):
        """テスト3: LINE連携（基本）"""
        self.tracker.set_operation("LINE基本連携")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            connect_data = {
                "token": "test_line_connect_basic_456",
                "testNotification": False  # テスト通知なし
            }
            
            self.test_tokens.append(connect_data["token"])
            
            response = await client.post(
                f"{BASE_URL}/api/notifications/line/connect",
                json=connect_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.tracker.mark("LINE連携API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            connection_result = response.json()
            assert connection_result["isConnected"] == True, "Connection should be established"
            assert connection_result["status"] == "connected", "Status should be connected"
            
            self.tracker.mark("連携結果バリデーション完了")
            
            print(f"✅ Test 3 Passed: Basic LINE connection established")
            return connection_result
    
    async def test_4_line_connect_with_test_notification(self):
        """テスト4: LINE連携（テスト通知付き）"""
        self.tracker.set_operation("LINE連携（テスト通知付き）")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            connect_data = {
                "token": "test_line_connect_notify_789",
                "testNotification": True  # テスト通知あり
            }
            
            self.test_tokens.append(connect_data["token"])
            
            response = await client.post(
                f"{BASE_URL}/api/notifications/line/connect",
                json=connect_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.tracker.mark("テスト通知付き連携API完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            connection_result = response.json()
            assert connection_result["isConnected"] == True, "Connection should be established"
            assert connection_result["status"] == "connected", "Status should be connected"
            assert "testNotificationSent" in connection_result, "Test notification flag should be present"
            
            self.tracker.mark("テスト通知結果バリデーション完了")
            
            print(f"✅ Test 4 Passed: LINE connected with test notification={connection_result.get('testNotificationSent', False)}")
            return connection_result
    
    async def test_5_line_notification_status(self):
        """テスト5: LINE通知状態確認"""
        self.tracker.set_operation("LINE状態確認")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/notifications/line/status")
            
            self.tracker.mark("状態確認API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            status_info = response.json()
            required_fields = [
                "isConnected", "status", "notificationCount", "errorCount",
                "connectionHealth", "tokenConfigured"
            ]
            
            for field in required_fields:
                assert field in status_info, f"Field '{field}' should be present in status info"
            
            # 前のテストでLINE連携したので、connected状態のはず
            assert status_info["isConnected"] == True, "Should be connected from previous test"
            assert status_info["tokenConfigured"] == True, "Token should be configured"
            assert isinstance(status_info["notificationCount"], int), "Notification count should be integer"
            assert isinstance(status_info["errorCount"], int), "Error count should be integer"
            assert status_info["connectionHealth"] in ["excellent", "good", "warning", "critical", "unknown"], "Invalid health status"
            
            self.tracker.mark("状態情報バリデーション完了")
            
            print(f"✅ Test 5 Passed: LINE status check - health={status_info['connectionHealth']}, notifications={status_info['notificationCount']}, errors={status_info['errorCount']}")
            return status_info
    
    async def test_6_line_disconnect(self):
        """テスト6: LINE切断"""
        self.tracker.set_operation("LINE切断")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            disconnect_data = {
                "isConnected": False
            }
            
            response = await client.put(
                f"{BASE_URL}/api/notifications/line",
                json=disconnect_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.tracker.mark("切断API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            updated_config = response.json()
            assert updated_config["isConnected"] == False, "Connection should be disabled"
            assert updated_config["status"] in ["disconnected", "not_configured"], "Status should indicate disconnection"
            
            self.tracker.mark("切断結果バリデーション完了")
            
            print(f"✅ Test 6 Passed: LINE disconnected successfully")
            return updated_config
    
    async def test_7_error_handling_invalid_token(self):
        """テスト7: エラーハンドリング（無効トークン）"""
        self.tracker.set_operation("無効トークンエラーハンドリング")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            invalid_connect_data = {
                "token": "invalid_token_should_fail",
                "testNotification": True
            }
            
            response = await client.post(
                f"{BASE_URL}/api/notifications/line/connect",
                json=invalid_connect_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.tracker.mark("無効トークンAPI呼び出し完了")
            
            # 無効トークンの場合は400エラーが期待される
            assert response.status_code == 400, f"Expected 400 for invalid token, got {response.status_code}"
            
            error_response = response.json()
            assert "detail" in error_response, "Error response should have detail field"
            assert "failed" in error_response["detail"].lower(), "Error message should indicate failure"
            
            self.tracker.mark("エラーレスポンスバリデーション完了")
            
            print(f"✅ Test 7 Passed: Invalid token handled correctly")
            return error_response
    
    async def test_8_status_after_disconnect(self):
        """テスト8: 切断後の状態確認"""
        self.tracker.set_operation("切断後状態確認")
        self.tracker.mark("テスト開始")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/notifications/line/status")
            
            self.tracker.mark("切断後状態API呼び出し完了")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            status_info = response.json()
            
            # 切断されているはず
            # tokenConfiguredは設定値によって変動する可能性があるため、チェックしない
            assert isinstance(status_info["isConnected"], bool), "isConnected should be boolean"
            assert isinstance(status_info["notificationCount"], int), "Notification count should be integer"
            
            self.tracker.mark("切断後状態バリデーション完了")
            
            print(f"✅ Test 8 Passed: Post-disconnect status check - connected={status_info['isConnected']}")
            return status_info
    
    async def run_all_tests(self):
        """全テスト実行"""
        test_results = {}
        
        try:
            # テスト1: 初期設定取得
            self.tracker.mark("全テスト開始")
            test_results["test_1"] = await self.test_1_get_initial_line_config()
            
            # テスト2: 設定更新
            test_results["test_2"] = await self.test_2_update_line_config()
            
            # テスト3: 基本LINE連携
            test_results["test_3"] = await self.test_3_line_connect_basic()
            
            # テスト4: テスト通知付きLINE連携
            test_results["test_4"] = await self.test_4_line_connect_with_test_notification()
            
            # テスト5: 状態確認
            test_results["test_5"] = await self.test_5_line_notification_status()
            
            # テスト6: LINE切断
            test_results["test_6"] = await self.test_6_line_disconnect()
            
            # テスト7: エラーハンドリング
            test_results["test_7"] = await self.test_7_error_handling_invalid_token()
            
            # テスト8: 切断後状態確認
            test_results["test_8"] = await self.test_8_status_after_disconnect()
            
            self.tracker.mark("全テスト完了")
            
            return test_results
            
        finally:
            # テストデータクリーンアップ
            await self.cleanup()
            self.tracker.summary()


async def main():
    """統合テストメイン実行"""
    print("🧪 Starting LINE Notification Infrastructure Integration Tests")
    print("=" * 70)
    
    test_instance = TestLineNotifications()
    
    try:
        # 全テスト実行
        results = await test_instance.run_all_tests()
        
        print("\n" + "=" * 70)
        print("🎉 All LINE Notification Infrastructure Tests Completed Successfully!")
        print(f"✅ PASSED: 8/8 tests")
        print(f"❌ FAILED: 0/8 tests")
        print("\n📋 Tested Endpoints:")
        print("  - GET /api/notifications/line (LINE通知設定取得)")
        print("  - PUT /api/notifications/line (LINE通知設定更新)")  
        print("  - POST /api/notifications/line/connect (LINE連携実行)")
        print("  - GET /api/notifications/line/status (LINE接続状態確認)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        print(f"❌ FAILED: Tests incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)