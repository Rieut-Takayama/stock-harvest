"""
手動スコア評価リポジトリ
Stock Harvest AI - データアクセス層
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import sqlite3
from sqlalchemy import text, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from ..database.config import get_database_connection
from ..database.tables import manual_scores
from ..lib.logger import logger, PerformanceTracker
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ManualScoresRepositoryError(Exception):
    """手動スコア評価リポジトリエラー"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "REPOSITORY_ERROR"
        self.details = details or {}
        super().__init__(message)


class ManualScoresRepository:
    """手動スコア評価リポジトリ"""
    
    def __init__(self):
        """リポジトリ初期化"""
        self.table = manual_scores
        logger.debug("ManualScoresRepository初期化完了")
    
    async def create_score_evaluation(self, evaluation_data: Dict[str, Any]) -> str:
        """スコア評価作成"""
        tracker = PerformanceTracker("create_score_evaluation")
        
        try:
            # IDの生成
            import uuid
            score_id = f"score-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
            
            # データベース接続取得
            db = await get_database_connection()
            
            # 現在日時の設定
            now = datetime.now()
            
            # データ準備
            insert_data = {
                'id': score_id,
                'stock_code': evaluation_data['stock_code'],
                'stock_name': evaluation_data['stock_name'],
                'score': evaluation_data['score'],
                'logic_type': evaluation_data['logic_type'],
                'scan_result_id': evaluation_data.get('scan_result_id'),
                'evaluation_reason': evaluation_data['evaluation_reason'],
                'evaluated_by': evaluation_data.get('evaluated_by', 'user'),
                'evaluated_at': now,
                'confidence_level': evaluation_data.get('confidence_level'),
                'price_at_evaluation': evaluation_data.get('price_at_evaluation'),
                'market_context': json.dumps(evaluation_data.get('market_context', {})),
                'ai_score_before': evaluation_data.get('ai_score_before'),
                'ai_score_after': evaluation_data.get('ai_score_after'),
                'score_change_history': json.dumps([]),  # 初期は空の配列
                'follow_up_required': evaluation_data.get('follow_up_required', False),
                'follow_up_date': evaluation_data.get('follow_up_date'),
                'performance_validation': json.dumps(evaluation_data.get('performance_validation', {})),
                'tags': json.dumps(evaluation_data.get('tags', [])),
                'is_learning_case': evaluation_data.get('is_learning_case', False),
                'status': 'active',
                'created_at': now,
                'updated_at': now
            }
            
            # データ挿入
            insert_stmt = self.table.insert().values(**insert_data)
            await db.execute(insert_stmt)
            await db.commit()
            
            logger.info(f"スコア評価作成完了: {score_id}", {
                'score_id': score_id,
                'stock_code': evaluation_data['stock_code'],
                'score': evaluation_data['score'],
                'logic_type': evaluation_data['logic_type']
            })
            
            tracker.end({'score_id': score_id})
            return score_id
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価作成中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価の作成中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価作成中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価の作成中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_score_by_stock(self, stock_code: str, logic_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """銘柄の最新スコア評価取得"""
        tracker = PerformanceTracker("get_score_by_stock")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # クエリ構築
            conditions = [
                self.table.c.stock_code == stock_code,
                self.table.c.status == 'active'
            ]
            
            if logic_type:
                conditions.append(self.table.c.logic_type == logic_type)
            
            # 最新のスコア評価を取得
            query = self.table.select().where(
                and_(*conditions)
            ).order_by(self.table.c.evaluated_at.desc()).limit(1)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            if not row:
                logger.debug(f"スコア評価が見つかりません: {stock_code}, {logic_type}")
                return None
            
            # 結果の変換
            score_dict = dict(row._mapping)
            
            # JSON文字列をdictに変換
            for json_field in ['market_context', 'score_change_history', 'performance_validation', 'tags']:
                if score_dict.get(json_field):
                    try:
                        score_dict[json_field] = json.loads(score_dict[json_field])
                    except (json.JSONDecodeError, TypeError):
                        if json_field == 'tags':
                            score_dict[json_field] = []
                        else:
                            score_dict[json_field] = {}
                else:
                    if json_field == 'tags':
                        score_dict[json_field] = []
                    else:
                        score_dict[json_field] = {}
            
            logger.debug(f"スコア評価取得完了: {stock_code}")
            tracker.end({'stock_code': stock_code})
            return score_dict
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価取得中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価取得中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_score_by_id(self, score_id: str) -> Optional[Dict[str, Any]]:
        """ID によるスコア評価取得"""
        tracker = PerformanceTracker("get_score_by_id")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # クエリ実行
            query = self.table.select().where(self.table.c.id == score_id)
            result = await db.execute(query)
            row = result.fetchone()
            
            if not row:
                logger.debug(f"スコア評価が見つかりません: {score_id}")
                return None
            
            # 結果の変換
            score_dict = dict(row._mapping)
            
            # JSON文字列をdictに変換
            for json_field in ['market_context', 'score_change_history', 'performance_validation', 'tags']:
                if score_dict.get(json_field):
                    try:
                        score_dict[json_field] = json.loads(score_dict[json_field])
                    except (json.JSONDecodeError, TypeError):
                        if json_field == 'tags':
                            score_dict[json_field] = []
                        else:
                            score_dict[json_field] = {}
                else:
                    if json_field == 'tags':
                        score_dict[json_field] = []
                    else:
                        score_dict[json_field] = {}
            
            logger.debug(f"スコア評価取得完了: {score_id}")
            tracker.end({'score_id': score_id})
            return score_dict
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価取得中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価取得中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def update_score_evaluation(self, score_id: str, update_data: Dict[str, Any]) -> bool:
        """スコア評価更新"""
        tracker = PerformanceTracker("update_score_evaluation")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # 現在のデータを取得（履歴記録用）
            current_score = await self.get_score_by_id(score_id)
            if not current_score:
                logger.warning(f"更新対象のスコア評価が見つかりません: {score_id}")
                return False
            
            # 更新データ準備
            update_values = {}
            change_history = current_score.get('score_change_history', [])
            
            # 許可されたフィールドのみ更新
            allowed_fields = [
                'score', 'evaluation_reason', 'confidence_level', 'price_at_evaluation',
                'ai_score_after', 'follow_up_required', 'follow_up_date', 'performance_validation',
                'tags', 'is_learning_case', 'status'
            ]
            
            # 変更履歴エントリ準備
            change_entry = {
                'changed_at': datetime.now().isoformat(),
                'changed_by': update_data.get('changed_by', 'user'),
                'change_reason': update_data.get('change_reason', ''),
                'changes': {}
            }
            
            for field in allowed_fields:
                if field in update_data:
                    new_value = update_data[field]
                    old_value = current_score.get(field)
                    
                    # 変更があった場合のみ記録
                    if new_value != old_value:
                        # JSON フィールドの処理
                        if field in ['performance_validation'] and new_value is not None:
                            update_values[field] = json.dumps(new_value)
                        elif field == 'tags' and new_value is not None:
                            update_values[field] = json.dumps(new_value)
                        else:
                            update_values[field] = new_value
                        
                        # 変更履歴に記録
                        change_entry['changes'][field] = {
                            'old': old_value,
                            'new': new_value
                        }
            
            # 変更する項目がない場合
            if not update_values:
                logger.debug(f"更新する項目がありません: {score_id}")
                return False
            
            # 変更履歴の更新
            if change_entry['changes']:
                change_history.append(change_entry)
                update_values['score_change_history'] = json.dumps(change_history)
            
            # 更新日時を設定
            update_values['updated_at'] = datetime.now()
            
            # 更新実行
            update_stmt = self.table.update().where(
                self.table.c.id == score_id
            ).values(**update_values)
            
            result = await db.execute(update_stmt)
            await db.commit()
            
            # 更新された行数をチェック
            if result.rowcount == 0:
                logger.warning(f"更新対象のスコア評価が見つかりません: {score_id}")
                return False
            
            logger.info(f"スコア評価更新完了: {score_id}", {
                'score_id': score_id,
                'updated_fields': list(update_values.keys()),
                'changes_count': len(change_entry['changes'])
            })
            
            tracker.end({'score_id': score_id, 'updated_fields': len(update_values)})
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価更新中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価更新中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価更新中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価更新中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def search_score_evaluations(
        self, 
        search_params: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """スコア評価検索"""
        tracker = PerformanceTracker("search_score_evaluations")
        
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
                
            if score := search_params.get('score'):
                conditions.append(self.table.c.score == score)
                
            if confidence_level := search_params.get('confidence_level'):
                conditions.append(self.table.c.confidence_level == confidence_level)
                
            if date_from := search_params.get('date_from'):
                conditions.append(self.table.c.evaluated_at >= date_from)
                
            if date_to := search_params.get('date_to'):
                conditions.append(self.table.c.evaluated_at <= date_to)
                
            if status := search_params.get('status'):
                conditions.append(self.table.c.status == status)
            else:
                # デフォルトはアクティブなエントリのみ
                conditions.append(self.table.c.status == 'active')
            
            # フラグ検索
            if 'is_learning_case' in search_params:
                conditions.append(self.table.c.is_learning_case == search_params['is_learning_case'])
                
            if 'follow_up_required' in search_params:
                conditions.append(self.table.c.follow_up_required == search_params['follow_up_required'])
            
            # TODO: タグ検索（JSON内の配列検索）は今回は省略
            
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
            
            # データ取得（評価日時の降順）
            query = base_query.order_by(self.table.c.evaluated_at.desc()).limit(limit).offset(offset)
            result = await db.execute(query)
            rows = result.fetchall()
            
            # 結果の変換
            evaluations = []
            for row in rows:
                eval_dict = dict(row._mapping)
                
                # JSON文字列をdictに変換
                for json_field in ['market_context', 'score_change_history', 'performance_validation', 'tags']:
                    if eval_dict.get(json_field):
                        try:
                            eval_dict[json_field] = json.loads(eval_dict[json_field])
                        except (json.JSONDecodeError, TypeError):
                            if json_field == 'tags':
                                eval_dict[json_field] = []
                            else:
                                eval_dict[json_field] = {}
                    else:
                        if json_field == 'tags':
                            eval_dict[json_field] = []
                        else:
                            eval_dict[json_field] = {}
                
                evaluations.append(eval_dict)
            
            logger.info(f"スコア評価検索完了: {len(evaluations)}件取得", {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'returned_count': len(evaluations)
            })
            
            tracker.end({'total_count': total_count, 'returned_count': len(evaluations)})
            return evaluations, total_count
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価検索中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価検索中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価検索中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価検索中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_score_history(self, stock_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """銘柄のスコア評価履歴取得"""
        tracker = PerformanceTracker("get_score_history")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # 履歴取得
            query = self.table.select().where(
                self.table.c.stock_code == stock_code
            ).order_by(self.table.c.evaluated_at.desc()).limit(limit)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            # 結果の変換
            history = []
            for row in rows:
                eval_dict = dict(row._mapping)
                
                # 必要最小限の情報のみ返す
                history_item = {
                    'id': eval_dict['id'],
                    'score': eval_dict['score'],
                    'logic_type': eval_dict['logic_type'],
                    'evaluation_reason': eval_dict['evaluation_reason'],
                    'evaluated_by': eval_dict['evaluated_by'],
                    'evaluated_at': eval_dict['evaluated_at'],
                    'confidence_level': eval_dict['confidence_level'],
                    'status': eval_dict['status'],
                    'is_learning_case': eval_dict['is_learning_case']
                }
                
                history.append(history_item)
            
            logger.debug(f"スコア評価履歴取得完了: {stock_code}, {len(history)}件")
            tracker.end({'stock_code': stock_code, 'count': len(history)})
            return history
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価履歴取得中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価履歴取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価履歴取得中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価履歴取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_evaluation_stats(self) -> Dict[str, Any]:
        """スコア評価統計取得"""
        tracker = PerformanceTracker("get_evaluation_stats")
        
        try:
            # データベース接続取得
            db = await get_database_connection()
            
            # 基本統計
            stats = {}
            
            # 総評価件数
            total_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE status = 'active'"
            total_result = await db.execute(text(total_query))
            stats['total_evaluations'] = total_result.scalar() or 0
            
            # スコア分布
            score_distribution = {}
            for score in ['S', 'A+', 'A', 'B', 'C']:
                score_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE score = '{score}' AND status = 'active'"
                score_result = await db.execute(text(score_query))
                score_distribution[score] = score_result.scalar() or 0
            
            stats['score_distribution'] = score_distribution
            
            # 確信度分布
            confidence_distribution = {}
            for level in ['high', 'medium', 'low']:
                conf_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE confidence_level = '{level}' AND status = 'active'"
                conf_result = await db.execute(text(conf_query))
                confidence_distribution[level] = conf_result.scalar() or 0
            
            # NULL値の件数も取得
            null_conf_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE confidence_level IS NULL AND status = 'active'"
            null_conf_result = await db.execute(text(null_conf_query))
            confidence_distribution['not_specified'] = null_conf_result.scalar() or 0
            
            stats['confidence_distribution'] = confidence_distribution
            
            # ロジック別分布
            logic_type_distribution = {}
            for logic in ['logic_a', 'logic_b']:
                logic_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE logic_type = '{logic}' AND status = 'active'"
                logic_result = await db.execute(text(logic_query))
                logic_type_distribution[logic] = logic_result.scalar() or 0
            
            stats['logic_type_distribution'] = logic_type_distribution
            
            # 学習事例件数
            learning_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE is_learning_case = 1 AND status = 'active'"
            learning_result = await db.execute(text(learning_query))
            stats['learning_cases_count'] = learning_result.scalar() or 0
            
            # フォローアップ待ち件数
            follow_up_query = f"SELECT COUNT(*) FROM {self.table.name} WHERE follow_up_required = 1 AND status = 'active'"
            follow_up_result = await db.execute(text(follow_up_query))
            stats['follow_up_pending_count'] = follow_up_result.scalar() or 0
            
            # 最近の評価（簡易版）
            try:
                recent_query = f"""
                SELECT id, stock_code, stock_name, score, logic_type, evaluated_at 
                FROM {self.table.name} 
                WHERE status = 'active'
                ORDER BY evaluated_at DESC 
                LIMIT 5
                """
                recent_result = await db.execute(text(recent_query))
                recent_rows = recent_result.fetchall()
                
                recent_evaluations = []
                for row in recent_rows:
                    recent_evaluations.append({
                        'id': row[0],
                        'stock_code': row[1],
                        'stock_name': row[2],
                        'score': row[3],
                        'logic_type': row[4],
                        'evaluated_at': row[5]
                    })
                
                stats['recent_evaluations'] = recent_evaluations
                
            except Exception as e:
                logger.warning(f"最近の評価取得でエラー: {e}")
                stats['recent_evaluations'] = []
            
            logger.info("スコア評価統計取得完了", {
                'total_evaluations': stats['total_evaluations'],
                'recent_count': len(stats['recent_evaluations'])
            })
            
            tracker.end({'total_evaluations': stats['total_evaluations']})
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"スコア評価統計取得中にデータベースエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価統計取得中にデータベースエラーが発生しました",
                "DATABASE_ERROR",
                {'error': str(e)}
            )
        except Exception as e:
            logger.error(f"スコア評価統計取得中に予期しないエラー: {e}")
            raise ManualScoresRepositoryError(
                "スコア評価統計取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )