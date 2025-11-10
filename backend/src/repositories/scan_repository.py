"""
スキャンリポジトリ
スキャン実行履歴と結果のデータベース操作
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncpg
from ..database.config import get_db_connection
from ..database.tables import scan_executions, scan_results, stock_master
import logging

logger = logging.getLogger(__name__)

class ScanRepository:
    
    async def create_scan_execution(self, scan_execution: Dict) -> Dict:
        """
        新しいスキャン実行記録を作成
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                INSERT INTO scan_executions 
                (id, status, progress, total_stocks, processed_stocks, current_stock, 
                 estimated_time, message, logic_a_count, logic_b_count, error_message)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """
                
                result = await conn.fetchrow(
                    query,
                    scan_execution['id'],
                    scan_execution['status'],
                    scan_execution['progress'],
                    scan_execution['total_stocks'],
                    scan_execution['processed_stocks'],
                    scan_execution['current_stock'],
                    scan_execution['estimated_time'],
                    scan_execution['message'],
                    scan_execution['logic_a_count'],
                    scan_execution['logic_b_count'],
                    scan_execution['error_message']
                )
                
                return dict(result) if result else {}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン実行記録作成エラー: {str(e)}")
            raise
    
    async def update_scan_execution(self, scan_id: str, updates: Dict) -> Dict:
        """
        スキャン実行記録を更新
        """
        try:
            conn = await get_db_connection()
            try:
                # 動的にUPDATEクエリを構築
                set_clauses = []
                values = []
                param_count = 1
                
                for key, value in updates.items():
                    if key in ['progress', 'total_stocks', 'processed_stocks', 'estimated_time', 
                              'logic_a_count', 'logic_b_count', 'status', 'message', 'current_stock',
                              'error_message', 'completed_at']:
                        set_clauses.append(f"{key} = ${param_count}")
                        values.append(value)
                        param_count += 1
                
                if not set_clauses:
                    return {}
                
                values.append(scan_id)  # WHERE条件のパラメータ
                
                query = f"""
                UPDATE scan_executions 
                SET {', '.join(set_clauses)}
                WHERE id = ${param_count}
                RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                return dict(result) if result else {}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン実行記録更新エラー: {str(e)}")
            raise
    
    async def get_latest_scan_execution(self) -> Optional[Dict]:
        """
        最新のスキャン実行記録を取得
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT * FROM scan_executions 
                ORDER BY started_at DESC 
                LIMIT 1
                """
                
                result = await conn.fetchrow(query)
                return dict(result) if result else None
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"最新スキャン実行記録取得エラー: {str(e)}")
            return None
    
    async def get_latest_completed_scan(self) -> Optional[Dict]:
        """
        最新の完了したスキャン実行記録を取得
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT * FROM scan_executions 
                WHERE status = 'completed'
                ORDER BY completed_at DESC 
                LIMIT 1
                """
                
                result = await conn.fetchrow(query)
                return dict(result) if result else None
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"完了済みスキャン取得エラー: {str(e)}")
            return None
    
    async def create_scan_result(self, scan_result: Dict) -> Dict:
        """
        スキャン結果を作成
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                INSERT INTO scan_results 
                (id, scan_id, stock_code, stock_name, price, change, change_rate, 
                 volume, logic_type, technical_signals, market_cap)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """
                
                import json
                technical_signals_json = json.dumps(scan_result['technical_signals'])
                
                result = await conn.fetchrow(
                    query,
                    scan_result['id'],
                    scan_result['scan_id'],
                    scan_result['stock_code'],
                    scan_result['stock_name'],
                    scan_result['price'],
                    scan_result['change'],
                    scan_result['change_rate'],
                    scan_result['volume'],
                    scan_result['logic_type'],
                    technical_signals_json,
                    scan_result['market_cap']
                )
                
                return dict(result) if result else {}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン結果作成エラー: {str(e)}")
            raise
    
    async def get_scan_results_by_logic(self, scan_id: str, logic_type: str) -> List[Dict]:
        """
        指定されたスキャンIDとロジックタイプのスキャン結果を取得
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT * FROM scan_results 
                WHERE scan_id = $1 AND logic_type = $2
                ORDER BY detected_at DESC
                """
                
                results = await conn.fetch(query, scan_id, logic_type)
                return [dict(result) for result in results]
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン結果取得エラー: {str(e)}")
            return []
    
    async def get_scan_results(self, scan_id: str) -> List[Dict]:
        """
        指定されたスキャンIDの全スキャン結果を取得
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT * FROM scan_results 
                WHERE scan_id = $1
                ORDER BY detected_at DESC
                """
                
                results = await conn.fetch(query, scan_id)
                return [dict(result) for result in results]
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン結果取得エラー: {str(e)}")
            return []
    
    async def cleanup_old_scan_data(self, days_to_keep: int = 30) -> int:
        """
        古いスキャンデータをクリーンアップ
        """
        try:
            conn = await get_db_connection()
            try:
                # 古いスキャン結果を削除
                result_query = """
                DELETE FROM scan_results 
                WHERE detected_at < NOW() - INTERVAL '%s days'
                """
                
                # 古いスキャン実行記録を削除
                execution_query = """
                DELETE FROM scan_executions 
                WHERE started_at < NOW() - INTERVAL '%s days'
                """
                
                result_count = await conn.execute(result_query, days_to_keep)
                execution_count = await conn.execute(execution_query, days_to_keep)
                
                # 削除された行数を解析
                result_deleted = int(result_count.split()[1]) if 'DELETE' in result_count else 0
                execution_deleted = int(execution_count.split()[1]) if 'DELETE' in execution_count else 0
                
                logger.info(f"クリーンアップ完了: スキャン結果{result_deleted}件, スキャン実行記録{execution_deleted}件を削除")
                
                return result_deleted + execution_deleted
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャンデータクリーンアップエラー: {str(e)}")
            return 0
    
    async def create_or_update_stock_master(self, stock_info: Dict) -> Dict:
        """
        銘柄マスタ情報を作成または更新
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                INSERT INTO stock_master (code, name, market, sector, is_active, metadata_info)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (code) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    market = EXCLUDED.market,
                    sector = EXCLUDED.sector,
                    is_active = EXCLUDED.is_active,
                    metadata_info = EXCLUDED.metadata_info,
                    last_updated = NOW()
                RETURNING *
                """
                
                import json
                metadata_json = json.dumps(stock_info.get('metadata_info', {}))
                
                result = await conn.fetchrow(
                    query,
                    stock_info['code'],
                    stock_info['name'],
                    stock_info.get('market'),
                    stock_info.get('sector'),
                    stock_info.get('is_active', True),
                    metadata_json
                )
                
                return dict(result) if result else {}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"銘柄マスタ更新エラー: {str(e)}")
            raise
    
    async def get_active_stocks(self) -> List[Dict]:
        """
        アクティブな銘柄一覧を取得
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT * FROM stock_master 
                WHERE is_active = true
                ORDER BY code
                """
                
                results = await conn.fetch(query)
                return [dict(result) for result in results]
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"アクティブ銘柄取得エラー: {str(e)}")
            return []