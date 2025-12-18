"""
銘柄アーカイブリポジトリ
Stock Harvest AI - データアクセス層
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import sqlite3
from sqlalchemy import text, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from ..database.config import get_database_connection
from ..database.tables import stock_archive
from ..lib.logger import logger, PerformanceTracker
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ArchiveRepositoryError(Exception):
    """アーカイブリポジトリエラー"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "REPOSITORY_ERROR"
        self.details = details or {}
        super().__init__(message)


class ArchiveRepository:
    """銘柄アーカイブリポジトリ"""
    
    def __init__(self):
        """リポジトリ初期化"""
        self.table = stock_archive
        logger.debug("ArchiveRepository初期化完了")
    
    async def create_archive(self, archive_data: Dict[str, Any]) -> str:
        """アーカイブエントリ作成"""
        tracker = PerformanceTracker("create_archive")
        
        try:
            # IDの生成
            import uuid
            archive_id = f"archive-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
            
            # データベース接続取得
            db = await get_database_connection()
            
            # 現在日時の設定
            now = datetime.now()
            
            # データ準備
            insert_data = {
                'id': archive_id,
                'stock_code': archive_data['stock_code'],
                'stock_name': archive_data['stock_name'],
                'logic_type': archive_data['logic_type'],
                'detection_date': now,  # 現在日時を検出日時として使用
                'scan_id': archive_data['scan_id'],
                'price_at_detection': archive_data['price_at_detection'],
                'volume_at_detection': archive_data['volume_at_detection'],
                'market_cap_at_detection': archive_data.get('market_cap_at_detection'),
                'technical_signals_snapshot': json.dumps(archive_data.get('technical_signals_snapshot', {})),
                'logic_specific_data': json.dumps(archive_data.get('logic_specific_data', {})),
                'manual_score': archive_data.get('manual_score'),
                'manual_score_reason': archive_data.get('manual_score_reason'),
                'lessons_learned': archive_data.get('lessons_learned'),
                'follow_up_notes': archive_data.get('follow_up_notes'),
                'archive_status': 'active',
                'created_at': now,
                'updated_at': now
            }
            
            # データ挿入
            insert_stmt = self.table.insert().values(**insert_data)
            await db.execute(insert_stmt)
            await db.commit()
            
            logger.info(f"アーカイブエントリ作成完了: {archive_id}", {
                'archive_id': archive_id,
                'stock_code': archive_data['stock_code'],
                'logic_type': archive_data['logic_type']
            })
            
            tracker.end({'archive_id': archive_id})
            return archive_id
            
        except SQLAlchemyError as e:
            logger.error(f"アーカイブエントリ作成中にデータベースエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブエントリの作成中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"アーカイブエントリ作成中に予期しないエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブエントリの作成中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def search_archives(
        self, 
        search_params: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """アーカイブ検索"""
        tracker = PerformanceTracker("search_archives")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # ベースクエリ
            base_query = self.table.select()
            conditions = []
            
            # 検索条件の構築
            if stock_code := search_params.get('stock_code'):
                conditions.append(self.table.c.stock_code == stock_code)
                
            if logic_type := search_params.get('logic_type'):
                conditions.append(self.table.c.logic_type == logic_type)
                
            if date_from := search_params.get('date_from'):
                conditions.append(self.table.c.detection_date >= date_from)
                
            if date_to := search_params.get('date_to'):
                conditions.append(self.table.c.detection_date <= date_to)
                
            if outcome_classification := search_params.get('outcome_classification'):
                conditions.append(self.table.c.outcome_classification == outcome_classification)
                
            if manual_score := search_params.get('manual_score'):
                conditions.append(self.table.c.manual_score == manual_score)
            
            # アクティブなエントリのみ取得
            conditions.append(self.table.c.archive_status == 'active')
            
            # 条件の適用
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            # 総数取得
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as count_subquery"
            count_result = await db.execute(text(count_query))
            total_count = count_result.scalar()
            
            # ページネーション
            page = search_params.get('page', 1)
            limit = search_params.get('limit', 20)
            offset = (page - 1) * limit
            
            # データ取得（作成日時の降順）
            query = base_query.order_by(self.table.c.created_at.desc()).limit(limit).offset(offset)
            result = await db.execute(query)
            rows = result.fetchall()
            
            # 結果の変換
            archives = []
            for row in rows:
                archive_dict = dict(row._mapping)
                
                # JSON文字列をdictに変換
                for json_field in ['technical_signals_snapshot', 'logic_specific_data', 
                                  'trade_execution', 'market_conditions_snapshot']:
                    if archive_dict.get(json_field):
                        try:
                            archive_dict[json_field] = json.loads(archive_dict[json_field])
                        except (json.JSONDecodeError, TypeError):
                            archive_dict[json_field] = {}
                    else:
                        archive_dict[json_field] = {}
                
                archives.append(archive_dict)
            
            logger.info(f"アーカイブ検索完了: {len(archives)}件取得", {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'returned_count': len(archives)
            })
            
            tracker.end({'total_count': total_count, 'returned_count': len(archives)})
            return archives, total_count
            
        except SQLAlchemyError as e:
            logger.error(f"アーカイブ検索中にデータベースエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ検索中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"アーカイブ検索中に予期しないエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ検索中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_archive_by_id(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """ID によるアーカイブ取得"""
        tracker = PerformanceTracker("get_archive_by_id")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # クエリ実行
            query = self.table.select().where(self.table.c.id == archive_id)
            result = await db.execute(query)
            row = result.fetchone()
            
            if not row:
                logger.debug(f"アーカイブが見つかりません: {archive_id}")
                return None
            
            # 結果の変換
            archive_dict = dict(row._mapping)
            
            # JSON文字列をdictに変換
            for json_field in ['technical_signals_snapshot', 'logic_specific_data', 
                              'trade_execution', 'market_conditions_snapshot']:
                if archive_dict.get(json_field):
                    try:
                        archive_dict[json_field] = json.loads(archive_dict[json_field])
                    except (json.JSONDecodeError, TypeError):
                        archive_dict[json_field] = {}
                else:
                    archive_dict[json_field] = {}
            
            logger.debug(f"アーカイブ取得完了: {archive_id}")
            tracker.end({'archive_id': archive_id})
            return archive_dict
            
        except SQLAlchemyError as e:
            logger.error(f"アーカイブ取得中にデータベースエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"アーカイブ取得中に予期しないエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def update_archive(self, archive_id: str, update_data: Dict[str, Any]) -> bool:
        """アーカイブ更新"""
        tracker = PerformanceTracker("update_archive")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # 更新データ準備
            update_values = {}
            
            # 許可されたフィールドのみ更新
            allowed_fields = [
                'performance_after_1d', 'performance_after_1w', 'performance_after_1m',
                'max_gain', 'max_loss', 'outcome_classification', 'manual_score',
                'manual_score_reason', 'trade_execution', 'lessons_learned',
                'follow_up_notes', 'archive_status'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    value = update_data[field]
                    
                    # JSON フィールドの処理
                    if field in ['trade_execution'] and value is not None:
                        update_values[field] = json.dumps(value)
                    else:
                        update_values[field] = value
            
            # 更新する項目がない場合
            if not update_values:
                logger.debug(f"更新する項目がありません: {archive_id}")
                return False
            
            # 更新日時を設定
            update_values['updated_at'] = datetime.now()
            
            # 更新実行
            update_stmt = self.table.update().where(
                self.table.c.id == archive_id
            ).values(**update_values)
            
            result = await db.execute(update_stmt)
            await db.commit()
            
            # 更新された行数をチェック
            if result.rowcount == 0:
                logger.warning(f"更新対象のアーカイブが見つかりません: {archive_id}")
                return False
            
            logger.info(f"アーカイブ更新完了: {archive_id}", {
                'archive_id': archive_id,
                'updated_fields': list(update_values.keys())
            })
            
            tracker.end({'archive_id': archive_id, 'updated_fields': len(update_values)})
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"アーカイブ更新中にデータベースエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ更新中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"アーカイブ更新中に予期しないエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ更新中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def delete_archive(self, archive_id: str) -> bool:
        """アーカイブ削除（論理削除）"""
        tracker = PerformanceTracker("delete_archive")
        
        try:
            # ステータス更新による論理削除
            update_result = await self.update_archive(archive_id, {
                'archive_status': 'deleted'
            })
            
            if update_result:
                logger.info(f"アーカイブ論理削除完了: {archive_id}")
            
            tracker.end({'archive_id': archive_id, 'deleted': update_result})
            return update_result
            
        except Exception as e:
            logger.error(f"アーカイブ削除中にエラー: {e}")
            raise ArchiveRepositoryError(
                "アーカイブ削除中にエラーが発生しました",
                "DELETE_ERROR",
                {'error': str(e)}
            )
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """パフォーマンス統計取得"""
        tracker = PerformanceTracker("get_performance_stats")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # 基本統計
            stats = {}
            
            # 総アーカイブ件数
            total_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE archive_status = 'active'"
            total_result = await db.execute(text(total_query))
            stats['total_archived'] = total_result.scalar() or 0
            
            # ロジック別件数
            logic_a_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE logic_type = 'logic_a' AND archive_status = 'active'"
            logic_a_result = await db.execute(text(logic_a_query))
            stats['logic_a_count'] = logic_a_result.scalar() or 0
            
            logic_b_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE logic_type = 'logic_b' AND archive_status = 'active'"
            logic_b_result = await db.execute(text(logic_b_query))
            stats['logic_b_count'] = logic_b_result.scalar() or 0
            
            # 成功率計算
            if stats['total_archived'] > 0:
                success_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE outcome_classification = 'success' AND archive_status = 'active'"
                success_result = await db.execute(text(success_query))
                success_count = success_result.scalar() or 0
                stats['success_rate'] = (success_count / stats['total_archived']) * 100
            else:
                stats['success_rate'] = 0.0
            
            # 平均パフォーマンス
            performance_fields = ['performance_after_1d', 'performance_after_1w', 'performance_after_1m']
            for field in performance_fields:
                avg_query = f"SELECT AVG({field}) FROM {self.table.name} WHERE {field} IS NOT NULL AND archive_status = 'active'"
                avg_result = await db.execute(text(avg_query))
                avg_value = avg_result.scalar()
                stats[f'average_{field}'] = float(avg_value) if avg_value is not None else None
            
            # 手動スコア分布
            score_distribution = {}
            for score in ['S', 'A+', 'A', 'B', 'C']:
                score_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE manual_score = '{score}' AND archive_status = 'active'"
                score_result = await db.execute(text(score_query))
                score_distribution[score] = score_result.scalar() or 0
            
            stats['manual_score_distribution'] = score_distribution
            
            # 最高・最低パフォーマンス銘柄（簡易版）
            try:
                # 最高パフォーマンス
                best_query = f"""
                SELECT stock_code, stock_name, performance_after_1m 
                FROM {self.table.name} 
                WHERE performance_after_1m IS NOT NULL AND archive_status = 'active'
                ORDER BY performance_after_1m DESC 
                LIMIT 1
                """
                best_result = await db.execute(text(best_query))
                best_row = best_result.fetchone()
                
                if best_row:
                    stats['best_performing_stock'] = {
                        'stock_code': best_row[0],
                        'stock_name': best_row[1],
                        'performance': float(best_row[2])
                    }
                
                # 最低パフォーマンス
                worst_query = f"""
                SELECT stock_code, stock_name, performance_after_1m 
                FROM {self.table.name} 
                WHERE performance_after_1m IS NOT NULL AND archive_status = 'active'
                ORDER BY performance_after_1m ASC 
                LIMIT 1
                """
                worst_result = await db.execute(text(worst_query))
                worst_row = worst_result.fetchone()
                
                if worst_row:
                    stats['worst_performing_stock'] = {
                        'stock_code': worst_row[0],
                        'stock_name': worst_row[1],
                        'performance': float(worst_row[2])
                    }
                    
            except Exception as e:
                logger.warning(f"最高・最低パフォーマンス銘柄取得でエラー: {e}")
                stats['best_performing_stock'] = None
                stats['worst_performing_stock'] = None
            
            logger.info("パフォーマンス統計取得完了", stats)
            tracker.end({'total_archived': stats['total_archived']})
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"パフォーマンス統計取得中にデータベースエラー: {e}")
            raise ArchiveRepositoryError(
                "パフォーマンス統計取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"パフォーマンス統計取得中に予期しないエラー: {e}")
            raise ArchiveRepositoryError(
                "パフォーマンス統計取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )