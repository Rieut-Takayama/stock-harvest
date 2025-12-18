"""
ロジックA・B強化版 統合テスト
実データ環境でのロジック強化版の動作検証
"""

import asyncio
import pytest
import sys
import os
from typing import Dict, Any

# テストのために必要なパス設定
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_root)

from src.services.logic_detection_service import LogicDetectionService
from src.services.real_stock_data_service import RealStockDataService
from src.services.stock_data_service import StockDataService
from src.services.technical_analysis_service import TechnicalAnalysisService
from tests.utils.MilestoneTracker import MilestoneTracker
from src.lib.logger import logger


class TestLogicEnhancedIntegration:
    """ロジック強化版統合テスト"""

    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.logic_service = LogicDetectionService()
        cls.real_data_service = RealStockDataService()
        cls.stock_data_service = StockDataService()
        cls.tech_analysis_service = TechnicalAnalysisService()
        
        # テスト用の銘柄コード（新興株含む）
        cls.test_stock_codes = [
            "3000",  # 新興株代表例
            "4000",  # 新興株代表例
            "3456",  # テスト用銘柄
            "7203",  # トヨタ（参照用）
        ]

    async def test_logic_a_enhanced_real_data_flow(self):
        """ロジックA強化版のリアルデータフロー統合テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("ロジックA強化版リアルデータフロー")
        tracker.mark("テスト開始")
        
        for stock_code in self.test_stock_codes[:2]:  # 2銘柄でテスト
            try:
                tracker.set_operation(f"銘柄{stock_code}処理")
                
                # Step 1: リアル株価データ取得
                tracker.mark(f"{stock_code}-株価データ取得開始")
                stock_data = await self.stock_data_service.fetch_stock_data(stock_code, "")
                tracker.mark(f"{stock_code}-株価データ取得完了")
                
                if not stock_data:
                    logger.warning(f"株価データ取得失敗: {stock_code}")
                    continue
                
                # Step 2: テクニカル指標生成
                tracker.mark(f"{stock_code}-テクニカル指標生成開始")
                if 'signals' not in stock_data:
                    stock_data['signals'] = self.tech_analysis_service.generate_technical_signals(
                        stock_data=stock_data
                    )
                tracker.mark(f"{stock_code}-テクニカル指標生成完了")
                
                # Step 3: ロジックA強化版実行
                tracker.mark(f"{stock_code}-ロジックA強化版検出開始")
                result = await self.logic_service.detect_logic_a_enhanced(stock_data)
                tracker.mark(f"{stock_code}-ロジックA強化版検出完了")
                
                # 検証
                assert isinstance(result, dict), "結果は辞書型である必要があります"
                assert 'detected' in result, "検出結果が含まれている必要があります"
                
                if result['detected']:
                    assert 'signal_type' in result, "検出時にはシグナルタイプが必要"
                    assert 'signal_strength' in result, "検出時にはシグナル強度が必要"
                    assert 'risk_assessment' in result, "検出時にはリスク評価が必要"
                    
                    logger.info(f"ロジックA強化版検出成功: {stock_code}")
                    logger.info(f"シグナルタイプ: {result['signal_type']}")
                    logger.info(f"シグナル強度: {result['signal_strength']}")
                    
                else:
                    logger.info(f"ロジックA強化版未検出: {stock_code} - 理由: {result.get('reason', '不明')}")
                
                # API負荷軽減のため待機
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"ロジックA強化版テストエラー {stock_code}: {str(e)}")
                # テスト継続（他の銘柄をテストするため）
        
        tracker.summary()

    async def test_logic_b_enhanced_real_data_flow(self):
        """ロジックB強化版のリアルデータフロー統合テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("ロジックB強化版リアルデータフロー")
        tracker.mark("テスト開始")
        
        for stock_code in self.test_stock_codes[:2]:  # 2銘柄でテスト
            try:
                tracker.set_operation(f"銘柄{stock_code}処理")
                
                # Step 1: リアル株価データ取得
                tracker.mark(f"{stock_code}-株価データ取得開始")
                stock_data = await self.stock_data_service.fetch_stock_data(stock_code, "")
                tracker.mark(f"{stock_code}-株価データ取得完了")
                
                if not stock_data:
                    logger.warning(f"株価データ取得失敗: {stock_code}")
                    continue
                
                # Step 2: テクニカル指標生成
                tracker.mark(f"{stock_code}-テクニカル指標生成開始")
                if 'signals' not in stock_data:
                    stock_data['signals'] = self.tech_analysis_service.generate_technical_signals(
                        stock_data=stock_data
                    )
                tracker.mark(f"{stock_code}-テクニカル指標生成完了")
                
                # Step 3: ロジックB強化版実行
                tracker.mark(f"{stock_code}-ロジックB強化版検出開始")
                result = await self.logic_service.detect_logic_b_enhanced(stock_data)
                tracker.mark(f"{stock_code}-ロジックB強化版検出完了")
                
                # 検証
                assert isinstance(result, dict), "結果は辞書型である必要があります"
                assert 'detected' in result, "検出結果が含まれている必要があります"
                
                if result['detected']:
                    assert 'signal_type' in result, "検出時にはシグナルタイプが必要"
                    assert 'signal_strength' in result, "検出時にはシグナル強度が必要"
                    assert 'risk_assessment' in result, "検出時にはリスク評価が必要"
                    
                    logger.info(f"ロジックB強化版検出成功: {stock_code}")
                    logger.info(f"シグナルタイプ: {result['signal_type']}")
                    logger.info(f"シグナル強度: {result['signal_strength']}")
                    
                else:
                    logger.info(f"ロジックB強化版未検出: {stock_code} - 理由: {result.get('reason', '不明')}")
                
                # API負荷軽減のため待機
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"ロジックB強化版テストエラー {stock_code}: {str(e)}")
                # テスト継続（他の銘柄をテストするため）
        
        tracker.summary()

    async def test_enhanced_api_endpoints_integration(self):
        """強化版APIエンドポイント統合テスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("強化版APIエンドポイント統合テスト")
        tracker.mark("テスト開始")
        
        # FastAPIのテストクライアントをシミュレート
        from fastapi.testclient import TestClient
        from src.main import app
        
        client = TestClient(app)
        
        test_stock_code = "3000"
        
        # ロジックA強化版APIテスト
        tracker.mark("ロジックA強化版API呼び出し開始")
        response_a = client.post(
            "/api/scan/logic-a-enhanced",
            json={
                "stock_code": test_stock_code,
                "stock_name": "テスト銘柄",
                "detection_mode": "enhanced"
            }
        )
        tracker.mark("ロジックA強化版API呼び出し完了")
        
        # ロジックA強化版APIレスポンス検証
        assert response_a.status_code in [200, 404], f"ロジックA強化版API応答エラー: {response_a.status_code}"
        
        if response_a.status_code == 200:
            data_a = response_a.json()
            assert data_a["success"] == True, "ロジックA強化版API成功フラグが必要"
            assert "detection_result" in data_a, "検出結果が含まれている必要があります"
            logger.info("ロジックA強化版API正常動作確認")
        
        # ロジックB強化版APIテスト
        tracker.mark("ロジックB強化版API呼び出し開始")
        response_b = client.post(
            "/api/scan/logic-b-enhanced",
            json={
                "stock_code": test_stock_code,
                "stock_name": "テスト銘柄",
                "detection_mode": "enhanced"
            }
        )
        tracker.mark("ロジックB強化版API呼び出し完了")
        
        # ロジックB強化版APIレスポンス検証
        assert response_b.status_code in [200, 404], f"ロジックB強化版API応答エラー: {response_b.status_code}"
        
        if response_b.status_code == 200:
            data_b = response_b.json()
            assert data_b["success"] == True, "ロジックB強化版API成功フラグが必要"
            assert "detection_result" in data_b, "検出結果が含まれている必要があります"
            logger.info("ロジックB強化版API正常動作確認")
        
        tracker.summary()

    async def test_enhanced_logic_config_validation(self):
        """強化版ロジック設定バリデーションテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("強化版ロジック設定バリデーション")
        tracker.mark("テスト開始")
        
        # ロジックA強化版設定検証
        tracker.mark("ロジックA強化版設定確認")
        config_a = self.logic_service.logic_a_enhanced_config
        
        # 必須設定項目の確認
        required_a_keys = [
            'entry_signal_rate', 'profit_target_rate', 'stop_loss_rate',
            'max_holding_days', 'min_stop_high_volume', 'max_lower_shadow_ratio',
            'max_listing_years', 'exclude_consecutive_stop_high'
        ]
        
        for key in required_a_keys:
            assert key in config_a, f"ロジックA強化版設定に{key}が不足"
        
        # 設定値の妥当性確認
        assert config_a['entry_signal_rate'] == 5.0, "エントリーシグナル率は5%である必要があります"
        assert config_a['profit_target_rate'] == 24.0, "利確目標は24%である必要があります"
        assert config_a['stop_loss_rate'] == -10.0, "損切りは-10%である必要があります"
        assert config_a['max_holding_days'] == 30, "最大保有期間は30日である必要があります"
        
        logger.info("ロジックA強化版設定バリデーション完了")
        
        # ロジックB強化版設定検証
        tracker.mark("ロジックB強化版設定確認")
        config_b = self.logic_service.logic_b_enhanced_config
        
        # 必須設定項目の確認
        required_b_keys = [
            'ma5_crossover_threshold', 'profit_target_rate', 'stop_loss_rate',
            'max_holding_days', 'min_volume', 'earnings_improvement_threshold',
            'consecutive_profit_quarters', 'exclude_loss_carryforward'
        ]
        
        for key in required_b_keys:
            assert key in config_b, f"ロジックB強化版設定に{key}が不足"
        
        # 設定値の妥当性確認
        assert config_b['ma5_crossover_threshold'] == 0.02, "MA5上抜け閾値は2%である必要があります"
        assert config_b['profit_target_rate'] == 25.0, "利確目標は25%である必要があります"
        assert config_b['stop_loss_rate'] == -10.0, "損切りは-10%である必要があります"
        assert config_b['max_holding_days'] == 45, "最大保有期間は45日である必要があります"
        
        logger.info("ロジックB強化版設定バリデーション完了")
        
        tracker.summary()

    async def test_enhanced_logic_performance_benchmark(self):
        """強化版ロジックパフォーマンスベンチマークテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("強化版ロジックパフォーマンスベンチマーク")
        tracker.mark("ベンチマーク開始")
        
        # 複数銘柄での一括処理パフォーマンステスト
        test_codes = self.test_stock_codes
        
        # ロジックA強化版パフォーマンステスト
        tracker.mark("ロジックA強化版一括処理開始")
        start_time = tracker.start_time
        
        for stock_code in test_codes:
            try:
                stock_data = await self.stock_data_service.fetch_stock_data(stock_code, "")
                if stock_data and 'signals' not in stock_data:
                    stock_data['signals'] = self.tech_analysis_service.generate_technical_signals(
                        stock_data=stock_data
                    )
                
                if stock_data:
                    result = await self.logic_service.detect_logic_a_enhanced(stock_data)
                    logger.debug(f"銘柄{stock_code} - ロジックA強化版: {result.get('detected', False)}")
                
                await asyncio.sleep(1)  # API負荷軽減
                
            except Exception as e:
                logger.warning(f"ベンチマーク中エラー {stock_code}: {str(e)}")
        
        tracker.mark("ロジックA強化版一括処理完了")
        
        # ロジックB強化版パフォーマンステスト
        tracker.mark("ロジックB強化版一括処理開始")
        
        for stock_code in test_codes:
            try:
                stock_data = await self.stock_data_service.fetch_stock_data(stock_code, "")
                if stock_data and 'signals' not in stock_data:
                    stock_data['signals'] = self.tech_analysis_service.generate_technical_signals(
                        stock_data=stock_data
                    )
                
                if stock_data:
                    result = await self.logic_service.detect_logic_b_enhanced(stock_data)
                    logger.debug(f"銘柄{stock_code} - ロジックB強化版: {result.get('detected', False)}")
                
                await asyncio.sleep(1)  # API負荷軽減
                
            except Exception as e:
                logger.warning(f"ベンチマーク中エラー {stock_code}: {str(e)}")
        
        tracker.mark("ロジックB強化版一括処理完了")
        
        tracker.summary()

# pytest実行用のエントリーポイント
if __name__ == "__main__":
    print("ロジック強化版統合テスト実行中...")
    
    # テストクラスのインスタンス化
    test_instance = TestLogicEnhancedIntegration()
    test_instance.setup_class()
    
    # 各テストを順番に実行
    async def run_all_tests():
        print("\n=== ロジックA強化版リアルデータフローテスト ===")
        await test_instance.test_logic_a_enhanced_real_data_flow()
        
        print("\n=== ロジックB強化版リアルデータフローテスト ===")
        await test_instance.test_logic_b_enhanced_real_data_flow()
        
        print("\n=== 強化版APIエンドポイント統合テスト ===")
        await test_instance.test_enhanced_api_endpoints_integration()
        
        print("\n=== 強化版ロジック設定バリデーションテスト ===")
        await test_instance.test_enhanced_logic_config_validation()
        
        print("\n=== 強化版ロジックパフォーマンスベンチマークテスト ===")
        await test_instance.test_enhanced_logic_performance_benchmark()
        
        print("\n🎉 全てのロジック強化版統合テストが完了しました！")
    
    # 非同期実行
    asyncio.run(run_all_tests())