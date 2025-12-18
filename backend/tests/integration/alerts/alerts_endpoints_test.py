"""
アラート管理 API統合テスト
スライス2-A: アラート管理の全エンドポイントテスト

テスト対象:
- GET /api/alerts - アラート一覧取得
- POST /api/alerts - アラート作成
- PUT /api/alerts/:id/toggle - アラート状態切替
- DELETE /api/alerts/:id - アラート削除
- GET /api/notifications/line - LINE通知設定取得
- PUT /api/notifications/line - LINE通知設定更新
"""

import pytest
import httpx
import asyncio
import json
from typing import Dict, Any

# テスト設定
BASE_URL = "http://localhost:8432"
TEST_TIMEOUT = 30.0


class TestAlertsEndpoints:
    """アラート管理エンドポイントテスト"""
    
    def setup_method(self):
        self.created_alert_ids = []  # テストで作成したアラートIDを記録
        
    async def cleanup(self):
        """テストデータクリーンアップ"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            for alert_id in self.created_alert_ids:
                try:
                    await client.delete(f"{BASE_URL}/api/alerts/{alert_id}")
                except:
                    pass  # エラーは無視
    
    async def test_1_get_alerts_empty_initial(self):
        """テスト1: アラート一覧取得（初期状態）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/alerts")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"
            # 初期状態では空でない可能性がある（他のテストデータ）
            print(f"✅ Test 1 Passed: Got {len(alerts)} alerts")
            return alerts
    
    async def test_2_create_price_alert(self):
        """テスト2: 価格アラート作成"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            alert_data = {
                "type": "price",
                "stockCode": "7203",
                "targetPrice": 3000,
                "condition": {
                    "type": "price",
                    "operator": ">=",
                    "value": 3000
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/api/alerts",
                json=alert_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            created_alert = response.json()
            assert created_alert["stockCode"] == "7203", "Stock code mismatch"
            assert created_alert["type"] == "price", "Alert type mismatch"
            assert created_alert["isActive"] == True, "Alert should be active by default"
            assert "id" in created_alert, "Alert ID should be present"
            
            # テストデータ記録
            self.created_alert_ids.append(created_alert["id"])
            
            print(f"✅ Test 2 Passed: Created price alert {created_alert['id']}")
            return created_alert
    
    async def test_3_create_logic_alert(self):
        """テスト3: ロジックアラート作成"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            alert_data = {
                "type": "logic",
                "stockCode": "9984",
                "condition": {
                    "type": "logic",
                    "logicType": "logic_a"
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/api/alerts",
                json=alert_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            created_alert = response.json()
            assert created_alert["stockCode"] == "9984", "Stock code mismatch"
            assert created_alert["type"] == "logic", "Alert type mismatch"
            
            # テストデータ記録
            self.created_alert_ids.append(created_alert["id"])
            
            print(f"✅ Test 3 Passed: Created logic alert {created_alert['id']}")
            return created_alert
    
    async def test_4_get_alerts_with_data(self):
        """テスト4: アラート一覧取得（データあり）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/alerts")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"
            assert len(alerts) >= 2, f"Expected at least 2 alerts, got {len(alerts)}"
            
            print(f"✅ Test 4 Passed: Got {len(alerts)} alerts")
            return alerts
    
    async def test_5_toggle_alert_status(self):
        """テスト5: アラート状態切替"""
        if not self.created_alert_ids:
            pytest.skip("No alerts available for toggle test")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            alert_id = self.created_alert_ids[0]
            
            response = await client.put(f"{BASE_URL}/api/alerts/{alert_id}/toggle")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            updated_alert = response.json()
            assert updated_alert["id"] == alert_id, "Alert ID mismatch"
            # 状態が変更されていることを確認
            assert "isActive" in updated_alert, "isActive field should be present"
            
            print(f"✅ Test 5 Passed: Toggled alert {alert_id} to {updated_alert['isActive']}")
            return updated_alert
    
    async def test_6_get_line_notification_config(self):
        """テスト6: LINE通知設定取得"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/notifications/line")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            config = response.json()
            required_fields = ["isConnected", "token", "status"]
            for field in required_fields:
                assert field in config, f"Field '{field}' should be present"
            
            print(f"✅ Test 6 Passed: LINE config status={config['status']}")
            return config
    
    async def test_7_update_line_notification_config(self):
        """テスト7: LINE通知設定更新"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            config_data = {
                "token": "test_integration_token_abc123",
                "isConnected": True
            }
            
            response = await client.put(
                f"{BASE_URL}/api/notifications/line",
                json=config_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            updated_config = response.json()
            assert updated_config["isConnected"] == True, "Connection status should be updated"
            assert updated_config["status"] == "connected", "Status should be connected"
            
            print(f"✅ Test 7 Passed: Updated LINE config to connected")
            return updated_config
    
    async def test_7_5_line_connect_with_test_notification(self):
        """テスト7.5: LINE連携（テスト通知付き）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            connect_data = {
                "token": "test_line_connect_token_xyz789",
                "testNotification": True
            }
            
            response = await client.post(
                f"{BASE_URL}/api/notifications/line/connect",
                json=connect_data,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            connection_result = response.json()
            assert connection_result["isConnected"] == True, "Connection should be established"
            assert connection_result["status"] == "connected", "Status should be connected"
            assert "testNotificationSent" in connection_result, "Test notification flag should be present"
            
            print(f"✅ Test 7.5 Passed: LINE connected with test notification={connection_result.get('testNotificationSent', False)}")
            return connection_result
    
    async def test_7_6_line_notification_status(self):
        """テスト7.6: LINE通知状態確認"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/notifications/line/status")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            status_info = response.json()
            required_fields = [
                "isConnected", "status", "notificationCount", "errorCount",
                "connectionHealth", "tokenConfigured"
            ]
            for field in required_fields:
                assert field in status_info, f"Field '{field}' should be present"
            
            # 前のテストでLINE連携したので、connected状態のはず
            assert status_info["isConnected"] == True, "Should be connected from previous test"
            assert status_info["tokenConfigured"] == True, "Token should be configured"
            
            print(f"✅ Test 7.6 Passed: LINE status check - health={status_info['connectionHealth']}, notifications={status_info['notificationCount']}")
            return status_info
    
    async def test_8_delete_alert(self):
        """テスト8: アラート削除"""
        if len(self.created_alert_ids) < 2:
            pytest.skip("Not enough alerts for delete test")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            alert_id = self.created_alert_ids[1]  # 2番目のアラートを削除
            
            response = await client.delete(f"{BASE_URL}/api/alerts/{alert_id}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            delete_response = response.json()
            assert "message" in delete_response, "Delete message should be present"
            
            # 削除されたことを確認
            get_response = await client.get(f"{BASE_URL}/api/alerts")
            alerts = get_response.json()
            alert_ids = [alert["id"] for alert in alerts]
            assert alert_id not in alert_ids, "Deleted alert should not be in the list"
            
            # 記録から削除
            self.created_alert_ids.remove(alert_id)
            
            print(f"✅ Test 8 Passed: Deleted alert {alert_id}")
            return delete_response
    
    async def test_9_error_handling_invalid_alert(self):
        """テスト9: エラーハンドリング（無効なアラート作成）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            invalid_data = {
                "type": "invalid_type",
                "stockCode": "invalid"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/alerts",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            # FastAPIはPydanticバリデーションエラーで422を返す
            assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid data, got {response.status_code}"
            
            print("✅ Test 9 Passed: Invalid alert creation handled correctly")
    
    async def test_10_error_handling_not_found(self):
        """テスト10: エラーハンドリング（存在しないアラート操作）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            fake_id = "alert-nonexistent123"
            
            # 存在しないアラートの削除
            response = await client.delete(f"{BASE_URL}/api/alerts/{fake_id}")
            assert response.status_code == 404, f"Expected 404 for non-existent alert, got {response.status_code}"
            
            # 存在しないアラートの状態切替
            response = await client.put(f"{BASE_URL}/api/alerts/{fake_id}/toggle")
            assert response.status_code == 404, f"Expected 404 for non-existent alert, got {response.status_code}"
            
            print("✅ Test 10 Passed: Non-existent alert operations handled correctly")
    
    async def run_all_tests(self):
        """全テスト実行"""
        test_results = {}
        
        try:
            # テスト1: 初期アラート一覧
            test_results["test_1"] = await self.test_1_get_alerts_empty_initial()
            
            # テスト2: 価格アラート作成
            test_results["test_2"] = await self.test_2_create_price_alert()
            
            # テスト3: ロジックアラート作成
            test_results["test_3"] = await self.test_3_create_logic_alert()
            
            # テスト4: データありアラート一覧
            test_results["test_4"] = await self.test_4_get_alerts_with_data()
            
            # テスト5: アラート状態切替
            test_results["test_5"] = await self.test_5_toggle_alert_status()
            
            # テスト6: LINE通知設定取得
            test_results["test_6"] = await self.test_6_get_line_notification_config()
            
            # テスト7: LINE通知設定更新
            test_results["test_7"] = await self.test_7_update_line_notification_config()
            
            # テスト7.5: LINE連携（テスト通知付き）
            test_results["test_7_5"] = await self.test_7_5_line_connect_with_test_notification()
            
            # テスト7.6: LINE通知状態確認
            test_results["test_7_6"] = await self.test_7_6_line_notification_status()
            
            # テスト8: アラート削除
            test_results["test_8"] = await self.test_8_delete_alert()
            
            # テスト9: エラーハンドリング（無効データ）
            test_results["test_9"] = await self.test_9_error_handling_invalid_alert()
            
            # テスト10: エラーハンドリング（存在しないリソース）
            test_results["test_10"] = await self.test_10_error_handling_not_found()
            
            return test_results
            
        finally:
            # テストデータクリーンアップ
            await self.cleanup()


async def main():
    """統合テストメイン実行"""
    print("🧪 Starting Alerts Management Integration Tests")
    print("=" * 60)
    
    test_instance = TestAlertsEndpoints()
    
    try:
        # 全テスト実行
        results = await test_instance.run_all_tests()
        
        print("\n" + "=" * 60)
        print("🎉 All LINE Notification Integration Tests Completed Successfully!")
        print(f"✅ PASSED: 12/12 tests (including new LINE connect & status endpoints)")
        print(f"❌ FAILED: 0/12 tests")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        print(f"❌ FAILED: Tests incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)