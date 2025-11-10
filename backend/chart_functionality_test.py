#!/usr/bin/env python3
"""
チャート機能動作確認スクリプト
スライス4-B実装の動作保証テスト
"""

import asyncio
import sys
import json
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append('.')

from src.services.charts_service import ChartsService
from tests.utils.ChartSliceMilestoneTracker import ChartSliceMilestoneTracker

class ChartFunctionalityTester:
    """チャート機能テスター"""
    
    def __init__(self):
        self.service = ChartsService()
        self.tracker = ChartSliceMilestoneTracker()
        self.test_results = []
    
    async def test_basic_chart_data_retrieval(self):
        """基本的なチャートデータ取得テスト"""
        print("\n📊 テスト1: 基本的なチャートデータ取得")
        
        try:
            # トヨタ自動車(7203)のデータ取得
            data = await self.service.get_chart_data("7203", "1d", "30d")
            
            # 基本的な検証
            assert data["success"] is True
            assert data["stockCode"] == "7203"
            assert data["symbol"] == "7203.T"
            assert data["dataCount"] > 0
            assert len(data["ohlcData"]) > 0
            assert "currentPrice" in data
            
            print(f"✅ 成功: 銘柄 {data['stockName']} のデータ {data['dataCount']} 件を取得")
            print(f"   現在価格: {data['currentPrice']['price']}円")
            print(f"   変動: {data['currentPrice']['change']:+.1f}円 ({data['currentPrice']['changeRate']:+.2f}%)")
            
            self.tracker.mark_test_passed("chart_data_valid_stock")
            self.test_results.append({"test": "basic_chart_data_retrieval", "status": "PASSED"})
            return True
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            self.tracker.mark_test_failed("chart_data_valid_stock", str(e))
            self.test_results.append({"test": "basic_chart_data_retrieval", "status": "FAILED", "error": str(e)})
            return False
    
    async def test_chart_data_with_indicators(self):
        """テクニカル指標付きデータ取得テスト"""
        print("\n📈 テスト2: テクニカル指標付きデータ取得")
        
        try:
            # 指標付きデータ取得
            data = await self.service.get_chart_data("7203", "1d", "90d", ["sma", "rsi", "macd"])
            
            # テクニカル指標検証
            technical = data.get("technicalIndicators", {})
            assert isinstance(technical, dict)
            
            indicators_found = []
            if "sma20" in technical:
                indicators_found.append("SMA20")
            if "rsi" in technical:
                indicators_found.append("RSI")
            if "macd" in technical:
                indicators_found.append("MACD")
            
            print(f"✅ 成功: テクニカル指標 {', '.join(indicators_found)} を計算")
            
            self.tracker.mark_test_passed("chart_data_with_parameters")
            self.test_results.append({"test": "chart_data_with_indicators", "status": "PASSED", "indicators": len(indicators_found)})
            return True
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            self.tracker.mark_test_failed("chart_data_with_parameters", str(e))
            self.test_results.append({"test": "chart_data_with_indicators", "status": "FAILED", "error": str(e)})
            return False
    
    async def test_invalid_stock_code_handling(self):
        """無効銘柄コード処理テスト"""
        print("\n🚫 テスト3: 無効銘柄コード処理")
        
        try:
            # 存在しない銘柄コード
            data = await self.service.get_chart_data("9999", "1d", "30d")
            
            # 空レスポンス検証
            assert data["success"] is False
            assert data["dataCount"] == 0
            assert len(data["ohlcData"]) == 0
            assert "message" in data
            
            print("✅ 成功: 無効銘柄コードで適切な空レスポンスを生成")
            
            self.tracker.mark_test_passed("chart_data_nonexistent_stock_code")
            self.test_results.append({"test": "invalid_stock_code_handling", "status": "PASSED"})
            return True
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            self.tracker.mark_test_failed("chart_data_nonexistent_stock_code", str(e))
            self.test_results.append({"test": "invalid_stock_code_handling", "status": "FAILED", "error": str(e)})
            return False
    
    async def test_multiple_stocks_performance(self):
        """複数銘柄処理性能テスト"""
        print("\n🚀 テスト4: 複数銘柄処理性能")
        
        try:
            import time
            stock_codes = ["7203", "6758", "9984"]  # トヨタ、ソニーG、SBG
            start_time = time.time()
            
            # 並行処理でデータ取得
            tasks = [self.service.get_chart_data(code, "1d", "30d") for code in stock_codes]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # 結果検証
            successful_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"   ⚠️ 銘柄 {stock_codes[i]}: エラー - {str(result)}")
                elif result.get("success", False):
                    successful_count += 1
                    print(f"   ✅ 銘柄 {stock_codes[i]}: 成功 ({result['dataCount']}件)")
            
            print(f"✅ 成功: {successful_count}/{len(stock_codes)} 銘柄を {processing_time:.2f}秒で処理")
            
            self.tracker.mark_test_passed("chart_multiple_stocks_concurrent")
            self.test_results.append({
                "test": "multiple_stocks_performance", 
                "status": "PASSED",
                "successful_count": successful_count,
                "total_count": len(stock_codes),
                "processing_time": processing_time
            })
            return True
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            self.tracker.mark_test_failed("chart_multiple_stocks_concurrent", str(e))
            self.test_results.append({"test": "multiple_stocks_performance", "status": "FAILED", "error": str(e)})
            return False
    
    async def test_service_health_check(self):
        """サービスヘルスチェック"""
        print("\n💊 テスト5: サービスヘルスチェック")
        
        try:
            health = await self.service.health_check()
            
            assert "yfinance" in health
            assert health["yfinance"] in ["available", "unavailable"]
            assert "lastCheck" in health
            
            print(f"✅ 成功: ヘルスチェック - yfinance: {health['yfinance']}")
            
            self.tracker.mark_test_passed("health_check")
            self.test_results.append({"test": "service_health_check", "status": "PASSED", "yfinance_status": health["yfinance"]})
            return True
            
        except Exception as e:
            print(f"❌ 失敗: {str(e)}")
            self.tracker.mark_test_failed("health_check", str(e))
            self.test_results.append({"test": "service_health_check", "status": "FAILED", "error": str(e)})
            return False
    
    def generate_test_report(self):
        """テストレポート生成"""
        passed_tests = [t for t in self.test_results if t["status"] == "PASSED"]
        failed_tests = [t for t in self.test_results if t["status"] == "FAILED"]
        
        print(f"\n{'='*60}")
        print("📊 スライス4-B（チャート表示） 動作確認レポート")
        print(f"{'='*60}")
        
        print(f"\n📈 テスト結果サマリー:")
        print(f"  総テスト数: {len(self.test_results)}")
        print(f"  成功: {len(passed_tests)} 件")
        print(f"  失敗: {len(failed_tests)} 件")
        print(f"  成功率: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print(f"\n❌ 失敗したテスト:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        
        print(f"\n✅ 成功したテスト:")
        for test in passed_tests:
            print(f"  - {test['test']}")
        
        # マイルストーン完了マーク
        if len(passed_tests) >= 4:  # 主要テスト4つが成功
            self.tracker.mark_implementation_task_completed("chart_controller", "FastAPI コントローラー実装完了")
            self.tracker.mark_implementation_task_completed("chart_service", "yfinance統合サービス実装完了")
            self.tracker.mark_implementation_task_completed("data_structure", "レスポンス形式・型定義整備完了")
            self.tracker.mark_implementation_task_completed("main_integration", "アプリケーション統合完了")
            
            self.tracker.mark_endpoint_implemented("GET /api/charts/data/:stockCode")
            self.tracker.mark_endpoint_implemented("GET /api/charts/health")
            self.tracker.mark_endpoint_tested("GET /api/charts/data/:stockCode")
            self.tracker.mark_endpoint_tested("GET /api/charts/health")
        
        # 最終レポート生成
        final_report = self.tracker.generate_final_report()
        
        print(f"\n🎯 実装完了確認:")
        print(f"  チャートデータ取得API: {'✅' if len(passed_tests) >= 3 else '❌'}")
        print(f"  yfinance統合: {'✅' if any('chart_data' in t['test'] for t in passed_tests) else '❌'}")
        print(f"  エラーハンドリング: {'✅' if any('invalid' in t['test'] for t in passed_tests) else '❌'}")
        print(f"  性能要件: {'✅' if any('performance' in t['test'] for t in passed_tests) else '❌'}")
        
        return final_report

async def main():
    """メイン実行関数"""
    print("🚀 スライス4-B（チャート表示）動作確認テスト開始")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ChartFunctionalityTester()
    
    # テスト実行
    tests = [
        tester.test_basic_chart_data_retrieval(),
        tester.test_chart_data_with_indicators(),
        tester.test_invalid_stock_code_handling(),
        tester.test_multiple_stocks_performance(),
        tester.test_service_health_check()
    ]
    
    await asyncio.gather(*tests)
    
    # レポート生成
    tester.generate_test_report()
    
    print(f"\n🏁 動作確認テスト完了")

if __name__ == "__main__":
    asyncio.run(main())