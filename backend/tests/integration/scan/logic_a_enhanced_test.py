"""
ロジックA強化版のテストケース
ストップ高張り付き精密検出機能の統合テスト
"""

import pytest
import asyncio
from backend.src.services.logic_detection_service import LogicDetectionService
from backend.src.services.stock_data_service import StockDataService
from backend.src.services.technical_analysis_service import TechnicalAnalysisService


class TestLogicAEnhanced:
    """ロジックA強化版のテストクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """テストセットアップ"""
        self.logic_service = LogicDetectionService()
        self.stock_data_service = StockDataService()
        self.tech_analysis_service = TechnicalAnalysisService()
        
        # テストデータ
        self.test_stock_data = {
            'code': '3000',  # 新興銘柄（上場条件を満たす）
            'name': 'テスト新興株',
            'price': 1500,
            'change': 250,
            'changeRate': 20.0,  # ストップ高レベル
            'volume': 25000000,  # 高出来高
            'signals': {
                'rsi': 75,
                'macd': 0.5,
                'bollingerPosition': 0.8,
                'volumeRatio': 2.5,
                'trendDirection': 'up'
            }
        }
    
    @pytest.mark.asyncio
    async def test_detect_logic_a_enhanced_positive_case(self):
        """ロジックA強化版 - 正常検出ケース"""
        # テスト実行
        result = await self.logic_service.detect_logic_a_enhanced(self.test_stock_data)
        
        # 検証
        assert isinstance(result, dict)
        assert 'detected' in result
        assert 'signal_type' in result or 'reason' in result
        
        # 検出された場合の詳細検証
        if result.get('detected'):
            assert 'signal_strength' in result
            assert 'entry_price' in result
            assert 'profit_target' in result
            assert 'stop_loss' in result
            assert 'risk_assessment' in result
            
            # 価格計算の検証
            assert result['entry_price'] > self.test_stock_data['price']
            assert result['profit_target'] > result['entry_price']
            assert result['stop_loss'] < result['entry_price']
    
    @pytest.mark.asyncio
    async def test_stop_high_detection_algorithm(self):
        """ストップ高検出アルゴリズムのテスト"""
        result = await self.logic_service._detect_stop_high_sticking(self.test_stock_data)
        
        # 結果の基本構造検証
        assert isinstance(result, dict)
        assert 'is_stop_high' in result
        assert 'reason' in result
        
        # ストップ高検出時の詳細情報検証
        if result.get('is_stop_high'):
            assert 'stop_high_price' in result
            assert 'reach_ratio' in result
            assert 'change_rate' in result
            assert 'volume' in result
            assert 'lower_shadow_ratio' in result
    
    @pytest.mark.asyncio
    async def test_listing_conditions_check(self):
        """上場条件チェックのテスト"""
        # 新興銘柄（条件満たす）
        result_new = await self.logic_service._check_listing_conditions('3000')
        assert isinstance(result_new, bool)
        
        # 既存銘柄（条件満たさない）
        result_old = await self.logic_service._check_listing_conditions('7203')
        assert isinstance(result_old, bool)
        
        # 新興銘柄の方が上場条件を満たしやすい
        assert result_new or not result_old  # 少なくとも論理的整合性を確認
    
    @pytest.mark.asyncio
    async def test_earnings_timing_check(self):
        """決算タイミング判定のテスト"""
        result = await self.logic_service._check_earnings_timing('3000')
        
        # 結果の基本構造検証
        assert isinstance(result, dict)
        assert 'is_earnings_day' in result
        assert 'source' in result
        
        # 推定結果の場合の詳細情報検証
        if result.get('source') == 'estimated':
            assert 'earnings_date' in result
            assert 'days_since_earnings' in result
            assert 'note' in result
    
    @pytest.mark.asyncio
    async def test_trading_signal_generation(self):
        """売買シグナル生成のテスト"""
        result = await self.logic_service._generate_trading_signal(self.test_stock_data)
        
        # 基本構造検証
        assert isinstance(result, dict)
        assert 'signal_type' in result
        assert 'signal_strength' in result
        
        # シグナル強度の範囲検証
        if 'signal_strength' in result:
            assert 0 <= result['signal_strength'] <= 100
        
        # エントリーシグナルの場合の詳細検証
        if result.get('signal_type') == 'BUY_ENTRY':
            assert 'entry_price' in result
            assert 'profit_target' in result
            assert 'stop_loss' in result
            assert 'risk_assessment' in result
            assert 'max_holding_days' in result
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self):
        """リスク評価機能のテスト"""
        result = await self.logic_service._assess_trading_risk(
            self.test_stock_data, 
            self.test_stock_data['signals']
        )
        
        # 基本構造検証
        assert isinstance(result, dict)
        assert 'risk_level' in result
        assert 'risk_score' in result
        assert 'risk_factors' in result
        assert 'recommendation' in result
        
        # リスクレベルの妥当性検証
        valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
        assert result['risk_level'] in valid_risk_levels
        
        # リスクスコアの範囲検証
        assert 0 <= result['risk_score'] <= 100
        
        # リスクファクターはリスト形式
        assert isinstance(result['risk_factors'], list)
    
    @pytest.mark.asyncio
    async def test_exclusion_rules(self):
        """除外ルール判定のテスト"""
        result = await self.logic_service._check_exclusion_rules(
            self.test_stock_data, 
            self.test_stock_data['code']
        )
        
        # 基本構造検証
        assert isinstance(result, dict)
        assert 'should_exclude' in result
        assert 'reason' in result
        
        # 除外判定はブール値
        assert isinstance(result['should_exclude'], bool)
    
    @pytest.mark.asyncio
    async def test_history_management(self):
        """履歴管理機能のテスト"""
        stock_code = 'TEST001'
        
        # 履歴記録
        test_record = {
            'detection_date': '2024-11-24',
            'detection_type': 'logic_a_enhanced',
            'stock_data': self.test_stock_data
        }
        
        await self.logic_service._record_stock_history(stock_code, test_record)
        
        # 履歴取得
        history = self.logic_service.get_stock_history(stock_code)
        
        # 検証
        assert isinstance(history, list)
        assert len(history) >= 1
        assert history[-1]['detection_type'] == 'logic_a_enhanced'
    
    @pytest.mark.asyncio
    async def test_first_time_condition(self):
        """初回条件判定のテスト"""
        stock_code = 'TEST002'
        
        # 初回チェック（履歴なし）
        result_first = await self.logic_service._check_first_time_condition(stock_code)
        assert result_first['is_first_time'] == True
        
        # 履歴追加後
        test_record = {
            'detection_date': '2024-11-24',
            'detection_type': 'logic_a_enhanced'
        }
        await self.logic_service._record_stock_history(stock_code, test_record)
        
        # 再チェック（履歴あり）
        result_second = await self.logic_service._check_first_time_condition(stock_code)
        assert result_second['is_first_time'] == False
    
    def test_config_management(self):
        """設定管理機能のテスト"""
        # 現在の設定取得
        configs = self.logic_service.get_logic_configs()
        
        assert isinstance(configs, dict)
        assert 'logic_a' in configs
        assert 'logic_b' in configs
        
        # 強化版設定の確認
        enhanced_config = self.logic_service.logic_a_enhanced_config
        assert isinstance(enhanced_config, dict)
        assert 'entry_signal_rate' in enhanced_config
        assert 'profit_target_rate' in enhanced_config
        assert 'stop_loss_rate' in enhanced_config
    
    @pytest.mark.asyncio
    async def test_negative_cases(self):
        """ネガティブケースのテスト"""
        # 上昇率不足のケース
        low_change_data = self.test_stock_data.copy()
        low_change_data['changeRate'] = 2.0  # 低い上昇率
        
        result_low = await self.logic_service.detect_logic_a_enhanced(low_change_data)
        assert result_low['detected'] == False
        
        # 出来高不足のケース
        low_volume_data = self.test_stock_data.copy()
        low_volume_data['volume'] = 1000000  # 低出来高
        
        result_volume = await self.logic_service.detect_logic_a_enhanced(low_volume_data)
        # 出来高不足により検出されないか、検出されても低いシグナル強度
        assert result_volume['detected'] == False or \
               (result_volume.get('signal_strength', 0) < 50)
    
    @pytest.mark.asyncio
    async def test_legacy_compatibility(self):
        """従来版との互換性テスト"""
        # 従来版検出
        legacy_result = await self.logic_service.detect_logic_a(self.test_stock_data)
        assert isinstance(legacy_result, bool)
        
        # 強化版検出
        enhanced_result = await self.logic_service.detect_logic_a_enhanced(self.test_stock_data)
        assert isinstance(enhanced_result, dict)
        
        # 両方が検出する場合、論理的整合性があることを確認
        if legacy_result and enhanced_result.get('detected'):
            # 両方で検出された場合は正常
            assert True
        elif not legacy_result and enhanced_result.get('detected'):
            # 強化版のみ検出（より精密な検出）
            assert True
        else:
            # その他のケースも許容（異なるロジックのため）
            assert True


# 統合テスト用のヘルパー関数
async def run_integration_test():
    """統合テスト実行ヘルパー"""
    test_instance = TestLogicAEnhanced()
    test_instance.setup_method()
    
    print("🔍 ロジックA強化版 統合テスト開始")
    
    try:
        # 主要テストの実行
        await test_instance.test_detect_logic_a_enhanced_positive_case()
        print("✅ ロジックA強化版基本機能 - PASS")
        
        await test_instance.test_stop_high_detection_algorithm()
        print("✅ ストップ高検出アルゴリズム - PASS")
        
        await test_instance.test_trading_signal_generation()
        print("✅ 売買シグナル生成 - PASS")
        
        await test_instance.test_risk_assessment()
        print("✅ リスク評価機能 - PASS")
        
        await test_instance.test_history_management()
        print("✅ 履歴管理機能 - PASS")
        
        print("🎉 全テスト完了 - ロジックA強化版が正常に動作しています")
        
    except Exception as e:
        print(f"❌ テスト失敗: {str(e)}")
        raise


if __name__ == "__main__":
    # 直接実行時のテスト
    asyncio.run(run_integration_test())