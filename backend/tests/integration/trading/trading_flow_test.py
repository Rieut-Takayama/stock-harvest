"""
売買支援API統合テスト - 完全フローテスト
@9統合テスト成功請負人が実行・成功させるテスト

実データを使用し、モックは一切使用しない方針で実装
"""

import pytest
import asyncio
import json
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from tests.utils.MilestoneTracker import MilestoneTracker
from tests.utils.db_test_helper import get_global_test_helper

# システム配下のインポート
import sys
import os

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from src.services.trading_service import TradingService
from src.models.trading_models import (
    EntryOptimizationRequest,
    IfdocoGuideRequest,
    TradingHistoryFilter,
    SignalHistoryFilter
)
from src.validators.trading_validators import (
    EntryOptimizationValidator,
    IfdocoGuideValidator,
    TradingHistoryValidator,
    SignalHistoryValidator
)


class TradingApiIntegrationTest:
    """売買支援API統合テスト"""

    def __init__(self):
        self.trading_service = TradingService()
        self.db_helper = get_global_test_helper()
        self.test_data_created = []

    async def setup_test_environment(self):
        """テスト環境セットアップ"""
        tracker = MilestoneTracker()
        tracker.set_operation("テスト環境セットアップ")
        
        try:
            # データベース接続
            db = await self.db_helper.setup_test_environment()
            tracker.mark("データベース接続完了")
            
            # テスト用銘柄マスタデータ作成
            await self._setup_test_stock_master(db)
            tracker.mark("テスト用銘柄マスタ作成完了")
            
            # テスト用売買履歴データ作成
            await self._setup_test_trading_history(db)
            tracker.mark("テスト用売買履歴作成完了")
            
            # テスト用シグナルデータ作成
            await self._setup_test_signal_data(db)
            tracker.mark("テスト用シグナルデータ作成完了")
            
            tracker.summary()
            return db
            
        except Exception as e:
            tracker.mark(f"セットアップエラー: {e}")
            tracker.summary()
            raise

    async def _setup_test_stock_master(self, db):
        """テスト用銘柄マスタデータ作成"""
        test_stocks = [
            {
                'code': '7203',
                'name': 'トヨタ自動車',
                'market': 'Prime',
                'sector': '輸送用機器',
                'is_active': True
            },
            {
                'code': '8306',
                'name': '三菱UFJフィナンシャル・グループ',
                'market': 'Prime',
                'sector': '銀行業',
                'is_active': True
            },
            {
                'code': '9984',
                'name': 'ソフトバンクグループ',
                'market': 'Prime',
                'sector': '情報・通信業',
                'is_active': True
            }
        ]
        
        for stock in test_stocks:
            # 重複チェック後、存在しない場合のみ作成
            existing = await db.fetch_one(
                "SELECT code FROM stock_master WHERE code = :code",
                {'code': stock['code']}
            )
            
            if not existing:
                await db.execute("""
                    INSERT INTO stock_master (code, name, market, sector, is_active)
                    VALUES (:code, :name, :market, :sector, :is_active)
                """, stock)
                self.test_data_created.append(('stock_master', stock['code']))

    async def _setup_test_trading_history(self, db):
        """テスト用売買履歴データ作成"""
        test_trades = [
            {
                'id': f'trade-test-{int(datetime.now().timestamp() * 1000)}-001',
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車',
                'trade_type': 'BUY',
                'logic_type': 'logic_a',
                'entry_price': Decimal('1000.0'),
                'exit_price': Decimal('1100.0'),
                'quantity': 100,
                'total_cost': Decimal('100000.0'),
                'commission': Decimal('500.0'),
                'profit_loss': Decimal('10000.0'),
                'profit_loss_rate': Decimal('10.0'),
                'holding_period': 14,
                'trade_date': datetime.now() - timedelta(days=30),
                'settlement_date': datetime.now() - timedelta(days=16),
                'order_method': 'limit',
                'target_profit': Decimal('1200.0'),
                'stop_loss': Decimal('900.0'),
                'risk_reward_ratio': Decimal('2.0'),
                'status': 'closed',
                'entry_reason': 'ロジックA検出による自動エントリー',
                'exit_reason': 'profit_target'
            },
            {
                'id': f'trade-test-{int(datetime.now().timestamp() * 1000)}-002',
                'stock_code': '8306',
                'stock_name': '三菱UFJフィナンシャル・グループ',
                'trade_type': 'BUY',
                'logic_type': 'logic_b',
                'entry_price': Decimal('800.0'),
                'exit_price': Decimal('750.0'),
                'quantity': 200,
                'total_cost': Decimal('160000.0'),
                'commission': Decimal('800.0'),
                'profit_loss': Decimal('-10000.0'),
                'profit_loss_rate': Decimal('-6.25'),
                'holding_period': 7,
                'trade_date': datetime.now() - timedelta(days=20),
                'settlement_date': datetime.now() - timedelta(days=13),
                'order_method': 'market',
                'target_profit': Decimal('1000.0'),
                'stop_loss': Decimal('720.0'),
                'risk_reward_ratio': Decimal('2.5'),
                'status': 'closed',
                'entry_reason': 'ロジックB検出による自動エントリー',
                'exit_reason': 'stop_loss'
            }
        ]
        
        for trade in test_trades:
            # 重複チェック
            existing = await db.fetch_one(
                "SELECT id FROM trading_history WHERE id = :id",
                {'id': trade['id']}
            )
            
            if not existing:
                await db.execute("""
                    INSERT INTO trading_history (
                        id, stock_code, stock_name, trade_type, logic_type,
                        entry_price, exit_price, quantity, total_cost, commission,
                        profit_loss, profit_loss_rate, holding_period,
                        trade_date, settlement_date, order_method,
                        target_profit, stop_loss, risk_reward_ratio,
                        status, entry_reason, exit_reason
                    ) VALUES (
                        :id, :stock_code, :stock_name, :trade_type, :logic_type,
                        :entry_price, :exit_price, :quantity, :total_cost, :commission,
                        :profit_loss, :profit_loss_rate, :holding_period,
                        :trade_date, :settlement_date, :order_method,
                        :target_profit, :stop_loss, :risk_reward_ratio,
                        :status, :entry_reason, :exit_reason
                    )
                """, trade)
                self.test_data_created.append(('trading_history', trade['id']))

    async def _setup_test_signal_data(self, db):
        """テスト用シグナルデータ作成"""
        test_signals = [
            {
                'id': f'signal-test-{int(datetime.now().timestamp() * 1000)}-001',
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車',
                'signal_type': 'BUY',
                'signal_strength': Decimal('85.0'),
                'confidence': Decimal('0.85'),
                'current_price': Decimal('1050.0'),
                'entry_price': Decimal('1040.0'),
                'profit_target': Decimal('1250.0'),
                'stop_loss': Decimal('950.0'),
                'risk_reward_ratio': Decimal('2.33'),
                'status': 'executed',
                'created_at': datetime.now() - timedelta(days=5)
            },
            {
                'id': f'signal-test-{int(datetime.now().timestamp() * 1000)}-002',
                'stock_code': '9984',
                'stock_name': 'ソフトバンクグループ',
                'signal_type': 'SELL',
                'signal_strength': Decimal('75.0'),
                'confidence': Decimal('0.75'),
                'current_price': Decimal('6000.0'),
                'entry_price': Decimal('6100.0'),
                'profit_target': Decimal('5500.0'),
                'stop_loss': Decimal('6300.0'),
                'risk_reward_ratio': Decimal('3.0'),
                'status': 'pending',
                'created_at': datetime.now() - timedelta(days=2)
            }
        ]
        
        for signal in test_signals:
            # 重複チェック
            existing = await db.fetch_one(
                "SELECT id FROM trading_signals WHERE id = :id",
                {'id': signal['id']}
            )
            
            if not existing:
                await db.execute("""
                    INSERT INTO trading_signals (
                        id, stock_code, stock_name, signal_type, signal_strength,
                        confidence, current_price, entry_price, profit_target,
                        stop_loss, risk_reward_ratio, status, created_at
                    ) VALUES (
                        :id, :stock_code, :stock_name, :signal_type, :signal_strength,
                        :confidence, :current_price, :entry_price, :profit_target,
                        :stop_loss, :risk_reward_ratio, :status, :created_at
                    )
                """, signal)
                self.test_data_created.append(('trading_signals', signal['id']))

    async def test_entry_optimization_api_flow(self):
        """エントリーポイント最適化API完全フローテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("エントリーポイント最適化APIテスト")
        
        try:
            # テストデータ準備
            test_request_data = {
                'stock_code': '7203',
                'current_price': 1050.0,
                'logic_type': 'logic_a',
                'investment_amount': 100000.0,
                'risk_tolerance': 'medium',
                'timeframe': '1m',
                'market_conditions': {
                    'market_trend': 'bullish',
                    'volatility': 'medium'
                }
            }
            tracker.mark("テストデータ準備完了")
            
            # バリデーション実行
            validated_data = EntryOptimizationValidator.validate_request(test_request_data)
            assert validated_data['stock_code'] == '7203'
            assert validated_data['current_price'] == Decimal('1050.0')
            tracker.mark("バリデーション成功")
            
            # リクエストモデル作成
            request = EntryOptimizationRequest(**validated_data)
            assert request.stock_code == '7203'
            assert request.current_price == Decimal('1050.0')
            tracker.mark("リクエストモデル作成成功")
            
            # サービス層実行
            result = await self.trading_service.optimize_entry_point(request)
            assert result.success == True
            assert result.stock_code == '7203'
            assert result.optimal_entry_price > 0
            assert result.risk_reward_ratio > 0
            assert result.confidence_level in ['low', 'medium', 'high']
            tracker.mark("エントリーポイント最適化成功")
            
            # レスポンス構造検証
            assert hasattr(result, 'target_profit_price')
            assert hasattr(result, 'stop_loss_price')
            assert hasattr(result, 'position_size_recommendation')
            assert hasattr(result, 'market_timing_score')
            assert isinstance(result.analysis_factors, dict)
            assert isinstance(result.execution_notes, list)
            tracker.mark("レスポンス構造検証成功")
            
            # パフォーマンス検証
            assert result.market_timing_score >= 1 and result.market_timing_score <= 100
            assert result.optimal_entry_price < request.current_price * Decimal('1.05')  # 現在価格の105%以下
            tracker.mark("パフォーマンス指標検証成功")
            
            tracker.summary()
            print("✅ エントリーポイント最適化API完全フローテスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ エントリーポイント最適化APIテストエラー: {e}")
            raise

    async def test_ifdoco_guide_api_flow(self):
        """IFDOCO注文ガイドAPI完全フローテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("IFDOCO注文ガイドAPIテスト")
        
        try:
            # テストデータ準備
            test_request_data = {
                'stock_code': '8306',
                'entry_price': 850.0,
                'investment_amount': 170000.0,
                'logic_type': 'logic_b',
                'risk_level': 'medium',
                'holding_period': '1m'
            }
            tracker.mark("テストデータ準備完了")
            
            # バリデーション実行
            validated_data = IfdocoGuideValidator.validate_request(test_request_data)
            assert validated_data['stock_code'] == '8306'
            assert validated_data['entry_price'] == Decimal('850.0')
            tracker.mark("バリデーション成功")
            
            # リクエストモデル作成
            request = IfdocoGuideRequest(**validated_data)
            assert request.stock_code == '8306'
            assert request.entry_price == Decimal('850.0')
            tracker.mark("リクエストモデル作成成功")
            
            # サービス層実行
            result = await self.trading_service.generate_ifdoco_guide(request)
            assert result.success == True
            assert result.stock_code == '8306'
            assert result.recommended_quantity > 0
            assert result.order_settings is not None
            tracker.mark("IFDOCO注文ガイド生成成功")
            
            # 注文設定検証
            order_settings = result.order_settings
            assert 'entry_order' in order_settings.dict()
            assert 'profit_target_order' in order_settings.dict()
            assert 'stop_loss_order' in order_settings.dict()
            assert order_settings.order_validity in ['day', 'week', 'month']
            tracker.mark("注文設定検証成功")
            
            # ガイド内容検証
            assert isinstance(result.step_by_step_guide, list)
            assert len(result.step_by_step_guide) > 0
            assert isinstance(result.risk_analysis, dict)
            assert isinstance(result.expected_scenarios, dict)
            assert isinstance(result.broker_specific_notes, dict)
            tracker.mark("ガイド内容検証成功")
            
            # 価格検証
            entry_price = result.entry_price
            profit_price = order_settings.profit_target_order['price']
            stop_price = order_settings.stop_loss_order['price']
            assert profit_price > entry_price  # 利確価格はエントリー価格より高い
            assert stop_price < entry_price     # ストップロス価格はエントリー価格より低い
            tracker.mark("価格設定妥当性検証成功")
            
            tracker.summary()
            print("✅ IFDOCO注文ガイドAPI完全フローテスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ IFDOCO注文ガイドAPIテストエラー: {e}")
            raise

    async def test_trading_history_api_flow(self):
        """売買履歴API完全フローテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("売買履歴APIテスト")
        
        try:
            # フィルタなし（全履歴取得）
            filters = TradingHistoryFilter(page=1, limit=10)
            result = await self.trading_service.get_trading_history(filters)
            
            assert result.success == True
            assert isinstance(result.trades, list)
            assert isinstance(result.summary, object)
            assert result.total >= 0
            tracker.mark("全履歴取得成功")
            
            # 銘柄コード指定フィルタ
            filters_with_stock = TradingHistoryFilter(
                stock_code='7203',
                page=1,
                limit=5
            )
            result_filtered = await self.trading_service.get_trading_history(filters_with_stock)
            
            assert result_filtered.success == True
            # フィルタ結果検証（7203の取引のみ）
            for trade in result_filtered.trades:
                assert trade['stock_code'] == '7203'
            tracker.mark("銘柄フィルタ取得成功")
            
            # ロジック種別フィルタ
            filters_logic = TradingHistoryFilter(
                logic_type='logic_a',
                page=1,
                limit=5
            )
            result_logic = await self.trading_service.get_trading_history(filters_logic)
            
            assert result_logic.success == True
            for trade in result_logic.trades:
                assert trade['logic_type'] == 'logic_a'
            tracker.mark("ロジックフィルタ取得成功")
            
            # サマリー統計検証
            summary = result.summary
            assert hasattr(summary, 'total_trades')
            assert hasattr(summary, 'win_rate')
            assert hasattr(summary, 'total_profit_loss')
            tracker.mark("サマリー統計検証成功")
            
            tracker.summary()
            print("✅ 売買履歴API完全フローテスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ 売買履歴APIテストエラー: {e}")
            raise

    async def test_signal_history_api_flow(self):
        """シグナル履歴API完全フローテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("シグナル履歴APIテスト")
        
        try:
            # フィルタなし（全履歴取得）
            filters = SignalHistoryFilter(page=1, limit=10)
            result = await self.trading_service.get_signal_history(filters)
            
            assert result.success == True
            assert isinstance(result.signals, list)
            assert isinstance(result.summary, object)
            assert result.total >= 0
            tracker.mark("全シグナル履歴取得成功")
            
            # 信頼度フィルタ
            filters_confidence = SignalHistoryFilter(
                confidence_min=0.8,
                page=1,
                limit=5
            )
            result_confidence = await self.trading_service.get_signal_history(filters_confidence)
            
            assert result_confidence.success == True
            for signal in result_confidence.signals:
                assert signal['confidence'] >= 0.8
            tracker.mark("信頼度フィルタ取得成功")
            
            # ステータスフィルタ
            filters_status = SignalHistoryFilter(
                status='executed',
                page=1,
                limit=5
            )
            result_status = await self.trading_service.get_signal_history(filters_status)
            
            assert result_status.success == True
            for signal in result_status.signals:
                assert signal['status'] == 'executed'
            tracker.mark("ステータスフィルタ取得成功")
            
            # サマリー統計検証
            summary = result.summary
            assert hasattr(summary, 'total_signals')
            assert hasattr(summary, 'executed_signals')
            assert hasattr(summary, 'average_confidence')
            tracker.mark("サマリー統計検証成功")
            
            tracker.summary()
            print("✅ シグナル履歴API完全フローテスト成功")
            return True
            
        except Exception as e:
            tracker.mark(f"テストエラー: {e}")
            tracker.summary()
            print(f"❌ シグナル履歴APIテストエラー: {e}")
            raise

    async def test_complete_trading_support_flow(self):
        """売買支援機能完全統合フローテスト"""
        tracker = MilestoneTracker()
        tracker.set_operation("売買支援機能完全統合フローテスト")
        
        try:
            # 1. エントリーポイント最適化
            optimization_request = EntryOptimizationRequest(
                stock_code='9984',
                current_price=Decimal('6200.0'),
                logic_type='manual',
                investment_amount=Decimal('300000.0'),
                risk_tolerance='medium',
                timeframe='1m'
            )
            
            optimization_result = await self.trading_service.optimize_entry_point(optimization_request)
            assert optimization_result.success == True
            tracker.mark("1. エントリーポイント最適化完了")
            
            # 2. 最適化結果を使用してIFDOCO注文ガイド生成
            ifdoco_request = IfdocoGuideRequest(
                stock_code='9984',
                entry_price=optimization_result.optimal_entry_price,
                investment_amount=Decimal('300000.0'),
                logic_type='manual',
                risk_level='medium',
                holding_period='1m'
            )
            
            ifdoco_result = await self.trading_service.generate_ifdoco_guide(ifdoco_request)
            assert ifdoco_result.success == True
            tracker.mark("2. IFDOCO注文ガイド生成完了")
            
            # 3. 模擬取引記録作成（実際の取引を想定）
            trade_record = {
                'stock_code': '9984',
                'stock_name': 'ソフトバンクグループ',
                'trade_type': 'BUY',
                'logic_type': 'manual',
                'entry_price': float(optimization_result.optimal_entry_price),
                'quantity': ifdoco_result.recommended_quantity,
                'total_cost': float(optimization_result.optimal_entry_price * ifdoco_result.recommended_quantity),
                'commission': 1000.0,
                'order_method': 'ifdoco',
                'target_profit': float(optimization_result.target_profit_price),
                'stop_loss': float(optimization_result.stop_loss_price),
                'risk_reward_ratio': float(optimization_result.risk_reward_ratio),
                'status': 'open',
                'entry_reason': f'システム最適化による推奨エントリー（信頼度: {optimization_result.confidence_level}）'
            }
            
            trade_id = await self.trading_service.trading_repo.create_trading_record(trade_record)
            assert trade_id is not None
            self.test_data_created.append(('trading_history', trade_id))
            tracker.mark("3. 取引記録作成完了")
            
            # 4. 作成された取引が履歴で確認できることを検証
            history_filters = TradingHistoryFilter(stock_code='9984', page=1, limit=5)
            history_result = await self.trading_service.get_trading_history(history_filters)
            
            assert history_result.success == True
            found_trade = False
            for trade in history_result.trades:
                if trade['id'] == trade_id:
                    found_trade = True
                    assert trade['stock_code'] == '9984'
                    assert trade['status'] == 'open'
                    break
            
            assert found_trade == True
            tracker.mark("4. 取引履歴確認完了")
            
            # 5. 全体的なパフォーマンス指標確認
            assert optimization_result.market_timing_score >= 1
            assert float(optimization_result.risk_reward_ratio) > 0
            assert ifdoco_result.recommended_quantity > 0
            tracker.mark("5. パフォーマンス指標確認完了")
            
            tracker.summary()
            print("✅ 売買支援機能完全統合フローテスト成功")
            print(f"   - 最適エントリー価格: {optimization_result.optimal_entry_price}")
            print(f"   - 推奨数量: {ifdoco_result.recommended_quantity}株")
            print(f"   - リスクリワード比率: {optimization_result.risk_reward_ratio}")
            print(f"   - 市場タイミングスコア: {optimization_result.market_timing_score}/100")
            print(f"   - 作成された取引ID: {trade_id}")
            
            return True
            
        except Exception as e:
            tracker.mark(f"統合フローエラー: {e}")
            tracker.summary()
            print(f"❌ 売買支援機能完全統合フローテストエラー: {e}")
            raise

    async def cleanup_test_data(self):
        """テストデータクリーンアップ"""
        tracker = MilestoneTracker()
        tracker.set_operation("テストデータクリーンアップ")
        
        try:
            db = await self.db_helper.get_db_connection()
            
            # 作成したテストデータを削除
            for table, record_id in reversed(self.test_data_created):  # 逆順で削除
                try:
                    if table == 'stock_master':
                        await db.execute(
                            "DELETE FROM stock_master WHERE code = :code",
                            {'code': record_id}
                        )
                    elif table == 'trading_history':
                        await db.execute(
                            "DELETE FROM trading_history WHERE id = :id",
                            {'id': record_id}
                        )
                    elif table == 'trading_signals':
                        await db.execute(
                            "DELETE FROM trading_signals WHERE id = :id",
                            {'id': record_id}
                        )
                    
                    tracker.mark(f"{table}:{record_id} 削除完了")
                    
                except Exception as cleanup_error:
                    print(f"⚠️ クリーンアップエラー（{table}:{record_id}): {cleanup_error}")
            
            tracker.summary()
            print("✅ テストデータクリーンアップ完了")
            
        except Exception as e:
            tracker.mark(f"クリーンアップエラー: {e}")
            tracker.summary()
            print(f"⚠️ テストデータクリーンアップエラー: {e}")


