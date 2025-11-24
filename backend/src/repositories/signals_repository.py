"""
売買シグナル履歴管理リポジトリ
データベースとの売買シグナル関連データのやり取りを担当

機能:
- シグナル履歴の保存・取得
- シグナル実行履歴の管理
- パフォーマンス統計の計算・更新
- アラート履歴の管理
- 手動決済シグナル（従来機能）
"""

import logging
import asyncio
import asyncpg
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import json
from uuid import uuid4

from ..database.config import database
from ..database.tables import (
    manual_signals, trading_signals, signal_executions, 
    signal_performance, alert_history
)

logger = logging.getLogger(__name__)


class SignalsRepository:
    """売買シグナル履歴管理リポジトリ"""
    
    def __init__(self):
        self.db = database

    async def create_signal(
        self,
        signal_id: str,
        signal_type: str,
        stock_code: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        新しい手動決済シグナルを作成
        
        Args:
            signal_id: シグナルID
            signal_type: シグナルタイプ ("stop_loss" または "take_profit")
            stock_code: 銘柄コード（オプション）
            reason: シグナル実行理由（オプション）
            
        Returns:
            作成されたシグナル情報
        """
        query = """
            INSERT INTO manual_signals 
            (id, signal_type, stock_code, reason, status, created_at, updated_at)
            VALUES (:signal_id, :signal_type, :stock_code, :reason, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING *
        """
        
        row = await database.fetch_one(
            query, {
                "signal_id": signal_id,
                "signal_type": signal_type, 
                "stock_code": stock_code,
                "reason": reason
            }
        )
        
        if row:
            return dict(row)
        else:
            raise Exception("Failed to create manual signal")

    async def update_signal_status(
        self,
        signal_id: str,
        status: str,
        executed_at: Optional[datetime] = None,
        affected_positions: Optional[int] = None,
        execution_result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        シグナルの実行状況を更新
        
        Args:
            signal_id: シグナルID
            status: 新しいステータス
            executed_at: 実行時刻
            affected_positions: 影響を受けたポジション数
            execution_result: 実行結果詳細
            error_message: エラーメッセージ
            
        Returns:
            更新されたシグナル情報
        """
        query = """
            UPDATE manual_signals 
            SET status = :status,
                executed_at = :executed_at,
                affected_positions = :affected_positions,
                execution_result = :execution_result,
                error_message = :error_message,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :signal_id
            RETURNING *
        """
        
        # JSONをJSONBに変換する際の処理
        import json
        execution_result_json = json.dumps(execution_result) if execution_result else None
        
        row = await database.fetch_one(
            query, {
                "signal_id": signal_id,
                "status": status,
                "executed_at": executed_at,
                "affected_positions": affected_positions,
                "execution_result": execution_result_json,
                "error_message": error_message
            }
        )
        
        if row:
            return dict(row)
        else:
            raise Exception(f"Manual signal with ID {signal_id} not found")

    async def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        IDによるシグナル情報取得
        
        Args:
            signal_id: シグナルID
            
        Returns:
            シグナル情報（見つからない場合はNone）
        """
        query = "SELECT * FROM manual_signals WHERE id = :signal_id"
        row = await database.fetch_one(query, {"signal_id": signal_id})
        
        if row:
            return dict(row)
        return None

    async def get_recent_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近のシグナル履歴を取得
        
        Args:
            limit: 取得件数制限
            
        Returns:
            シグナル履歴のリスト
        """
        query = """
            SELECT * FROM manual_signals 
            ORDER BY created_at DESC 
            LIMIT :limit
        """
        rows = await database.fetch_all(query, {"limit": limit})
        
        return [dict(row) for row in rows]

    async def get_pending_signals(self) -> List[Dict[str, Any]]:
        """
        実行待ちのシグナルを取得
        
        Returns:
            実行待ちシグナルのリスト
        """
        query = """
            SELECT * FROM manual_signals 
            WHERE status = 'pending'
            ORDER BY created_at ASC
        """
        rows = await database.fetch_all(query)
        
        return [dict(row) for row in rows]
    
    # === 新機能: 売買シグナル履歴管理 ===
    
    async def save_trading_signal(self, signal_data: Dict) -> str:
        """
        売買シグナルをデータベースに保存
        """
        try:
            # ID生成
            signal_id = f"signal-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8]}"
            
            # データ準備
            insert_data = {
                'id': signal_id,
                'stock_code': signal_data['stock_code'],
                'stock_name': signal_data.get('stock_name', ''),
                'signal_type': signal_data['action'],
                'signal_strength': signal_data['signal_strength'],
                'confidence': signal_data['confidence'],
                'current_price': signal_data['current_price'],
                'entry_price': signal_data.get('entry_price'),
                'profit_target': signal_data.get('profit_target'),
                'stop_loss': signal_data.get('stop_loss'),
                'risk_reward_ratio': signal_data.get('risk_reward_ratio'),
                'recommended_shares': signal_data.get('recommended_shares'),
                'position_value': signal_data.get('position_value'),
                'portfolio_exposure': signal_data.get('portfolio_exposure'),
                'component_scores': json.dumps(signal_data.get('component_scores', {})),
                'risk_assessment': json.dumps(signal_data.get('risk_assessment', {})),
                'execution_notes': json.dumps(signal_data.get('execution_notes', [])),
                'logic_results': json.dumps(signal_data.get('logic_results', {})),
                'technical_analysis': json.dumps(signal_data.get('technical_analysis', {})),
                'timeframe_analysis': json.dumps(signal_data.get('timeframe_analysis', {})),
                'is_executable': signal_data.get('executable', False),
                'expires_at': datetime.now() + timedelta(days=7)  # 7日間有効
            }
            
            # データベースに挿入
            await self.db.execute(
                trading_signals.insert().values(**insert_data)
            )
            
            logger.info(f"シグナル保存完了: {signal_id} - {signal_data['stock_code']}")
            return signal_id
            
        except Exception as e:
            logger.error(f"シグナル保存エラー: {str(e)}")
            raise
    
    async def get_active_trading_signals(self, stock_code: str = None, limit: int = 50) -> List[Dict]:
        """
        アクティブシグナル一覧取得
        """
        try:
            # クエリ構築
            query = trading_signals.select().where(
                trading_signals.c.status == 'active'
            ).order_by(trading_signals.c.created_at.desc()).limit(limit)
            
            if stock_code:
                query = query.where(trading_signals.c.stock_code == stock_code)
            
            # データ取得
            results = await self.db.fetch_all(query)
            
            # 結果を辞書リストに変換
            signals = []
            for row in results:
                signal = dict(row)
                
                # JSON文字列を辞書に変換
                signal['component_scores'] = json.loads(signal['component_scores'] or '{}')
                signal['risk_assessment'] = json.loads(signal['risk_assessment'] or '{}')
                signal['execution_notes'] = json.loads(signal['execution_notes'] or '[]')
                signal['logic_results'] = json.loads(signal['logic_results'] or '{}')
                signal['technical_analysis'] = json.loads(signal['technical_analysis'] or '{}')
                signal['timeframe_analysis'] = json.loads(signal['timeframe_analysis'] or '{}')
                
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"アクティブシグナル取得エラー: {str(e)}")
            return []
    
    async def get_trading_signal_history(
        self, 
        stock_code: str = None, 
        signal_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        シグナル履歴取得
        """
        try:
            # 基本クエリ
            query = trading_signals.select().order_by(
                trading_signals.c.created_at.desc()
            ).limit(limit)
            
            # 条件追加
            conditions = []
            
            if stock_code:
                conditions.append(trading_signals.c.stock_code == stock_code)
            
            if signal_type:
                conditions.append(trading_signals.c.signal_type == signal_type)
            
            if start_date:
                conditions.append(trading_signals.c.created_at >= start_date)
            
            if end_date:
                conditions.append(trading_signals.c.created_at <= end_date)
            
            if conditions:
                from sqlalchemy import and_
                query = query.where(and_(*conditions))
            
            # データ取得
            results = await self.db.fetch_all(query)
            
            # 結果処理
            signals = []
            for row in results:
                signal = dict(row)
                
                # JSON文字列を辞書に変換
                signal['component_scores'] = json.loads(signal['component_scores'] or '{}')
                signal['risk_assessment'] = json.loads(signal['risk_assessment'] or '{}')
                signal['execution_notes'] = json.loads(signal['execution_notes'] or '[]')
                
                signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"シグナル履歴取得エラー: {str(e)}")
            return []
    
    async def update_trading_signal_status(self, signal_id: str, status: str, notes: str = None) -> bool:
        """
        シグナルステータス更新
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now()
            }
            
            if notes:
                update_data['execution_notes'] = json.dumps([notes])
            
            await self.db.execute(
                trading_signals.update().where(
                    trading_signals.c.id == signal_id
                ).values(**update_data)
            )
            
            logger.info(f"シグナルステータス更新完了: {signal_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"シグナルステータス更新エラー: {str(e)}")
            return False
    
    async def save_signal_execution(self, execution_data: Dict) -> str:
        """
        シグナル実行履歴保存
        """
        try:
            # ID生成
            execution_id = f"execution-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid4())[:8]}"
            
            # データ準備
            insert_data = {
                'id': execution_id,
                'signal_id': execution_data['signal_id'],
                'execution_type': execution_data['execution_type'],
                'executed_price': execution_data['executed_price'],
                'executed_shares': execution_data['executed_shares'],
                'execution_cost': execution_data.get('execution_cost', 0),
                'market_price': execution_data['market_price'],
                'slippage': execution_data.get('slippage', 0),
                'execution_method': execution_data.get('execution_method', 'manual'),
                'execution_notes': execution_data.get('execution_notes'),
                'profit_loss': execution_data.get('profit_loss'),
                'profit_loss_rate': execution_data.get('profit_loss_rate'),
                'holding_period': execution_data.get('holding_period'),
                'status': execution_data.get('status', 'completed'),
                'error_message': execution_data.get('error_message')
            }
            
            # データベースに挿入
            await self.db.execute(
                signal_executions.insert().values(**insert_data)
            )
            
            logger.info(f"シグナル実行履歴保存完了: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"シグナル実行履歴保存エラー: {str(e)}")
            raise
    
    async def get_execution_history(
        self, 
        signal_id: str = None,
        execution_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        シグナル実行履歴取得
        """
        try:
            # 基本クエリ
            query = signal_executions.select().order_by(
                signal_executions.c.created_at.desc()
            ).limit(limit)
            
            # 条件追加
            conditions = []
            
            if signal_id:
                conditions.append(signal_executions.c.signal_id == signal_id)
            
            if execution_type:
                conditions.append(signal_executions.c.execution_type == execution_type)
            
            if start_date:
                conditions.append(signal_executions.c.created_at >= start_date)
            
            if end_date:
                conditions.append(signal_executions.c.created_at <= end_date)
            
            if conditions:
                from sqlalchemy import and_
                query = query.where(and_(*conditions))
            
            # データ取得
            results = await self.db.fetch_all(query)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"シグナル実行履歴取得エラー: {str(e)}")
            return []
    
    async def calculate_daily_performance(self, target_date: datetime = None) -> Dict:
        """
        日次パフォーマンス統計計算
        """
        try:
            if target_date is None:
                target_date = datetime.now().date()
            
            # その日のシグナル統計を取得
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            
            # 総シグナル数
            total_signals_query = f"""
                SELECT COUNT(*) FROM trading_signals 
                WHERE created_at BETWEEN '{start_time}' AND '{end_time}'
            """
            total_signals = await self.db.fetch_val(total_signals_query) or 0
            
            # 買いシグナル数
            buy_signals_query = f"""
                SELECT COUNT(*) FROM trading_signals 
                WHERE created_at BETWEEN '{start_time}' AND '{end_time}'
                AND signal_type IN ('BUY', 'STRONG_BUY')
            """
            buy_signals = await self.db.fetch_val(buy_signals_query) or 0
            
            # 売りシグナル数
            sell_signals_query = f"""
                SELECT COUNT(*) FROM trading_signals 
                WHERE created_at BETWEEN '{start_time}' AND '{end_time}'
                AND signal_type IN ('SELL', 'STRONG_SELL')
            """
            sell_signals = await self.db.fetch_val(sell_signals_query) or 0
            
            # 実行されたシグナル数
            executed_signals_query = f"""
                SELECT COUNT(DISTINCT signal_id) FROM signal_executions 
                WHERE created_at BETWEEN '{start_time}' AND '{end_time}'
            """
            executed_signals = await self.db.fetch_val(executed_signals_query) or 0
            
            # 損益統計（決済取引のみ）
            profit_loss_query = f"""
                SELECT 
                    COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as successful_trades,
                    COUNT(CASE WHEN profit_loss <= 0 THEN 1 END) as failed_trades,
                    AVG(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_profit,
                    AVG(CASE WHEN profit_loss <= 0 THEN profit_loss END) as avg_loss,
                    SUM(profit_loss) as total_profit_loss,
                    MAX(profit_loss) as max_profit,
                    MIN(profit_loss) as max_loss,
                    AVG(profit_loss_rate) as avg_return_rate,
                    AVG(holding_period) as avg_holding_period
                FROM signal_executions 
                WHERE created_at BETWEEN '{start_time}' AND '{end_time}'
                AND execution_type = 'exit' AND profit_loss IS NOT NULL
            """
            
            profit_loss_stats = await self.db.fetch_one(profit_loss_query) or {}
            
            # 統計データ構築
            stats = {
                'date': target_date,
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'executed_signals': executed_signals,
                'successful_trades': profit_loss_stats.get('successful_trades', 0) or 0,
                'failed_trades': profit_loss_stats.get('failed_trades', 0) or 0,
                'average_profit': float(profit_loss_stats.get('avg_profit', 0) or 0),
                'average_loss': float(profit_loss_stats.get('avg_loss', 0) or 0),
                'total_profit_loss': float(profit_loss_stats.get('total_profit_loss', 0) or 0),
                'max_profit': float(profit_loss_stats.get('max_profit', 0) or 0),
                'max_loss': float(profit_loss_stats.get('max_loss', 0) or 0),
                'average_holding_period': float(profit_loss_stats.get('avg_holding_period', 0) or 0),
            }
            
            # 勝率計算
            total_trades = stats['successful_trades'] + stats['failed_trades']
            stats['win_rate'] = (stats['successful_trades'] / total_trades * 100) if total_trades > 0 else 0
            
            # プロフィットファクター計算
            total_profit = stats['successful_trades'] * abs(stats['average_profit'])
            total_loss = stats['failed_trades'] * abs(stats['average_loss'])
            stats['profit_factor'] = (total_profit / total_loss) if total_loss > 0 else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"日次パフォーマンス計算エラー: {str(e)}")
            return {}
    
    async def save_daily_performance(self, performance_data: Dict) -> bool:
        """
        日次パフォーマンス統計保存
        """
        try:
            # 既存データをチェック
            existing = await self.db.fetch_one(
                signal_performance.select().where(
                    signal_performance.c.date == performance_data['date']
                )
            )
            
            if existing:
                # 更新
                await self.db.execute(
                    signal_performance.update().where(
                        signal_performance.c.date == performance_data['date']
                    ).values(**performance_data)
                )
                logger.info(f"パフォーマンス統計更新: {performance_data['date']}")
            else:
                # 挿入
                await self.db.execute(
                    signal_performance.insert().values(**performance_data)
                )
                logger.info(f"パフォーマンス統計保存: {performance_data['date']}")
            
            return True
            
        except Exception as e:
            logger.error(f"パフォーマンス統計保存エラー: {str(e)}")
            return False
    
    async def get_performance_summary(
        self, 
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        パフォーマンスサマリー取得
        """
        try:
            # 期間設定
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()
            
            # 基本統計
            query = signal_performance.select().where(
                signal_performance.c.date.between(start_date.date(), end_date.date())
            )
            
            results = await self.db.fetch_all(query)
            
            if not results:
                return {
                    'period': f"{start_date.date()} - {end_date.date()}",
                    'total_signals': 0,
                    'win_rate': 0,
                    'profit_factor': 0,
                    'total_return': 0,
                    'days_analyzed': 0
                }
            
            # 累計統計計算
            total_signals = sum(r['total_signals'] for r in results)
            total_successful = sum(r['successful_trades'] for r in results)
            total_failed = sum(r['failed_trades'] for r in results)
            total_profit_loss = sum(r['total_profit_loss'] for r in results)
            
            # 勝率
            total_trades = total_successful + total_failed
            overall_win_rate = (total_successful / total_trades * 100) if total_trades > 0 else 0
            
            # プロフィットファクター（加重平均）
            total_profits = sum(r['successful_trades'] * abs(r['average_profit']) for r in results if r['average_profit'] > 0)
            total_losses = sum(r['failed_trades'] * abs(r['average_loss']) for r in results if r['average_loss'] < 0)
            overall_profit_factor = (total_profits / total_losses) if total_losses > 0 else 0
            
            # 最大ドローダウン（簡易計算）
            daily_returns = [r['total_profit_loss'] for r in results]
            max_drawdown = self._calculate_max_drawdown(daily_returns)
            
            summary = {
                'period': f"{start_date.date()} - {end_date.date()}",
                'days_analyzed': len(results),
                'total_signals': total_signals,
                'total_trades': total_trades,
                'successful_trades': total_successful,
                'failed_trades': total_failed,
                'win_rate': round(overall_win_rate, 2),
                'profit_factor': round(overall_profit_factor, 2),
                'total_return': round(total_profit_loss, 2),
                'average_daily_return': round(total_profit_loss / len(results), 2),
                'max_drawdown': round(max_drawdown, 2),
                'best_day': max(daily_returns) if daily_returns else 0,
                'worst_day': min(daily_returns) if daily_returns else 0
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"パフォーマンスサマリー取得エラー: {str(e)}")
            return {}
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """
        最大ドローダウン計算
        """
        try:
            if not returns:
                return 0
            
            cumulative = 0
            peak = 0
            max_drawdown = 0
            
            for ret in returns:
                cumulative += ret
                if cumulative > peak:
                    peak = cumulative
                
                drawdown = (peak - cumulative) / peak * 100 if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown
            
        except Exception:
            return 0