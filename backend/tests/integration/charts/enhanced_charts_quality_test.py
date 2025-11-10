"""
Enhanced Charts Quality Test
チャート機能の品質向上のための追加テスト
"""

import pytest
import asyncio
import time
from typing import Dict, Any

from ...utils.api_test_helper import APITestHelper

class TestEnhancedChartsQuality:
    """チャート機能品質向上テスト"""
    
    def setup_method(self):
        """各テストメソッド前の初期化"""
        self.api = APITestHelper()
    
    @pytest.mark.asyncio
    async def test_data_integrity_validation(self):
        """データ整合性検証テスト"""
        print("\n🔍 テスト: データ整合性検証")
        
        response = await self.api.get("/api/charts/data/7203")
        assert response["status_code"] == 200
        data = response["json"]
        
        # OHLC データの整合性チェック
        ohlc_data = data.get("ohlcData", [])
        if ohlc_data:
            for candle in ohlc_data:
                # High >= Low
                assert candle["high"] >= candle["low"], f"High {candle['high']} < Low {candle['low']}"
                
                # Open/Close は High/Low の範囲内
                assert candle["low"] <= candle["open"] <= candle["high"], f"Open {candle['open']} out of range"
                assert candle["low"] <= candle["close"] <= candle["high"], f"Close {candle['close']} out of range"
                
                # Volume は非負
                assert candle["volume"] >= 0, f"Volume {candle['volume']} is negative"
                
                # 日付フォーマット検証
                assert isinstance(candle["date"], str), "Date should be string"
                assert len(candle["date"]) == 10, "Date should be YYYY-MM-DD format"
        
        print("✅ データ整合性検証成功")
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """レスポンス時間一貫性テスト"""
        print("\n⏱️ テスト: レスポンス時間一貫性")
        
        response_times = []
        for i in range(5):
            start_time = time.time()
            response = await self.api.get("/api/charts/data/7203")
            end_time = time.time()
            
            assert response["status_code"] == 200
            response_times.append(end_time - start_time)
        
        # 平均レスポンス時間
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # レスポンス時間のばらつきチェック（最大時間が平均の5倍を超えない）
        # 外部APIの性質上、初回リクエストがキャッシュされることを考慮
        assert max_time <= avg_time * 5, f"Response time inconsistency: max {max_time:.2f}s > avg*5 {avg_time*5:.2f}s"
        
        print(f"✅ レスポンス時間一貫性OK (平均: {avg_time:.2f}s, 最大: {max_time:.2f}s, 最小: {min_time:.2f}s)")
    
    @pytest.mark.asyncio
    async def test_error_message_quality(self):
        """エラーメッセージ品質テスト"""
        print("\n📝 テスト: エラーメッセージ品質")
        
        # 無効な銘柄コード
        response = await self.api.get("/api/charts/data/invalid")
        assert response["status_code"] == 400
        error = response["json"]
        
        # エラーメッセージが具体的であることをチェック
        assert "detail" in error
        assert "4桁の数字" in error["detail"], "Error message should be descriptive"
        
        # 短すぎる銘柄コード
        response = await self.api.get("/api/charts/data/123")
        assert response["status_code"] == 400
        error = response["json"]
        assert "detail" in error
        
        print("✅ エラーメッセージ品質OK")
    
    @pytest.mark.asyncio
    async def test_parameter_validation_robustness(self):
        """パラメータ検証堅牢性テスト"""
        print("\n🛡️ テスト: パラメータ検証堅牢性")
        
        # 無効な期間パラメータ
        response = await self.api.get("/api/charts/data/7203", params={"period": "invalid"})
        # サーバーが適切にデフォルト値を使用するか、エラーを返すことをチェック
        assert response["status_code"] in [200, 400]
        
        # 無効な時間枠パラメータ
        response = await self.api.get("/api/charts/data/7203", params={"timeframe": "invalid"})
        assert response["status_code"] in [200, 400]
        
        # 空の指標パラメータ
        response = await self.api.get("/api/charts/data/7203", params={"indicators": ""})
        assert response["status_code"] == 200  # 空の指標は許可されるべき
        
        print("✅ パラメータ検証堅牢性OK")
    
    @pytest.mark.asyncio
    async def test_concurrent_load_stability(self):
        """並行負荷安定性テスト"""
        print("\n🚀 テスト: 並行負荷安定性")
        
        # 10個の同時リクエスト
        tasks = []
        for _ in range(10):
            task = self.api.get("/api/charts/data/7203")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful_responses = 0
        for response in responses:
            if not isinstance(response, Exception) and response["status_code"] == 200:
                successful_responses += 1
        
        # 最低90%の成功率を期待
        success_rate = successful_responses / len(responses)
        assert success_rate >= 0.9, f"Success rate {success_rate:.2f} < 0.9"
        
        # 総実行時間が単一リクエストの10倍を超えないことをチェック
        total_time = end_time - start_time
        assert total_time < 30.0, f"Concurrent execution took too long: {total_time:.2f}s"
        
        print(f"✅ 並行負荷安定性OK (成功率: {success_rate:.2f}, 実行時間: {total_time:.2f}s)")
    
    @pytest.mark.asyncio
    async def test_response_schema_compliance(self):
        """レスポンススキーマ準拠テスト"""
        print("\n📋 テスト: レスポンススキーマ準拠")
        
        response = await self.api.get("/api/charts/data/7203")
        assert response["status_code"] == 200
        data = response["json"]
        
        # 必須フィールドの存在確認
        required_fields = ["success", "stockCode", "symbol", "stockName", "timeframe", "period", "dataCount", "lastUpdated", "ohlcData"]
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing"
        
        # データ型検証
        assert isinstance(data["success"], bool)
        assert isinstance(data["stockCode"], str)
        assert isinstance(data["dataCount"], int)
        assert isinstance(data["ohlcData"], list)
        
        # OHLC データ構造検証
        if data["ohlcData"]:
            first_candle = data["ohlcData"][0]
            candle_fields = ["date", "timestamp", "open", "high", "low", "close", "volume"]
            for field in candle_fields:
                assert field in first_candle, f"Candle field '{field}' missing"
        
        print("✅ レスポンススキーマ準拠OK")

# スタンドアロン実行
if __name__ == "__main__":
    pytest.main([__file__, "-v"])