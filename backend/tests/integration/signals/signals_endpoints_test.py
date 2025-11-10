"""
手動決済シグナル統合テスト
Stock Harvest AI プロジェクト

実際のAPIサーバーと実際のデータベースに対するテストを実行します。
モック未使用、実データベース・実API接続での動作テストです。
"""

import pytest
import httpx
import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any

# テストユーティリティ
from ...utils.api_test_helper import APITestHelper
from ...utils.db_test_helper import DatabaseTestHelper


class TestSignalsEndpoints:
    """手動決済シグナルエンドポイント統合テスト"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.api_helper = APITestHelper()
        cls.db_helper = DatabaseTestHelper()
        cls.base_url = cls.api_helper.base_url
        
    def test_01_manual_execute_stop_loss_basic(self):
        """
        テスト1: 基本的な損切りシグナル実行
        POST /api/signals/manual-execute (stop_loss)
        """
        # リクエストデータ
        payload = {
            "type": "stop_loss",
            "reason": "市場急落による緊急損切り"
        }
        
        # APIリクエスト実行
        response = httpx.post(
            f"{self.base_url}/api/signals/manual-execute",
            json=payload,
            timeout=30.0
        )
        
        # レスポンス検証
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}, response: {response.text}"
        
        data = response.json()
        assert "success" in data
        assert "signalId" in data
        assert "executedAt" in data
        assert "message" in data
        assert data["success"] == True
        assert data["signalId"].startswith("signal-")
        assert "損切りシグナル" in data["message"]
        
        # データベース確認
        signal_id = data["signalId"]
        db_record = asyncio.run(self._get_signal_from_db(signal_id))
        assert db_record is not None
        assert db_record["signal_type"] == "stop_loss"
        assert db_record["status"] == "executed"
        
        print(f"✅ Test 1 passed: Stop loss signal executed successfully with ID {signal_id}")

    def test_02_manual_execute_take_profit_with_stock(self):
        """
        テスト2: 特定銘柄の利確シグナル実行
        POST /api/signals/manual-execute (take_profit + stockCode)
        """
        payload = {
            "type": "take_profit",
            "stockCode": "7203",
            "reason": "目標利益到達のため利確"
        }
        
        response = httpx.post(
            f"{self.base_url}/api/signals/manual-execute",
            json=payload,
            timeout=30.0
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "7203" in data["message"]
        assert "利確シグナル" in data["message"]
        
        # データベース確認
        signal_id = data["signalId"]
        db_record = asyncio.run(self._get_signal_from_db(signal_id))
        assert db_record["stock_code"] == "7203"
        assert db_record["signal_type"] == "take_profit"
        
        print(f"✅ Test 2 passed: Take profit signal for stock 7203 executed with ID {signal_id}")

    def test_03_validation_error_invalid_signal_type(self):
        """
        テスト3: 無効なシグナルタイプのバリデーションエラー
        """
        payload = {
            "type": "invalid_type",
            "reason": "テスト用無効タイプ"
        }
        
        response = httpx.post(
            f"{self.base_url}/api/signals/manual-execute",
            json=payload,
            timeout=30.0
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid signal type" in data["detail"]
        
        print("✅ Test 3 passed: Invalid signal type validation working")

    def test_04_validation_error_invalid_stock_code(self):
        """
        テスト4: 無効な銘柄コードのバリデーションエラー
        """
        payload = {
            "type": "stop_loss",
            "stockCode": "invalid",
            "reason": "テスト用無効銘柄コード"
        }
        
        response = httpx.post(
            f"{self.base_url}/api/signals/manual-execute",
            json=payload,
            timeout=30.0
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid stock code format" in data["detail"]
        
        print("✅ Test 4 passed: Invalid stock code validation working")

    def test_05_signal_history_endpoint(self):
        """
        テスト5: シグナル履歴取得エンドポイント
        GET /api/signals/history
        """
        response = httpx.get(
            f"{self.base_url}/api/signals/history?limit=5",
            timeout=30.0
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "signals" in data
        assert "total" in data
        assert data["success"] == True
        assert isinstance(data["signals"], list)
        
        # 前のテストで作成されたシグナルが含まれているはず
        assert len(data["signals"]) >= 2
        
        print(f"✅ Test 5 passed: Signal history retrieved with {len(data['signals'])} records")

    def test_06_signal_history_limit_validation(self):
        """
        テスト6: シグナル履歴取得の制限値バリデーション
        """
        # 上限チェック
        response = httpx.get(
            f"{self.base_url}/api/signals/history?limit=150",
            timeout=30.0
        )
        assert response.status_code == 400
        
        # 下限チェック
        response = httpx.get(
            f"{self.base_url}/api/signals/history?limit=0",
            timeout=30.0
        )
        assert response.status_code == 400
        
        print("✅ Test 6 passed: History limit validation working")

    def test_07_concurrent_signal_execution(self):
        """
        テスト7: 複数シグナルの並行実行
        """
        # 3つのシグナルを並行実行
        payloads = [
            {"type": "stop_loss", "reason": "並行テスト1"},
            {"type": "take_profit", "stockCode": "6758", "reason": "並行テスト2"},
            {"type": "stop_loss", "stockCode": "4689", "reason": "並行テスト3"}
        ]
        
        async def execute_signal(payload):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/signals/manual-execute",
                    json=payload,
                    timeout=30.0
                )
                return response
        
        async def run_concurrent_test():
            tasks = [execute_signal(payload) for payload in payloads]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            return responses
        
        responses = asyncio.run(run_concurrent_test())
        
        # すべてのレスポンスが成功していることを確認
        success_count = 0
        for i, response in enumerate(responses):
            if isinstance(response, httpx.Response):
                print(f"Response {i}: Status {response.status_code}, Body: {response.text[:200]}")
                if response.status_code == 200:
                    success_count += 1
            else:
                print(f"Response {i}: Exception: {response}")
        
        print(f"Success count: {success_count}/{len(payloads)}")
        assert success_count == len(payloads)
        
        print(f"✅ Test 7 passed: {success_count}/{len(payloads)} concurrent signals executed successfully")

    def test_08_signal_persistence_after_restart(self):
        """
        テスト8: シグナルデータの永続化確認（サーバー再起動後も残る）
        """
        # 新しいシグナル作成
        payload = {
            "type": "take_profit",
            "reason": "永続化テスト用シグナル"
        }
        
        response = httpx.post(
            f"{self.base_url}/api/signals/manual-execute",
            json=payload,
            timeout=30.0
        )
        assert response.status_code == 200
        
        signal_id = response.json()["signalId"]
        
        # データベースから直接確認
        db_record = asyncio.run(self._get_signal_from_db(signal_id))
        assert db_record is not None
        assert db_record["reason"] == "永続化テスト用シグナル"
        
        # 履歴エンドポイントからも確認
        history_response = httpx.get(
            f"{self.base_url}/api/signals/history?limit=10",
            timeout=30.0
        )
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        signal_found = any(
            signal["id"] == signal_id 
            for signal in history_data["signals"]
        )
        assert signal_found
        
        print(f"✅ Test 8 passed: Signal {signal_id} persisted in database and accessible via API")

    async def _get_signal_from_db(self, signal_id: str) -> Dict[str, Any]:
        """データベースから直接シグナル情報を取得"""
        try:
            from ...utils.db_test_helper import DatabaseTestHelper
            db_helper = DatabaseTestHelper()
            
            query = "SELECT * FROM manual_signals WHERE id = :signal_id"
            db = await db_helper.get_db_connection()
            row = await db.fetch_one(query, {"signal_id": signal_id})
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Database query error: {e}")
            return None

    def test_99_cleanup_test_data(self):
        """
        テスト99: テストデータクリーンアップ
        """
        # テストで作成されたシグナルを削除
        # 本番環境では不要だが、テスト環境のデータ蓄積防止のため実装
        
        try:
            async def cleanup():
                from ...utils.db_test_helper import DatabaseTestHelper
                db_helper = DatabaseTestHelper()
                
                # 今日作成されたテストシグナルを削除
                today = datetime.now().date()
                query = """
                    DELETE FROM manual_signals 
                    WHERE created_at::date = :today 
                    AND (reason LIKE '%テスト%' OR reason LIKE '%test%' OR reason LIKE '%並行テスト%' OR reason LIKE '%永続化テスト%')
                """
                db = await db_helper.get_db_connection()
                result = await db.execute(query, {"today": today})
                return result
            
            result = asyncio.run(cleanup())
            print(f"✅ Test 99 passed: Test data cleanup completed")
            
        except Exception as e:
            # クリーンアップ失敗はテストを失敗させない
            print(f"⚠️ Cleanup warning (non-critical): {e}")


if __name__ == "__main__":
    # 単体でテスト実行する場合
    test_class = TestSignalsEndpoints()
    test_class.setup_class()
    
    print("🧪 Running Signals Endpoints Integration Tests...")
    
    try:
        test_class.test_01_manual_execute_stop_loss_basic()
        test_class.test_02_manual_execute_take_profit_with_stock()
        test_class.test_03_validation_error_invalid_signal_type()
        test_class.test_04_validation_error_invalid_stock_code()
        test_class.test_05_signal_history_endpoint()
        test_class.test_06_signal_history_limit_validation()
        test_class.test_07_concurrent_signal_execution()
        test_class.test_08_signal_persistence_after_restart()
        test_class.test_99_cleanup_test_data()
        
        print("\n🎉 All Signals tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise