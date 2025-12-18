"""
スキャンリポジトリ
スキャン実行履歴と結果のデータベース操作
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..database.config import get_db_connection
from ..database.tables import scan_executions, scan_results, stock_master
from ..lib.logger import logger

class ScanRepository:
    
    async def create_scan_execution(self, scan_execution: Dict) -> Dict:
        """
        新しいスキャン実行記録を作成
        """
        try:
            database = await get_db_connection()
            query = """
            INSERT INTO scan_executions 
            (id, status, progress, total_stocks, processed_stocks, current_stock, 
             estimated_time, message, logic_a_count, logic_b_count, error_message)
            VALUES (:id, :status, :progress, :total_stocks, :processed_stocks, :current_stock, 
                    :estimated_time, :message, :logic_a_count, :logic_b_count, :error_message)
            """
            
            values = {
                'id': scan_execution['id'],
                'status': scan_execution['status'],
                'progress': scan_execution['progress'],
                'total_stocks': scan_execution['total_stocks'],
                'processed_stocks': scan_execution['processed_stocks'],
                'current_stock': scan_execution['current_stock'],
                'estimated_time': scan_execution['estimated_time'],
                'message': scan_execution['message'],
                'logic_a_count': scan_execution['logic_a_count'],
                'logic_b_count': scan_execution['logic_b_count'],
                'error_message': scan_execution['error_message']
            }
            
            await database.execute(query, values)
            
            # 作成されたレコードを取得
            result = await database.fetch_one(
                "SELECT * FROM scan_executions WHERE id = :id", 
                {"id": scan_execution['id']}
            )
            
            return dict(result) if result else {}
                
        except Exception as e:
            logger.error(f"スキャン実行記録作成エラー: {str(e)}")
            raise
    
    async def update_scan_execution(self, scan_id: str, updates: Dict) -> Dict:
        """
        スキャン実行記録を更新
        """
        try:
            database = await get_db_connection()
            
            # 動的にUPDATEクエリを構築
            set_clauses = []
            values = {'id': scan_id}
            
            for key, value in updates.items():
                if key in ['progress', 'total_stocks', 'processed_stocks', 'estimated_time', 
                          'logic_a_count', 'logic_b_count', 'status', 'message', 'current_stock',
                          'error_message', 'completed_at']:
                    set_clauses.append(f"{key} = :{key}")
                    values[key] = value
            
            if not set_clauses:
                return {}
            
            query = f"""
            UPDATE scan_executions 
            SET {', '.join(set_clauses)}
            WHERE id = :id
            """
            
            await database.execute(query, values)
            
            # 更新されたレコードを取得
            result = await database.fetch_one(
                "SELECT * FROM scan_executions WHERE id = :id", 
                {"id": scan_id}
            )
            return dict(result) if result else {}
                
        except Exception as e:
            logger.error(f"スキャン実行記録更新エラー: {str(e)}")
            raise
    
    async def get_latest_scan_execution(self) -> Optional[Dict]:
        """
        最新のスキャン実行記録を取得
        """
        try:
            database = await get_db_connection()
            query = """
            SELECT * FROM scan_executions 
            ORDER BY started_at DESC 
            LIMIT 1
            """
            
            result = await database.fetch_one(query)
            return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"最新スキャン実行記録取得エラー: {str(e)}")
            return None
    
    async def get_latest_completed_scan(self) -> Optional[Dict]:
        """
        最新の完了したスキャン実行記録を取得
        """
        try:
            database = await get_db_connection()
            query = """
            SELECT * FROM scan_executions 
            WHERE status = 'completed'
            ORDER BY completed_at DESC 
            LIMIT 1
            """
            
            result = await database.fetch_one(query)
            return dict(result) if result else None
                
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
    
    # パフォーマンス最適化とバッチ処理メソッド
    async def batch_create_scan_results(self, scan_results: List[Dict]) -> Dict:
        """
        バッチでスキャン結果を作成 - パフォーマンス最適化
        """
        try:
            if not scan_results:
                return {'created_count': 0}
            
            conn = await get_db_connection()
            try:
                # バッチINSERT用のクエリ構築
                placeholders = []
                values = []
                param_count = 1
                
                for result in scan_results:
                    import json
                    technical_signals_json = json.dumps(result['technical_signals'])
                    
                    placeholder = f"(${param_count}, ${param_count+1}, ${param_count+2}, ${param_count+3}, ${param_count+4}, ${param_count+5}, ${param_count+6}, ${param_count+7}, ${param_count+8}, ${param_count+9}, ${param_count+10})"
                    placeholders.append(placeholder)
                    
                    values.extend([
                        result['id'], result['scan_id'], result['stock_code'], 
                        result['stock_name'], result['price'], result['change'],
                        result['change_rate'], result['volume'], result['logic_type'],
                        technical_signals_json, result['market_cap']
                    ])
                    
                    param_count += 11
                
                query = f"""
                INSERT INTO scan_results 
                (id, scan_id, stock_code, stock_name, price, change, change_rate, 
                 volume, logic_type, technical_signals, market_cap)
                VALUES {', '.join(placeholders)}
                """
                
                await conn.execute(query, *values)
                
                logger.info(f"バッチスキャン結果作成完了: {len(scan_results)}件")
                return {'created_count': len(scan_results)}
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"バッチスキャン結果作成エラー: {str(e)}")
            raise
    
    async def get_scan_execution_stats(self) -> Dict:
        """
        スキャン実行統計を取得 - 管理機能強化
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                SELECT 
                    COUNT(*) as total_scans,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_scans,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_scans,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_scans,
                    AVG(CASE WHEN status = 'completed' THEN processed_stocks END) as avg_processed_stocks,
                    MAX(logic_a_count + logic_b_count) as max_detections
                FROM scan_executions
                WHERE started_at >= NOW() - INTERVAL '30 days'
                """
                
                result = await conn.fetchrow(query)
                
                return {
                    'total_scans': result['total_scans'] or 0,
                    'completed_scans': result['completed_scans'] or 0,
                    'failed_scans': result['failed_scans'] or 0,
                    'running_scans': result['running_scans'] or 0,
                    'avg_processed_stocks': float(result['avg_processed_stocks'] or 0),
                    'max_detections': result['max_detections'] or 0,
                    'success_rate': round((result['completed_scans'] or 0) / max(result['total_scans'] or 1, 1) * 100, 2)
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャン統計取得エラー: {str(e)}")
            return {}
    
    async def cancel_running_scan(self, scan_id: str) -> bool:
        """
        実行中のスキャンをキャンセル - 運用機能強化
        """
        try:
            conn = await get_db_connection()
            try:
                query = """
                UPDATE scan_executions 
                SET status = 'cancelled',
                    message = 'スキャンがキャンセルされました',
                    completed_at = NOW()
                WHERE id = $1 AND status = 'running'
                RETURNING id
                """
                
                result = await conn.fetchrow(query, scan_id)
                
                if result:
                    logger.info(f"スキャンキャンセル完了: {scan_id}")
                    return True
                else:
                    logger.warning(f"キャンセル対象スキャンが見つからない: {scan_id}")
                    return False
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"スキャンキャンセルエラー: {str(e)}")
            return False
    
    async def optimize_database_performance(self) -> Dict:
        """
        データベースパフォーマンス最適化 - 自動メンテナンス
        """
        try:
            conn = await get_db_connection()
            try:
                # インデックス作成確認
                index_queries = [
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_executions_status ON scan_executions(status)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_executions_started_at ON scan_executions(started_at)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_logic_type ON scan_results(logic_type)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_results_detected_at ON scan_results(detected_at)"
                ]
                
                created_indexes = 0
                for index_query in index_queries:
                    try:
                        await conn.execute(index_query)
                        created_indexes += 1
                    except Exception as idx_e:
                        logger.debug(f"インデックス作成スキップ: {str(idx_e)}")
                
                # テーブル統計更新
                await conn.execute("ANALYZE scan_executions")
                await conn.execute("ANALYZE scan_results")
                
                logger.info(f"データベース最適化完了: インデックス{created_indexes}件作成")
                
                return {
                    'success': True,
                    'indexes_created': created_indexes,
                    'tables_analyzed': 2
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"データベース最適化エラー: {str(e)}")
            return {'success': False, 'error': str(e)}