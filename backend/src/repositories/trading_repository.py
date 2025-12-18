"""
売買支援関連リポジトリ
Stock Harvest AI プロジェクト用
"""

from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json
from sqlalchemy import select, and_, or_, desc, asc, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.config import get_db
from ..database.tables import (
    trading_history,
    trading_signals,
    signal_executions,
    signal_performance,
    scan_results,
    stock_master,
    stock_data_cache,
    earnings_schedule
)
from ..lib.logger import logger


class TradingRepository:
    """売買支援関連データアクセス"""

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session

    async def get_db_session(self) -> AsyncSession:
        """データベースセッション取得"""
        if self.db_session:
            return self.db_session
        return await get_db()

    async def get_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """銘柄情報取得"""
        try:
            db = await self.get_db_session()
            
            # 銘柄マスタから基本情報を取得
            query = select(stock_master).where(stock_master.c.code == stock_code)
            result = await db.execute(query)
            stock_info = result.fetchone()
            
            if not stock_info:
                logger.warning(f"銘柄情報が見つかりません: {stock_code}")
                return None
            
            return {
                'stock_code': stock_info.code,
                'stock_name': stock_info.name,
                'market': stock_info.market,
                'sector': stock_info.sector,
                'is_active': stock_info.is_active
            }
            
        except Exception as e:
            logger.error(f"銘柄情報取得エラー: {e}", exc_info=True)
            return None

    async def get_current_stock_price(self, stock_code: str) -> Optional[Decimal]:
        """現在株価取得（キャッシュから）"""
        try:
            db = await self.get_db_session()
            
            # 株価データキャッシュから最新価格を取得
            query = (
                select(stock_data_cache)
                .where(stock_data_cache.c.stock_code == stock_code)
                .where(stock_data_cache.c.expires_at > datetime.now())
                .order_by(desc(stock_data_cache.c.updated_at))
            )
            result = await db.execute(query)
            cache_data = result.fetchone()
            
            if cache_data and cache_data.price_data:
                price_data = cache_data.price_data
                if isinstance(price_data, str):
                    price_data = json.loads(price_data)
                
                # 現在価格を取得
                current_price = price_data.get('current_price')
                if current_price:
                    return Decimal(str(current_price))
            
            logger.warning(f"株価データが見つかりません: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"現在株価取得エラー: {e}", exc_info=True)
            return None

    async def get_historical_trading_data(self, stock_code: str, logic_type: Optional[str] = None, 
                                        days: int = 365) -> List[Dict[str, Any]]:
        """過去の売買データ取得"""
        try:
            db = await self.get_db_session()
            
            # 過去の売買履歴を取得
            conditions = [trading_history.c.stock_code == stock_code]
            if logic_type:
                conditions.append(trading_history.c.logic_type == logic_type)
            
            # 指定日数以内のデータ
            cutoff_date = datetime.now() - timedelta(days=days)
            conditions.append(trading_history.c.trade_date >= cutoff_date)
            
            query = (
                select(trading_history)
                .where(and_(*conditions))
                .order_by(desc(trading_history.c.trade_date))
            )
            
            result = await db.execute(query)
            trades = result.fetchall()
            
            return [
                {
                    'id': trade.id,
                    'trade_type': trade.trade_type,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'profit_loss': trade.profit_loss,
                    'profit_loss_rate': trade.profit_loss_rate,
                    'holding_period': trade.holding_period,
                    'trade_date': trade.trade_date,
                    'settlement_date': trade.settlement_date,
                    'logic_type': trade.logic_type,
                    'status': trade.status
                }
                for trade in trades
            ]
            
        except Exception as e:
            logger.error(f"過去売買データ取得エラー: {e}", exc_info=True)
            return []

    async def get_signal_performance_stats(self, stock_code: Optional[str] = None, 
                                         logic_type: Optional[str] = None, 
                                         days: int = 90) -> Dict[str, Any]:
        """シグナル成績統計取得"""
        try:
            db = await self.get_db_session()
            
            # 条件設定
            conditions = []
            if stock_code:
                conditions.append(trading_signals.c.stock_code == stock_code)
            
            cutoff_date = datetime.now() - timedelta(days=days)
            conditions.append(trading_signals.c.created_at >= cutoff_date)
            
            # 基本統計の取得
            query = select([
                func.count(trading_signals.c.id).label('total_signals'),
                func.avg(trading_signals.c.confidence).label('avg_confidence'),
                func.count().filter(trading_signals.c.status == 'executed').label('executed_signals'),
                func.count().filter(trading_signals.c.signal_type == 'BUY').label('buy_signals'),
                func.count().filter(trading_signals.c.signal_type == 'SELL').label('sell_signals')
            ])
            
            if conditions:
                query = query.where(and_(*conditions))
                
            result = await db.execute(query)
            stats = result.fetchone()
            
            return {
                'total_signals': stats.total_signals or 0,
                'average_confidence': float(stats.avg_confidence) if stats.avg_confidence else 0.0,
                'executed_signals': stats.executed_signals or 0,
                'buy_signals': stats.buy_signals or 0,
                'sell_signals': stats.sell_signals or 0,
                'execution_rate': (stats.executed_signals / max(stats.total_signals, 1)) * 100
            }
            
        except Exception as e:
            logger.error(f"シグナル成績統計取得エラー: {e}", exc_info=True)
            return {
                'total_signals': 0,
                'average_confidence': 0.0,
                'executed_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'execution_rate': 0.0
            }

    async def get_trading_history_list(self, filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """売買履歴一覧取得"""
        try:
            db = await self.get_db_session()
            
            # 条件構築
            conditions = []
            
            if filters.get('stock_code'):
                conditions.append(trading_history.c.stock_code == filters['stock_code'])
            
            if filters.get('logic_type'):
                conditions.append(trading_history.c.logic_type == filters['logic_type'])
            
            if filters.get('trade_type'):
                conditions.append(trading_history.c.trade_type == filters['trade_type'])
            
            if filters.get('status'):
                conditions.append(trading_history.c.status == filters['status'])
            
            if filters.get('date_from'):
                conditions.append(trading_history.c.trade_date >= filters['date_from'])
            
            if filters.get('date_to'):
                conditions.append(trading_history.c.trade_date <= filters['date_to'])
            
            if filters.get('min_profit_loss') is not None:
                conditions.append(trading_history.c.profit_loss >= filters['min_profit_loss'])
            
            if filters.get('max_profit_loss') is not None:
                conditions.append(trading_history.c.profit_loss <= filters['max_profit_loss'])
            
            # 総件数取得
            count_query = select(func.count(trading_history.c.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()
            
            # データ取得
            query = select(trading_history)
            if conditions:
                query = query.where(and_(*conditions))
            
            # ページネーション
            offset = (filters.get('page', 1) - 1) * filters.get('limit', 20)
            query = query.order_by(desc(trading_history.c.trade_date)).offset(offset).limit(filters.get('limit', 20))
            
            result = await db.execute(query)
            trades = result.fetchall()
            
            trade_list = []
            for trade in trades:
                trade_data = {
                    'id': trade.id,
                    'stock_code': trade.stock_code,
                    'stock_name': trade.stock_name,
                    'trade_type': trade.trade_type,
                    'logic_type': trade.logic_type,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'total_cost': trade.total_cost,
                    'commission': trade.commission,
                    'profit_loss': trade.profit_loss,
                    'profit_loss_rate': trade.profit_loss_rate,
                    'holding_period': trade.holding_period,
                    'trade_date': trade.trade_date,
                    'settlement_date': trade.settlement_date,
                    'order_method': trade.order_method,
                    'target_profit': trade.target_profit,
                    'stop_loss': trade.stop_loss,
                    'risk_reward_ratio': trade.risk_reward_ratio,
                    'status': trade.status,
                    'notes': trade.notes
                }
                trade_list.append(trade_data)
            
            return trade_list, total_count
            
        except Exception as e:
            logger.error(f"売買履歴一覧取得エラー: {e}", exc_info=True)
            return [], 0

    async def get_trading_summary_stats(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """売買サマリー統計取得"""
        try:
            db = await self.get_db_session()
            
            # 条件構築（get_trading_history_listと同様）
            conditions = []
            
            if filters.get('stock_code'):
                conditions.append(trading_history.c.stock_code == filters['stock_code'])
            
            if filters.get('logic_type'):
                conditions.append(trading_history.c.logic_type == filters['logic_type'])
            
            if filters.get('date_from'):
                conditions.append(trading_history.c.trade_date >= filters['date_from'])
            
            if filters.get('date_to'):
                conditions.append(trading_history.c.trade_date <= filters['date_to'])
            
            # 基本統計
            base_query = select([
                func.count(trading_history.c.id).label('total_trades'),
                func.count().filter(trading_history.c.status == 'open').label('open_positions'),
                func.count().filter(trading_history.c.status == 'closed').label('closed_positions'),
                func.sum(trading_history.c.profit_loss).label('total_profit_loss'),
                func.avg(trading_history.c.profit_loss_rate).label('avg_profit_loss_rate'),
                func.max(trading_history.c.profit_loss).label('max_profit'),
                func.min(trading_history.c.profit_loss).label('max_loss'),
                func.avg(trading_history.c.holding_period).label('avg_holding_period')
            ])
            
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            result = await db.execute(base_query)
            stats = result.fetchone()
            
            # 勝率計算（決済済みポジションのみ）
            win_conditions = conditions.copy() if conditions else []
            win_conditions.extend([
                trading_history.c.status == 'closed',
                trading_history.c.profit_loss.isnot(None)
            ])
            
            win_query = select([
                func.count().filter(trading_history.c.profit_loss > 0).label('winning_trades'),
                func.count(trading_history.c.id).label('closed_trades'),
                func.avg().filter(trading_history.c.profit_loss > 0, trading_history.c.profit_loss).label('avg_profit'),
                func.avg().filter(trading_history.c.profit_loss < 0, trading_history.c.profit_loss).label('avg_loss')
            ]).where(and_(*win_conditions))
            
            win_result = await db.execute(win_query)
            win_stats = win_result.fetchone()
            
            # 勝率とプロフィットファクター計算
            winning_trades = win_stats.winning_trades or 0
            closed_trades = win_stats.closed_trades or 0
            win_rate = (winning_trades / max(closed_trades, 1)) * 100
            
            avg_profit = win_stats.avg_profit or Decimal('0')
            avg_loss = abs(win_stats.avg_loss) if win_stats.avg_loss else Decimal('0')
            profit_factor = (avg_profit * winning_trades) / max((avg_loss * (closed_trades - winning_trades)), Decimal('0.01'))
            
            return {
                'total_trades': stats.total_trades or 0,
                'open_positions': stats.open_positions or 0,
                'closed_positions': stats.closed_positions or 0,
                'total_profit_loss': stats.total_profit_loss or Decimal('0'),
                'total_profit_loss_rate': stats.avg_profit_loss_rate or Decimal('0'),
                'win_rate': win_rate,
                'average_profit': avg_profit,
                'average_loss': avg_loss,
                'max_profit': stats.max_profit or Decimal('0'),
                'max_loss': stats.max_loss or Decimal('0'),
                'profit_factor': profit_factor,
                'average_holding_period': stats.avg_holding_period or Decimal('0')
            }
            
        except Exception as e:
            logger.error(f"売買サマリー統計取得エラー: {e}", exc_info=True)
            return {
                'total_trades': 0,
                'open_positions': 0,
                'closed_positions': 0,
                'total_profit_loss': Decimal('0'),
                'total_profit_loss_rate': Decimal('0'),
                'win_rate': Decimal('0'),
                'average_profit': Decimal('0'),
                'average_loss': Decimal('0'),
                'max_profit': Decimal('0'),
                'max_loss': Decimal('0'),
                'profit_factor': Decimal('0'),
                'average_holding_period': Decimal('0')
            }

    async def get_signal_history_list(self, filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
        """シグナル履歴一覧取得"""
        try:
            db = await self.get_db_session()
            
            # 条件構築
            conditions = []
            
            if filters.get('stock_code'):
                conditions.append(trading_signals.c.stock_code == filters['stock_code'])
            
            if filters.get('signal_type'):
                conditions.append(trading_signals.c.signal_type == filters['signal_type'])
            
            if filters.get('status'):
                conditions.append(trading_signals.c.status == filters['status'])
            
            if filters.get('confidence_min'):
                conditions.append(trading_signals.c.confidence >= filters['confidence_min'])
            
            if filters.get('date_from'):
                conditions.append(trading_signals.c.created_at >= filters['date_from'])
            
            if filters.get('date_to'):
                conditions.append(trading_signals.c.created_at <= filters['date_to'])
            
            # 総件数取得
            count_query = select(func.count(trading_signals.c.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            count_result = await db.execute(count_query)
            total_count = count_result.scalar()
            
            # データ取得
            query = select(trading_signals)
            if conditions:
                query = query.where(and_(*conditions))
            
            # ページネーション
            offset = (filters.get('page', 1) - 1) * filters.get('limit', 20)
            query = query.order_by(desc(trading_signals.c.created_at)).offset(offset).limit(filters.get('limit', 20))
            
            result = await db.execute(query)
            signals = result.fetchall()
            
            signal_list = []
            for signal in signals:
                signal_data = {
                    'id': signal.id,
                    'stock_code': signal.stock_code,
                    'stock_name': signal.stock_name,
                    'signal_type': signal.signal_type,
                    'signal_strength': signal.signal_strength,
                    'confidence': signal.confidence,
                    'current_price': signal.current_price,
                    'entry_price': signal.entry_price,
                    'profit_target': signal.profit_target,
                    'stop_loss': signal.stop_loss,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'status': signal.status,
                    'created_at': signal.created_at,
                    'expires_at': signal.expires_at
                }
                signal_list.append(signal_data)
            
            return signal_list, total_count
            
        except Exception as e:
            logger.error(f"シグナル履歴一覧取得エラー: {e}", exc_info=True)
            return [], 0

    async def get_signal_summary_stats(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """シグナルサマリー統計取得"""
        try:
            db = await self.get_db_session()
            
            # 条件構築（get_signal_history_listと同様）
            conditions = []
            
            if filters.get('stock_code'):
                conditions.append(trading_signals.c.stock_code == filters['stock_code'])
            
            if filters.get('date_from'):
                conditions.append(trading_signals.c.created_at >= filters['date_from'])
            
            if filters.get('date_to'):
                conditions.append(trading_signals.c.created_at <= filters['date_to'])
            
            # 基本統計
            base_query = select([
                func.count(trading_signals.c.id).label('total_signals'),
                func.count().filter(trading_signals.c.status == 'executed').label('executed_signals'),
                func.count().filter(trading_signals.c.status == 'pending').label('pending_signals'),
                func.count().filter(trading_signals.c.status == 'cancelled').label('cancelled_signals'),
                func.avg(trading_signals.c.confidence).label('average_confidence')
            ])
            
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            result = await db.execute(base_query)
            stats = result.fetchone()
            
            return {
                'total_signals': stats.total_signals or 0,
                'executed_signals': stats.executed_signals or 0,
                'pending_signals': stats.pending_signals or 0,
                'cancelled_signals': stats.cancelled_signals or 0,
                'signal_accuracy': Decimal('0'),  # 後で実際のパフォーマンスから計算
                'average_confidence': stats.average_confidence or Decimal('0'),
                'profitable_signals': 0,  # 後で実装
                'loss_signals': 0,  # 後で実装
                'neutral_signals': 0  # 後で実装
            }
            
        except Exception as e:
            logger.error(f"シグナルサマリー統計取得エラー: {e}", exc_info=True)
            return {
                'total_signals': 0,
                'executed_signals': 0,
                'pending_signals': 0,
                'cancelled_signals': 0,
                'signal_accuracy': Decimal('0'),
                'average_confidence': Decimal('0'),
                'profitable_signals': 0,
                'loss_signals': 0,
                'neutral_signals': 0
            }

    async def create_trading_record(self, trade_data: Dict[str, Any]) -> str:
        """売買記録作成"""
        try:
            db = await self.get_db_session()
            
            # 新しいトレードIDを生成
            trade_id = f"trade-{int(datetime.now().timestamp() * 1000)}"
            
            insert_data = {
                'id': trade_id,
                'stock_code': trade_data['stock_code'],
                'stock_name': trade_data.get('stock_name', ''),
                'trade_type': trade_data['trade_type'],
                'logic_type': trade_data.get('logic_type'),
                'entry_price': trade_data['entry_price'],
                'exit_price': trade_data.get('exit_price'),
                'quantity': trade_data['quantity'],
                'total_cost': trade_data['total_cost'],
                'commission': trade_data.get('commission', Decimal('0')),
                'profit_loss': trade_data.get('profit_loss'),
                'profit_loss_rate': trade_data.get('profit_loss_rate'),
                'holding_period': trade_data.get('holding_period'),
                'trade_date': trade_data.get('trade_date', datetime.now()),
                'settlement_date': trade_data.get('settlement_date'),
                'order_method': trade_data.get('order_method', 'manual'),
                'target_profit': trade_data.get('target_profit'),
                'stop_loss': trade_data.get('stop_loss'),
                'risk_reward_ratio': trade_data.get('risk_reward_ratio'),
                'signal_id': trade_data.get('signal_id'),
                'scan_result_id': trade_data.get('scan_result_id'),
                'entry_reason': trade_data.get('entry_reason'),
                'exit_reason': trade_data.get('exit_reason'),
                'market_conditions': trade_data.get('market_conditions'),
                'performance_analysis': trade_data.get('performance_analysis'),
                'status': trade_data.get('status', 'open'),
                'notes': trade_data.get('notes')
            }
            
            insert_query = trading_history.insert().values(**insert_data)
            await db.execute(insert_query)
            await db.commit()
            
            logger.info(f"売買記録作成完了: {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"売買記録作成エラー: {e}", exc_info=True)
            await db.rollback()
            raise