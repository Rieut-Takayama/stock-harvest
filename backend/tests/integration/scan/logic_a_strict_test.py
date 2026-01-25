"""
ロジックA厳密版統合テスト
5つの条件判定ロジック（LogicAStrictService）の検証
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from src.services.logic_a_strict_service import LogicAStrictService
from src.database.config import get_db_connection


class TestLogicAStrictService:
    """ロジックA厳密版サービスの統合テストクラス"""

    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.service = LogicAStrictService()

    def setup_method(self, method):
        """各テストメソッド前の初期化"""
        print(f"\n🧪 テスト開始: {method.__name__}")

    def teardown_method(self, method):
        """各テストメソッド後のクリーンアップ"""
        print(f"✅ テスト完了: {method.__name__}")

    @pytest.mark.asyncio
    async def test_condition_1_stop_high_reached(self):
        """
        条件1: ストップ高価格に到達（終値 = ストップ高価格）
        """
        # テストデータ: ストップ高に到達した銘柄
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1000,
                'high': 1300,
                'low': 1000,
                'close': 1300,  # ストップ高価格
                'volume': 1000000
            },
            'prevClose': 1000  # 前日終値
        }

        # 条件1のみをテスト
        result = await self.service._check_condition_1(
            stock_data['code'],
            stock_data['ohlc']['close'],
            stock_data['prevClose']
        )

        assert result['passed'] is True
        assert 'ストップ高到達' in result['reason']
        print(f"✅ 条件1クリア: {result['reason']}")

    @pytest.mark.asyncio
    async def test_condition_1_not_stop_high(self):
        """
        条件1: ストップ高に未到達
        """
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1000,
                'high': 1200,
                'low': 1000,
                'close': 1200,  # ストップ高未到達
                'volume': 1000000
            },
            'prevClose': 1000
        }

        result = await self.service._check_condition_1(
            stock_data['code'],
            stock_data['ohlc']['close'],
            stock_data['prevClose']
        )

        assert result['passed'] is False
        assert 'ストップ高未到達' in result['reason']
        print(f"✅ 条件1未達: {result['reason']}")

    @pytest.mark.asyncio
    async def test_condition_2_sticking(self):
        """
        条件2: 始値 = 終値（張り付き状態）
        """
        result = self.service._check_condition_2(1300, 1300)

        assert result['passed'] is True
        assert '張り付き状態' in result['reason']
        print(f"✅ 条件2クリア: {result['reason']}")

    @pytest.mark.asyncio
    async def test_condition_2_not_sticking(self):
        """
        条件2: 始値 ≠ 終値（張り付き不成立）
        """
        result = self.service._check_condition_2(1000, 1300)

        assert result['passed'] is False
        assert '張り付き不成立' in result['reason']
        print(f"✅ 条件2未達: {result['reason']}")

    @pytest.mark.asyncio
    async def test_condition_3_low_within_threshold(self):
        """
        条件3: 安値 < 終値 × 0.01（1%未満条件）
        """
        result = self.service._check_condition_3(10, 1300)

        assert result['passed'] is True
        assert '安値条件クリア' in result['reason']
        print(f"✅ 条件3クリア: {result['reason']}")

    @pytest.mark.asyncio
    async def test_condition_3_low_exceeds_threshold(self):
        """
        条件3: 安値が閾値を超えている
        """
        result = self.service._check_condition_3(50, 1300)

        assert result['passed'] is False
        assert '安値条件未達' in result['reason']
        print(f"✅ 条件3未達: {result['reason']}")

    @pytest.mark.asyncio
    async def test_required_data_validation_success(self):
        """
        必須データの検証: 正常系
        """
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1000,
                'high': 1300,
                'low': 1000,
                'close': 1300,
                'volume': 1000000
            }
        }

        result = self.service._validate_required_data(stock_data)
        assert result is True
        print("✅ 必須データ検証成功")

    @pytest.mark.asyncio
    async def test_required_data_validation_missing_code(self):
        """
        必須データの検証: codeフィールド欠損
        """
        stock_data = {
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1000,
                'high': 1300,
                'low': 1000,
                'close': 1300,
                'volume': 1000000
            }
        }

        result = self.service._validate_required_data(stock_data)
        assert result is False
        print("✅ 必須データ欠損を正しく検出")

    @pytest.mark.asyncio
    async def test_required_data_validation_missing_ohlc(self):
        """
        必須データの検証: OHLCフィールド欠損
        """
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1000,
                'high': 1300,
                'low': 1000
                # closeとvolumeが欠損
            }
        }

        result = self.service._validate_required_data(stock_data)
        assert result is False
        print("✅ OHLC欠損を正しく検出")

    @pytest.mark.asyncio
    async def test_detect_with_insufficient_data(self):
        """
        不完全なデータでの検出テスト
        """
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A'
            # ohlcフィールドが欠損
        }

        result = await self.service.detect_strict_stop_high_sticking(stock_data)

        assert result['detected'] is False
        assert '必須データ不足' in result['reason']
        print(f"✅ データ不足を正しく検出: {result['reason']}")

    @pytest.mark.asyncio
    async def test_full_detection_flow_with_test_data(self):
        """
        完全な検出フロー（テストデータ）
        注意: 条件4,5はDBデータが必要なため、ここではスキップ
        """
        stock_data = {
            'code': '1234',
            'name': 'テスト銘柄A',
            'ohlc': {
                'open': 1300,
                'high': 1300,
                'low': 10,
                'close': 1300,
                'volume': 1000000
            },
            'prevClose': 1000
        }

        result = await self.service.detect_strict_stop_high_sticking(stock_data)

        # 条件1-3はクリアするが、条件4でDBデータが必要なため失敗する
        assert result['detected'] is False
        # 条件4または5で失敗することを確認（DBテーブルがない場合も含む）
        assert ('上場日情報が見つからない' in result['reason'] or
                '決算発表' in result['reason'] or
                '条件4検証エラー' in result['reason'] or
                '条件5検証エラー' in result['reason'])
        print(f"✅ 検出フロー実行: {result['reason']}")


if __name__ == "__main__":
    # 単体での実行用
    import asyncio

    async def run_tests():
        test_instance = TestLogicAStrictService()
        test_instance.setup_class()

        try:
            await test_instance.test_condition_1_stop_high_reached()
            await test_instance.test_condition_1_not_stop_high()
            await test_instance.test_condition_2_sticking()
            await test_instance.test_condition_2_not_sticking()
            await test_instance.test_condition_3_low_within_threshold()
            await test_instance.test_condition_3_low_exceeds_threshold()
            await test_instance.test_required_data_validation_success()
            await test_instance.test_required_data_validation_missing_code()
            await test_instance.test_required_data_validation_missing_ohlc()
            await test_instance.test_detect_with_insufficient_data()
            await test_instance.test_full_detection_flow_with_test_data()
            print("✅ 全てのロジックA厳密版テストが成功しました")

        except Exception as e:
            print(f"❌ テスト失敗: {e}")
            raise

    asyncio.run(run_tests())