# @9統合テスト成功請負人が実行する統合テスト関数群
async def test_trading_support_apis_integration():
    """
    @9統合テスト成功請負人が実行する売買支援API統合テスト
    
    このテストは以下の機能を完全に検証します:
    1. エントリーポイント最適化API
    2. IFDOCO注文ガイドAPI  
    3. 売買履歴API
    4. シグナル履歴API
    5. 完全統合フロー
    
    実データを使用し、モックは一切使用しません。
    """
    print("🚀 売買支援API統合テスト開始")
    print("=" * 60)
    
    integration_test = TradingApiIntegrationTest()
    
    try:
        # テスト環境セットアップ
        await integration_test.setup_test_environment()
        print("✅ テスト環境セットアップ完了\n")
        
        # 各API個別テスト
        await integration_test.test_entry_optimization_api_flow()
        print()
        
        await integration_test.test_ifdoco_guide_api_flow()
        print()
        
        await integration_test.test_trading_history_api_flow()
        print()
        
        await integration_test.test_signal_history_api_flow()
        print()
        
        # 完全統合フローテスト
        await integration_test.test_complete_trading_support_flow()
        print()
        
        print("=" * 60)
        print("🎉 売買支援API統合テスト全件成功！")
        print("✅ エントリーポイント最適化API: PASS")
        print("✅ IFDOCO注文ガイドAPI: PASS") 
        print("✅ 売買履歴API: PASS")
        print("✅ シグナル履歴API: PASS")
        print("✅ 完全統合フロー: PASS")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        raise
        
    finally:
        # テストデータクリーンアップ
        await integration_test.cleanup_test_data()
        print("🧹 テストデータクリーンアップ完了")


if __name__ == "__main__":
    """
    @9統合テスト成功請負人用のテスト実行エントリーポイント
    
    実行方法:
    cd backend
    python -m pytest tests/integration/trading/trading_flow_test.py::test_trading_support_apis_integration -v
    
    または:
    python tests/integration/trading/trading_flow_test.py
    """
    asyncio.run(test_trading_support_apis_integration())