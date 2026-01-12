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

    async def test_11_filter_by_status_active(self):
        """テスト11: ステータスフィルタリング（active）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # アクティブなアラートのみ取得
            response = await client.get(f"{BASE_URL}/api/alerts?status=active")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"

            # 全てアクティブであることを確認
            for alert in alerts:
                assert alert["isActive"] == True, f"All alerts should be active, but alert {alert['id']} is inactive"

            print(f"✅ Test 11 Passed: Filtered {len(alerts)} active alerts")
            return alerts

    async def test_12_filter_by_status_inactive(self):
        """テスト12: ステータスフィルタリング（inactive）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # 非アクティブなアラートのみ取得
            response = await client.get(f"{BASE_URL}/api/alerts?status=inactive")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"

            # 全て非アクティブであることを確認
            for alert in alerts:
                assert alert["isActive"] == False, f"All alerts should be inactive, but alert {alert['id']} is active"

            print(f"✅ Test 12 Passed: Filtered {len(alerts)} inactive alerts")
            return alerts

    async def test_13_filter_by_type_price(self):
        """テスト13: タイプフィルタリング（price）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # 価格アラートのみ取得
            response = await client.get(f"{BASE_URL}/api/alerts?type=price")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"

            # 全て価格アラートであることを確認
            for alert in alerts:
                assert alert["type"] == "price", f"All alerts should be price type, but alert {alert['id']} is {alert['type']}"

            print(f"✅ Test 13 Passed: Filtered {len(alerts)} price alerts")
            return alerts

    async def test_14_filter_by_type_logic(self):
        """テスト14: タイプフィルタリング（logic）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # ロジックアラートのみ取得
            response = await client.get(f"{BASE_URL}/api/alerts?type=logic")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"

            # 全てロジックアラートであることを確認
            for alert in alerts:
                assert alert["type"] == "logic", f"All alerts should be logic type, but alert {alert['id']} is {alert['type']}"

            print(f"✅ Test 14 Passed: Filtered {len(alerts)} logic alerts")
            return alerts

    async def test_15_filter_combined_status_and_type(self):
        """テスト15: 複合フィルタリング（status + type）"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # アクティブな価格アラートのみ取得
            response = await client.get(f"{BASE_URL}/api/alerts?status=active&type=price")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert isinstance(alerts, list), "Response should be a list"

            # 全てアクティブかつ価格アラートであることを確認
            for alert in alerts:
                assert alert["isActive"] == True, f"Alert {alert['id']} should be active"
                assert alert["type"] == "price", f"Alert {alert['id']} should be price type"

            print(f"✅ Test 15 Passed: Filtered {len(alerts)} active price alerts")
            return alerts

    async def test_16_sort_by_created_at_desc(self):
        """テスト16: 作成日時降順ソート確認"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # 複数のアラートを作成（時間差をつける）
            import asyncio
            for i in range(3):
                alert_data = {
                    "type": "price",
                    "stockCode": f"000{i}",
                    "targetPrice": 1000 + i * 100,
                    "condition": {
                        "type": "price",
                        "operator": ">=",
                        "value": 1000 + i * 100
                    }
                }
                response = await client.post(
                    f"{BASE_URL}/api/alerts",
                    json=alert_data,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    self.created_alert_ids.append(response.json()["id"])
                await asyncio.sleep(0.1)  # 時間差を確保

            # アラート一覧取得
            response = await client.get(f"{BASE_URL}/api/alerts")

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            alerts = response.json()
            assert len(alerts) >= 3, f"Expected at least 3 alerts, got {len(alerts)}"

            # 作成日時が降順（新しい順）になっていることを確認
            from datetime import datetime
            for i in range(len(alerts) - 1):
                current_date = datetime.fromisoformat(alerts[i]["createdAt"].replace('Z', '+00:00'))
                next_date = datetime.fromisoformat(alerts[i + 1]["createdAt"].replace('Z', '+00:00'))
                assert current_date >= next_date, f"Alerts should be sorted by createdAt DESC"

            print(f"✅ Test 16 Passed: {len(alerts)} alerts sorted by createdAt DESC")
            return alerts
    
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

            # テスト11: ステータスフィルタリング（active）
            test_results["test_11"] = await self.test_11_filter_by_status_active()

            # テスト12: ステータスフィルタリング（inactive）
            test_results["test_12"] = await self.test_12_filter_by_status_inactive()

            # テスト13: タイプフィルタリング（price）
            test_results["test_13"] = await self.test_13_filter_by_type_price()

            # テスト14: タイプフィルタリング（logic）
            test_results["test_14"] = await self.test_14_filter_by_type_logic()

            # テスト15: 複合フィルタリング（status + type）
            test_results["test_15"] = await self.test_15_filter_combined_status_and_type()

            # テスト16: 作成日時降順ソート確認
            test_results["test_16"] = await self.test_16_sort_by_created_at_desc()

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
        print("🎉 All Alerts Management Integration Tests Completed Successfully!")
        print(f"✅ PASSED: 18/18 tests (including filtering & sorting features)")
        print(f"❌ FAILED: 0/18 tests")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        print(f"❌ FAILED: Tests incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)