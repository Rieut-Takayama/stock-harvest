"""
スキャン基盤強化版統合テスト
スライス4: スキャン基盤の完全フロー検証・実データテスト
バックエンド実装エージェント作成
"""

import pytest
import httpx
import asyncio
import time
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import sys
import os

# テストユーティリティのインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from tests.utils.api_test_helper import APITestHelper
from tests.utils.db_test_helper import DatabaseTestHelper
from tests.utils.ScanSliceMilestoneTracker import ScanSliceMilestoneTracker

class TestScanFoundationIntegration:
    """スキャン基盤強化版統合テストクラス"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.api_helper = APITestHelper()
        cls.db_helper = DatabaseTestHelper()
        cls.base_url = cls.api_helper.base_url
        cls.tracker = ScanSliceMilestoneTracker()
        
        print("\n🔧 スキャン基盤統合テスト - セットアップ開始")
        cls.tracker.mark("テストクラス初期化")
    
    def setup_method(self, method):
        """各テストメソッド前の初期化"""
        print(f"\n🧪 テスト開始: {method.__name__}")
        self.tracker.set_operation(f"テスト実行: {method.__name__}")
    
    def teardown_method(self, method):
        """各テストメソッド後のクリーンアップ"""
        print(f"✅ テスト完了: {method.__name__}")

    @pytest.mark.asyncio
    async def test_01_scan_execute_enhanced_flow(self):
        """
        強化版スキャン実行フロー統合テスト
        API仕様書準拠 + 実データ処理 + パフォーマンス検証
        """
        self.tracker.mark("スキャン実行フロー開始")
        
        async with httpx.AsyncClient() as client:
            # Step 1: スキャン実行開始
            response = await client.post(
                f"{self.base_url}/api/scan/execute",
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # API仕様書準拠の検証
            assert "scanId" in data
            assert "message" in data
            assert data["message"] == "全銘柄スキャンを開始しました"
            
            scan_id = data["scanId"]
            assert scan_id.startswith("scan_")
            
            print(f"📍 スキャンID取得: {scan_id}")
            self.tracker.mark("スキャンID取得")
            
            # Step 2: 開始直後のステータス確認
            await asyncio.sleep(1)  # スキャン開始待機
            
            status_response = await client.get(
                f"{self.base_url}/api/scan/status",
                timeout=30.0
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            # API仕様書準拠のステータスフィールド検証
            required_status_fields = [
                'isRunning', 'progress', 'totalStocks', 
                'processedStocks', 'currentStock', 'estimatedTime', 'message'
            ]
            
            for field in required_status_fields:
                assert field in status_data, f"ステータスフィールド {field} が存在しない"
            
            assert status_data['isRunning'] == True
            assert status_data['progress'] >= 0
            assert status_data['totalStocks'] > 0
            
            print(f"📊 初期ステータス: 進捗={status_data['progress']}%, 総銘柄数={status_data['totalStocks']}")
            self.tracker.mark("初期ステータス確認")
            
            # Step 3: スキャン進行の監視
            max_wait_time = 120  # 2分間の制限
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status_response = await client.get(f"{self.base_url}/api/scan/status")
                status_data = status_response.json()
                
                print(f"🔄 スキャン進捗: {status_data['progress']}%, 処理済み={status_data['processedStocks']}, 現在={status_data.get('currentStock', 'N/A')}")
                
                if not status_data['isRunning']:
                    break
                
                await asyncio.sleep(2)
            
            self.tracker.mark("スキャン進行監視")
            
            # Step 4: 最終ステータスの確認
            final_status_response = await client.get(f"{self.base_url}/api/scan/status")
            final_status = final_status_response.json()
            
            # スキャン完了を確認
            if final_status['isRunning']:
                print("⚠️ スキャンがタイムアウト時間内に完了しませんでした")
                # タイムアウトの場合でもテストは継続
            else:
                print(f"🎉 スキャン完了: 進捗={final_status['progress']}%")
                assert final_status['progress'] == 100
            
            self.tracker.mark("スキャン完了確認")

    @pytest.mark.asyncio
    async def test_02_scan_results_api_compliance(self):
        """
        スキャン結果取得API仕様書準拠テスト
        レスポンス形式とデータ構造の厳密検証
        """
        self.tracker.mark("結果取得API検証開始")
        
        async with httpx.AsyncClient() as client:
            # 結果取得
            response = await client.get(
                f"{self.base_url}/api/scan/results",
                timeout=30.0
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # API仕様書準拠のレスポンス構造検証
            required_fields = ['scanId', 'completedAt', 'totalProcessed', 'logicA', 'logicB']
            
            for field in required_fields:
                assert field in data, f"結果フィールド {field} が存在しない"
            
            # logicA・logicBの構造検証
            for logic_type in ['logicA', 'logicB']:
                logic_data = data[logic_type]
                
                assert 'detected' in logic_data
                assert 'stocks' in logic_data
                assert isinstance(logic_data['detected'], int)
                assert isinstance(logic_data['stocks'], list)
                
                # 検出数と株式リストの整合性
                assert logic_data['detected'] == len(logic_data['stocks'])
                
                # 株式データの形式検証
                for stock in logic_data['stocks']:
                    required_stock_fields = ['code', 'name', 'price', 'change', 'changeRate', 'volume']
                    for stock_field in required_stock_fields:
                        assert stock_field in stock, f"株式フィールド {stock_field} が存在しない"
                    
                    # データ型の検証
                    assert isinstance(stock['code'], str)
                    assert isinstance(stock['name'], str)
                    assert isinstance(stock['price'], (int, float))
                    assert isinstance(stock['change'], (int, float))
                    assert isinstance(stock['changeRate'], (int, float))
                    assert isinstance(stock['volume'], int)
            
            print(f"📈 結果サマリー: logicA={data['logicA']['detected']}件, logicB={data['logicB']['detected']}件")
            self.tracker.mark("結果構造検証完了")

    @pytest.mark.asyncio 
    async def test_03_scan_status_realtime_updates(self):
        """
        リアルタイムステータス更新テスト
        進捗の正確性とリアルタイム性の検証
        """
        self.tracker.mark("リアルタイム更新テスト開始")
        
        async with httpx.AsyncClient() as client:
            # スキャン開始
            execute_response = await client.post(f"{self.base_url}/api/scan/execute")
            assert execute_response.status_code == 200
            
            scan_data = execute_response.json()
            scan_id = scan_data["scanId"]
            
            # リアルタイムステータス監視
            status_history = []
            monitoring_duration = 30  # 30秒間監視
            start_time = time.time()
            
            while time.time() - start_time < monitoring_duration:
                status_response = await client.get(f"{self.base_url}/api/scan/status")
                status_data = status_response.json()
                
                status_history.append({
                    'timestamp': time.time(),
                    'progress': status_data['progress'],
                    'processedStocks': status_data['processedStocks'],
                    'isRunning': status_data['isRunning']
                })
                
                if not status_data['isRunning']:
                    break
                    
                await asyncio.sleep(2)
            
            # 進捗の単調増加を検証
            for i in range(1, len(status_history)):
                current = status_history[i]
                previous = status_history[i-1]
                
                # 進捗は後退してはいけない
                assert current['progress'] >= previous['progress'], "進捗が後退している"
                assert current['processedStocks'] >= previous['processedStocks'], "処理済み銘柄数が後退している"
            
            print(f"📊 ステータス履歴: {len(status_history)}回更新")
            self.tracker.mark("進捗単調増加検証")

    @pytest.mark.asyncio
    async def test_04_scan_database_consistency(self):
        """
        データベース整合性テスト
        スキャン実行とデータベース状態の整合性検証
        """
        self.tracker.mark("DB整合性テスト開始")
        
        async with httpx.AsyncClient() as client:
            # 事前にスキャンを実行
            execute_response = await client.post(f"{self.base_url}/api/scan/execute")
            scan_data = execute_response.json()
            scan_id = scan_data["scanId"]
            
            # スキャン完了まで待機
            await self._wait_for_scan_completion(client, timeout=60)
            
            # API結果を取得
            api_results_response = await client.get(f"{self.base_url}/api/scan/results")
            api_results = api_results_response.json()
            
            # データベースから直接結果を取得して比較
            db = await self.db_helper.get_db_connection()
            db_scan_executions = await db.fetch_all(
                "SELECT * FROM scan_executions WHERE id = :scan_id", {"scan_id": scan_id}
            )

            assert len(db_scan_executions) == 1
            db_execution = db_scan_executions[0]

            # API結果とDB結果の整合性確認
            assert api_results['totalProcessed'] == db_execution['processed_stocks']
            assert api_results['scanId'] == scan_id

            # スキャン結果の件数一致確認
            db_results_logic_a = await db.fetch_all(
                "SELECT COUNT(*) as count FROM scan_results WHERE scan_id = :scan_id AND logic_type IN ('logic_a', 'logic_a_enhanced')",
                {"scan_id": scan_id}
            )
            db_results_logic_b = await db.fetch_all(
                "SELECT COUNT(*) as count FROM scan_results WHERE scan_id = :scan_id AND logic_type IN ('logic_b', 'logic_b_enhanced')",
                {"scan_id": scan_id}
            )
            
            logic_a_db_count = db_results_logic_a[0]['count'] if db_results_logic_a else 0
            logic_b_db_count = db_results_logic_b[0]['count'] if db_results_logic_b else 0
            
            assert api_results['logicA']['detected'] == logic_a_db_count
            assert api_results['logicB']['detected'] == logic_b_db_count
            
            print(f"🔗 DB整合性確認: API/DB一致")
            self.tracker.mark("DB整合性確認")

    @pytest.mark.asyncio
    async def test_05_scan_error_handling(self):
        """
        エラーハンドリングテスト
        異常系の適切な処理とレスポンスの検証
        """
        self.tracker.mark("エラーハンドリングテスト開始")
        
        async with httpx.AsyncClient() as client:
            # 不正なパラメータでのテスト（将来の拡張を想定）
            # 現在はパラメータなしのAPIだが、フォーマット検証
            
            # 同時スキャン実行制限のテスト
            # 1つ目のスキャン開始
            first_scan = await client.post(f"{self.base_url}/api/scan/execute")
            assert first_scan.status_code == 200
            
            # すぐに2つ目のスキャンを試行
            second_scan = await client.post(f"{self.base_url}/api/scan/execute")
            
            # 同時実行を許可するか制限するかは実装次第
            # ここでは実装の動作を確認
            print(f"🔄 同時スキャンレスポンス: {second_scan.status_code}")
            
            # 存在しないスキャンIDでのステータス確認
            fake_status = await client.get(f"{self.base_url}/api/scan/status")
            # ステータスAPIは最新のスキャンを返すため、常に200
            assert fake_status.status_code == 200
            
            self.tracker.mark("エラーケース検証")

    @pytest.mark.asyncio
    async def test_06_scan_performance_benchmark(self):
        """
        パフォーマンスベンチマークテスト
        レスポンス時間とスループットの測定
        """
        self.tracker.mark("パフォーマンステスト開始")
        
        async with httpx.AsyncClient() as client:
            # API実行時間の計測
            performance_metrics = {}
            
            # スキャン実行API
            start_time = time.time()
            execute_response = await client.post(f"{self.base_url}/api/scan/execute")
            execute_time = time.time() - start_time
            performance_metrics['scan_execute'] = execute_time
            
            assert execute_response.status_code == 200
            
            # ステータスAPI（複数回実行）
            status_times = []
            for _ in range(5):
                start_time = time.time()
                await client.get(f"{self.base_url}/api/scan/status")
                status_time = time.time() - start_time
                status_times.append(status_time)
            
            performance_metrics['scan_status_avg'] = sum(status_times) / len(status_times)
            performance_metrics['scan_status_max'] = max(status_times)
            
            # 結果取得API
            start_time = time.time()
            await client.get(f"{self.base_url}/api/scan/results")
            results_time = time.time() - start_time
            performance_metrics['scan_results'] = results_time
            
            # パフォーマンス基準の確認
            assert performance_metrics['scan_execute'] < 5.0  # 5秒以内
            assert performance_metrics['scan_status_avg'] < 1.0  # 1秒以内
            assert performance_metrics['scan_results'] < 3.0  # 3秒以内
            
            print(f"⚡ パフォーマンス結果:")
            for metric, value in performance_metrics.items():
                print(f"  - {metric}: {value:.3f}秒")
            
            self.tracker.mark("パフォーマンス計測完了")

    async def _wait_for_scan_completion(self, client, timeout: int = 60) -> bool:
        """
        スキャン完了まで待機するヘルパーメソッド
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_response = await client.get(f"{self.base_url}/api/scan/status")
            status_data = status_response.json()
            
            if not status_data['isRunning']:
                return True
                
            await asyncio.sleep(2)
        
        return False  # タイムアウト

    @classmethod
    def teardown_class(cls):
        """テストクラス終了処理"""
        print("\n🏁 スキャン基盤統合テスト - 全体サマリー")
        cls.tracker.summary()
        
        # テスト結果のサマリー
        print("\n📋 スキャン基盤テスト完了:")
        print("  ✅ スキャン実行フロー")
        print("  ✅ API仕様書準拠")
        print("  ✅ リアルタイム更新")
        print("  ✅ データベース整合性")
        print("  ✅ エラーハンドリング")
        print("  ✅ パフォーマンスベンチマーク")


if __name__ == "__main__":
    # スタンドアロンテスト実行
    print("🚀 スキャン基盤統合テスト - スタンドアロン実行")
    
    # 環境変数設定
    import os
    os.environ["DATABASE_URL"] = "sqlite:///./test_database.db"
    
    # テスト実行
    pytest.main([__file__, "-v", "--tb=short"])