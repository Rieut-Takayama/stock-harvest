"""
Charts Endpoints Integration Test
チャート機能エンドポイントの統合テスト
"""

import pytest
import asyncio
from typing import Dict, Any
import json

# テストユーティリティ
from ...utils.api_test_helper import APITestHelper
from ...utils.db_test_helper import DatabaseTestHelper
from ...utils.ChartSliceMilestoneTracker import ChartSliceMilestoneTracker

class TestChartsEndpoints:
    """チャートエンドポイント統合テスト"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.api = APITestHelper()
        cls.db = DatabaseTestHelper()
        cls.tracker = ChartSliceMilestoneTracker()
        
        print("\n🧪 チャート機能統合テスト開始")
        print("=" * 50)
    
    @classmethod
    async def asetup_class(cls):
        """非同期テストクラス初期化"""
        await cls.api.setup_client()
    
    @classmethod
    def teardown_class(cls):
        """テストクラス終了処理"""
        # マイルストーンレポート生成
        cls.tracker.generate_final_report()
        print("=" * 50)
        print("🏁 チャート機能統合テスト完了")
    
    @classmethod
    async def ateardown_class(cls):
        """非同期テストクラス終了処理"""
        await cls.api.cleanup_client()
    
    def setup_method(self):
        """各テストメソッド前の初期化"""
        # HTTPXクライアントの新しいインスタンスを作成
        self.api = APITestHelper()
    
    @pytest.mark.asyncio
    async def test_charts_health_check(self):
        """チャート機能ヘルスチェック"""
        print("\n📊 テスト: チャート機能ヘルスチェック")
        
        try:
            response = await self.api.get("/api/charts/health")
            
            # レスポンス検証
            assert response["status_code"] == 200
            data = response["json"]
            
            assert data["status"] == "healthy"
            assert data["service"] == "charts"
            assert "timestamp" in data
            assert "details" in data
            
            # yfinance可用性チェック
            details = data["details"]
            assert "yfinance" in details
            assert details["yfinance"] in ["available", "unavailable", "mock_mode"]
            
            self.tracker.mark_test_passed("health_check")
            print("✅ ヘルスチェック成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("health_check", str(e))
            print(f"❌ ヘルスチェック失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_data_valid_stock_code(self):
        """有効銘柄コードでのチャートデータ取得"""
        print("\n📊 テスト: 有効銘柄コードでのチャートデータ取得")
        
        try:
            # トヨタ自動車(7203)のデータを取得
            stock_code = "7203"
            response = await self.api.get(f"/api/charts/data/{stock_code}")
            
            # レスポンス検証
            assert response["status_code"] == 200
            data = response["json"]
            
            # 基本フィールド検証
            assert data["stockCode"] == stock_code
            assert data["symbol"] == f"{stock_code}.T"
            assert "stockName" in data
            assert data["timeframe"] == "1d"
            assert data["period"] == "30d"
            assert isinstance(data["dataCount"], int)
            
            # OHLCデータ検証
            ohlc_data = data.get("ohlcData", [])
            assert isinstance(ohlc_data, list)
            
            if ohlc_data:  # データがある場合
                first_candle = ohlc_data[0]
                assert "date" in first_candle
                assert "open" in first_candle
                assert "high" in first_candle
                assert "low" in first_candle
                assert "close" in first_candle
                assert "volume" in first_candle
                
                # 価格情報検証
                assert first_candle["high"] >= first_candle["low"]
                assert first_candle["volume"] >= 0
            
            # 現在価格情報検証
            current_price = data.get("currentPrice", {})
            assert "price" in current_price
            assert "change" in current_price
            assert "changeRate" in current_price
            assert "volume" in current_price
            
            self.tracker.mark_test_passed("chart_data_valid_stock")
            print(f"✅ 有効銘柄({stock_code})のチャートデータ取得成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_data_valid_stock", str(e))
            print(f"❌ 有効銘柄チャートデータ取得失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_data_with_parameters(self):
        """パラメータ付きチャートデータ取得"""
        print("\n📊 テスト: パラメータ付きチャートデータ取得")
        
        try:
            stock_code = "7203"
            params = {
                "timeframe": "1d",
                "period": "90d", 
                "indicators": "sma,rsi,macd"
            }
            
            response = await self.api.get(f"/api/charts/data/{stock_code}", params=params)
            
            # レスポンス検証
            assert response["status_code"] == 200
            data = response["json"]
            
            assert data["timeframe"] == "1d"
            assert data["period"] == "90d"
            
            # テクニカル指標検証
            technical = data.get("technicalIndicators", {})
            assert isinstance(technical, dict)
            
            # 移動平均線チェック
            if "sma20" in technical:
                assert isinstance(technical["sma20"], list)
            
            # RSIチェック
            if "rsi" in technical:
                assert isinstance(technical["rsi"], list)
                
            # MACDチェック
            if "macd" in technical:
                macd_data = technical["macd"]
                assert isinstance(macd_data, dict)
                if "macd" in macd_data:
                    assert isinstance(macd_data["macd"], list)
            
            self.tracker.mark_test_passed("chart_data_with_parameters")
            print("✅ パラメータ付きチャートデータ取得成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_data_with_parameters", str(e))
            print(f"❌ パラメータ付きチャートデータ取得失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_data_invalid_stock_code(self):
        """無効銘柄コードでのエラーハンドリング"""
        print("\n📊 テスト: 無効銘柄コードでのエラーハンドリング")
        
        try:
            # 無効な銘柄コード（文字列混在）
            invalid_code = "abcd"
            response = await self.api.get(f"/api/charts/data/{invalid_code}")
            
            # 422エラー検証（FastAPIバリデーションエラー）
            assert response["status_code"] == 422
            error_data = response["json"]
            
            assert "detail" in error_data
            # FastAPIのバリデーションエラーメッセージ確認
            assert isinstance(error_data["detail"], list)
            assert len(error_data["detail"]) > 0
            # パターンマッチエラーが含まれていることを確認
            error_msg = str(error_data["detail"][0])
            assert "should match pattern" in error_msg or "pattern" in error_msg
            
            self.tracker.mark_test_passed("chart_data_invalid_stock_code")
            print("✅ 無効銘柄コードエラーハンドリング成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_data_invalid_stock_code", str(e))
            print(f"❌ 無効銘柄コードエラーハンドリング失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio 
    async def test_chart_data_nonexistent_stock_code(self):
        """存在しない銘柄コードでのレスポンス"""
        print("\n📊 テスト: 存在しない銘柄コードでのレスポンス")
        
        try:
            # 存在しない銘柄コード（フォーマットは正しい）
            nonexistent_code = "1234"
            response = await self.api.get(f"/api/charts/data/{nonexistent_code}")
            
            # レスポンス検証（200で空データ返却）
            assert response["status_code"] == 200
            data = response["json"]
            
            assert data["stockCode"] == nonexistent_code
            assert data["success"] is False  # 空レスポンスフラグ
            assert data["dataCount"] == 0
            assert len(data["ohlcData"]) == 0
            assert "message" in data
            
            self.tracker.mark_test_passed("chart_data_nonexistent_stock_code")
            print("✅ 存在しない銘柄コードレスポンス成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_data_nonexistent_stock_code", str(e))
            print(f"❌ 存在しない銘柄コードレスポンス失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_data_response_performance(self):
        """チャートデータ取得パフォーマンス"""
        print("\n📊 テスト: チャートデータ取得パフォーマンス")
        
        try:
            import time
            
            stock_code = "7203"
            start_time = time.time()
            
            response = await self.api.get(f"/api/charts/data/{stock_code}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # レスポンス検証
            assert response["status_code"] == 200
            
            # パフォーマンス検証（30秒以内）
            assert response_time < 30.0, f"レスポンス時間が遅すぎます: {response_time:.2f}秒"
            
            self.tracker.mark_test_passed("chart_data_response_performance")
            print(f"✅ パフォーマンステスト成功 (応答時間: {response_time:.2f}秒)")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_data_response_performance", str(e))
            print(f"❌ パフォーマンステスト失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_multiple_stocks_concurrent(self):
        """複数銘柄同時チャートデータ取得"""
        print("\n📊 テスト: 複数銘柄同時チャートデータ取得")
        
        try:
            # 複数の有名銘柄で同時リクエスト
            stock_codes = ["7203", "6758", "9984"]  # トヨタ、ソニーG、SBG
            
            # 同時実行
            tasks = []
            for code in stock_codes:
                task = self.api.get(f"/api/charts/data/{code}")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 各レスポンス検証
            successful_responses = 0
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"⚠️ 銘柄 {stock_codes[i]} でエラー: {str(response)}")
                    continue
                    
                if response["status_code"] == 200:
                    successful_responses += 1
                    data = response["json"]
                    assert data["stockCode"] == stock_codes[i]
            
            # 最低2つは成功することを期待
            assert successful_responses >= 2, f"成功レスポンス数が少なすぎます: {successful_responses}"
            
            self.tracker.mark_test_passed("chart_multiple_stocks_concurrent")
            print(f"✅ 複数銘柄同時取得成功 ({successful_responses}/{len(stock_codes)}銘柄)")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_multiple_stocks_concurrent", str(e))
            print(f"❌ 複数銘柄同時取得失敗: {str(e)}")
            raise
    
    @pytest.mark.asyncio
    async def test_chart_api_integration_full_workflow(self):
        """チャートAPI統合フルワークフロー"""
        print("\n📊 テスト: チャートAPI統合フルワークフロー")
        
        try:
            stock_code = "7203"
            
            # 1. ヘルスチェック
            health_response = await self.api.get("/api/charts/health")
            assert health_response["status_code"] == 200
            
            # 2. 基本チャートデータ取得
            chart_response = await self.api.get(f"/api/charts/data/{stock_code}")
            assert chart_response["status_code"] == 200
            chart_data = chart_response["json"]
            
            # 3. 期間を変更してデータ取得
            long_period_response = await self.api.get(
                f"/api/charts/data/{stock_code}",
                params={"period": "1y"}
            )
            assert long_period_response["status_code"] == 200
            long_data = long_period_response["json"]
            
            # データ件数比較（1年 > 30日）
            if long_data["dataCount"] > 0 and chart_data["dataCount"] > 0:
                assert long_data["dataCount"] >= chart_data["dataCount"]
            
            # 4. テクニカル指標付きデータ取得
            technical_response = await self.api.get(
                f"/api/charts/data/{stock_code}",
                params={"indicators": "sma,rsi,bollinger"}
            )
            assert technical_response["status_code"] == 200
            technical_data = technical_response["json"]
            
            # テクニカル指標存在確認
            technical_indicators = technical_data.get("technicalIndicators", {})
            assert isinstance(technical_indicators, dict)
            
            self.tracker.mark_test_passed("chart_api_integration_full_workflow")
            print("✅ チャートAPI統合フルワークフロー成功")
            
        except Exception as e:
            self.tracker.mark_test_failed("chart_api_integration_full_workflow", str(e))
            print(f"❌ チャートAPI統合フルワークフロー失敗: {str(e)}")
            raise

# スタンドアロン実行
if __name__ == "__main__":
    pytest.main([__file__, "-v"])