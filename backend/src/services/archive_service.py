"""
銘柄アーカイブサービス
Stock Harvest AI - ビジネスロジック層
"""

import csv
import io
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from ..repositories.archive_repository import ArchiveRepository, ArchiveRepositoryError
from ..validators.archive_validators import ArchiveValidator, ArchiveValidationError
from ..lib.logger import logger, PerformanceTracker


class ArchiveServiceError(Exception):
    """アーカイブサービスエラー"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "SERVICE_ERROR"
        self.details = details or {}
        super().__init__(message)


class ArchiveService:
    """銘柄アーカイブサービス"""
    
    def __init__(self):
        """サービス初期化"""
        self.repository = ArchiveRepository()
        logger.debug("ArchiveService初期化完了")
    
    async def create_archive_entry(self, archive_data: Dict[str, Any]) -> Dict[str, Any]:
        """アーカイブエントリ作成"""
        tracker = PerformanceTracker("create_archive_entry")
        
        try:
            # バリデーション
            validated_data = ArchiveValidator.validate_create_request(archive_data)
            
            # アーカイブエントリ作成
            archive_id = await self.repository.create_archive(validated_data)
            
            # 作成されたエントリを取得して返す
            created_archive = await self.repository.get_archive_by_id(archive_id)
            
            logger.info(f"アーカイブエントリ作成サービス完了: {archive_id}", {
                'archive_id': archive_id,
                'stock_code': validated_data['stock_code'],
                'logic_type': validated_data['logic_type']
            })
            
            tracker.end({'archive_id': archive_id})
            return {
                'success': True,
                'archive_id': archive_id,
                'archive': created_archive,
                'message': 'アーカイブエントリを正常に作成しました'
            }
            
        except ArchiveValidationError as e:
            logger.warning(f"アーカイブエントリ作成バリデーションエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ArchiveRepositoryError as e:
            logger.error(f"アーカイブエントリ作成リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"アーカイブエントリ作成中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "アーカイブエントリの作成中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def search_archives(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """アーカイブ検索"""
        tracker = PerformanceTracker("search_archives")
        
        try:
            # バリデーション
            validated_params = ArchiveValidator.validate_search_request(search_params)
            
            # 検索実行
            archives, total_count = await self.repository.search_archives(validated_params)
            
            # ページネーション情報計算
            page = validated_params.get('page', 1)
            limit = validated_params.get('limit', 20)
            has_next = (page * limit) < total_count
            
            logger.info(f"アーカイブ検索サービス完了: {len(archives)}件取得", {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'returned_count': len(archives)
            })
            
            tracker.end({'total_count': total_count, 'returned_count': len(archives)})
            return {
                'success': True,
                'archives': archives,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'limit': limit,
                    'has_next': has_next,
                    'total_pages': (total_count + limit - 1) // limit
                },
                'search_params': validated_params
            }
            
        except ArchiveValidationError as e:
            logger.warning(f"アーカイブ検索バリデーションエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ArchiveRepositoryError as e:
            logger.error(f"アーカイブ検索リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"アーカイブ検索中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "アーカイブ検索中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_archive_details(self, archive_id: str) -> Dict[str, Any]:
        """アーカイブ詳細取得"""
        tracker = PerformanceTracker("get_archive_details")
        
        try:
            # ID のバリデーション
            if not archive_id or not isinstance(archive_id, str):
                raise ArchiveServiceError(
                    "アーカイブIDが無効です",
                    "INVALID_ID"
                )
            
            # アーカイブ取得
            archive = await self.repository.get_archive_by_id(archive_id.strip())
            
            if not archive:
                logger.warning(f"アーカイブが見つかりません: {archive_id}")
                raise ArchiveServiceError(
                    "指定されたアーカイブが見つかりません",
                    "NOT_FOUND"
                )
            
            # 削除済みエントリのチェック
            if archive.get('archive_status') == 'deleted':
                logger.warning(f"削除済みアーカイブへのアクセス: {archive_id}")
                raise ArchiveServiceError(
                    "指定されたアーカイブは削除されています",
                    "DELETED"
                )
            
            logger.debug(f"アーカイブ詳細取得サービス完了: {archive_id}")
            tracker.end({'archive_id': archive_id})
            return {
                'success': True,
                'archive': archive
            }
            
        except ArchiveServiceError:
            raise
        except ArchiveRepositoryError as e:
            logger.error(f"アーカイブ詳細取得リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"アーカイブ詳細取得中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "アーカイブ詳細取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def update_archive_performance(self, archive_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """アーカイブパフォーマンス更新"""
        tracker = PerformanceTracker("update_archive_performance")
        
        try:
            # ID のバリデーション
            if not archive_id or not isinstance(archive_id, str):
                raise ArchiveServiceError(
                    "アーカイブIDが無効です",
                    "INVALID_ID"
                )
            
            # 更新データのバリデーション
            validated_updates = {}
            
            # パフォーマンス関連フィールド
            performance_fields = [
                'performance_after_1d', 'performance_after_1w', 'performance_after_1m',
                'max_gain', 'max_loss'
            ]
            
            for field in performance_fields:
                if field in update_data:
                    value = update_data[field]
                    if value is not None:
                        validated_updates[field] = ArchiveValidator.validate_percentage(value, field)
                    else:
                        validated_updates[field] = None
            
            # 結果分類
            if outcome_classification := update_data.get('outcome_classification'):
                validated_updates['outcome_classification'] = ArchiveValidator.validate_outcome_classification(
                    outcome_classification
                )
            
            # 手動スコア
            if manual_score := update_data.get('manual_score'):
                validated_updates['manual_score'] = ArchiveValidator.validate_manual_score(manual_score)
            
            if manual_score_reason := update_data.get('manual_score_reason'):
                validated_updates['manual_score_reason'] = ArchiveValidator.validate_text_field(
                    manual_score_reason, "manual_score_reason", 500
                )
            
            # 学習事項・フォローアップメモ
            if lessons_learned := update_data.get('lessons_learned'):
                validated_updates['lessons_learned'] = ArchiveValidator.validate_text_field(
                    lessons_learned, "lessons_learned", 2000
                )
            
            if follow_up_notes := update_data.get('follow_up_notes'):
                validated_updates['follow_up_notes'] = ArchiveValidator.validate_text_field(
                    follow_up_notes, "follow_up_notes", 1000
                )
            
            # 売買実行情報、アーカイブステータス
            if trade_execution := update_data.get('trade_execution'):
                validated_updates['trade_execution'] = trade_execution  # JSONはそのまま保存
            
            if archive_status := update_data.get('archive_status'):
                validated_updates['archive_status'] = ArchiveValidator.validate_archive_status(archive_status)
            
            # 更新する項目がない場合
            if not validated_updates:
                logger.warning(f"更新する項目がありません: {archive_id}")
                raise ArchiveServiceError(
                    "更新する項目がありません",
                    "NO_UPDATE_DATA"
                )
            
            # 更新実行
            success = await self.repository.update_archive(archive_id, validated_updates)
            
            if not success:
                logger.warning(f"アーカイブの更新に失敗: {archive_id}")
                raise ArchiveServiceError(
                    "アーカイブの更新に失敗しました",
                    "UPDATE_FAILED"
                )
            
            # 更新後のデータを取得
            updated_archive = await self.repository.get_archive_by_id(archive_id)
            
            logger.info(f"アーカイブパフォーマンス更新サービス完了: {archive_id}", {
                'archive_id': archive_id,
                'updated_fields': list(validated_updates.keys())
            })
            
            tracker.end({'archive_id': archive_id, 'updated_fields': len(validated_updates)})
            return {
                'success': True,
                'archive_id': archive_id,
                'archive': updated_archive,
                'updated_fields': list(validated_updates.keys()),
                'message': 'アーカイブを正常に更新しました'
            }
            
        except ArchiveServiceError:
            raise
        except ArchiveValidationError as e:
            logger.warning(f"アーカイブ更新バリデーションエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ArchiveRepositoryError as e:
            logger.error(f"アーカイブ更新リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"アーカイブ更新中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "アーカイブ更新中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def delete_archive(self, archive_id: str) -> Dict[str, Any]:
        """アーカイブ削除（論理削除）"""
        tracker = PerformanceTracker("delete_archive")
        
        try:
            # ID のバリデーション
            if not archive_id or not isinstance(archive_id, str):
                raise ArchiveServiceError(
                    "アーカイブIDが無効です",
                    "INVALID_ID"
                )
            
            # 削除実行
            success = await self.repository.delete_archive(archive_id.strip())
            
            if not success:
                logger.warning(f"アーカイブの削除に失敗: {archive_id}")
                raise ArchiveServiceError(
                    "アーカイブの削除に失敗しました",
                    "DELETE_FAILED"
                )
            
            logger.info(f"アーカイブ削除サービス完了: {archive_id}")
            tracker.end({'archive_id': archive_id})
            return {
                'success': True,
                'archive_id': archive_id,
                'message': 'アーカイブを正常に削除しました'
            }
            
        except ArchiveServiceError:
            raise
        except ArchiveRepositoryError as e:
            logger.error(f"アーカイブ削除リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"アーカイブ削除中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "アーカイブ削除中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_performance_statistics(self) -> Dict[str, Any]:
        """パフォーマンス統計取得"""
        tracker = PerformanceTracker("get_performance_statistics")
        
        try:
            # 統計取得
            stats = await self.repository.get_performance_stats()
            
            # 追加計算や整形
            if stats['total_archived'] > 0:
                # ロジック別成功率計算
                logic_stats = {}
                for logic_type in ['logic_a', 'logic_b']:
                    # この部分は簡易実装。実際にはより詳細な分析が必要
                    logic_stats[logic_type] = {
                        'count': stats.get(f'{logic_type}_count', 0),
                        'success_rate': 0.0  # 今回は簡易実装
                    }
                
                stats['logic_performance'] = logic_stats
            
            logger.info("アーカイブパフォーマンス統計取得サービス完了", {
                'total_archived': stats['total_archived']
            })
            
            tracker.end({'total_archived': stats['total_archived']})
            return {
                'success': True,
                'statistics': stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except ArchiveRepositoryError as e:
            logger.error(f"パフォーマンス統計取得リポジトリエラー: {e.message}")
            raise ArchiveServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"パフォーマンス統計取得中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "パフォーマンス統計取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def export_to_csv(self, search_params: Dict[str, Any], export_options: Dict[str, Any] = None) -> str:
        """CSV形式でアーカイブデータをエクスポート"""
        tracker = PerformanceTracker("export_to_csv")
        
        try:
            # エクスポートオプションのデフォルト値設定
            export_options = export_options or {}
            date_format = export_options.get('date_format', '%Y-%m-%d %H:%M:%S')
            decimal_places = export_options.get('decimal_places', 2)
            include_fields = export_options.get('include_fields', [])
            
            # 大量データ取得のため、ページング制限を一時的に解除
            search_params_for_export = search_params.copy()
            search_params_for_export['limit'] = 10000  # 最大10,000件まで
            
            # データ取得
            search_result = await self.search_archives(search_params_for_export)
            archives = search_result['archives']
            
            if not archives:
                logger.info("エクスポート対象のアーカイブがありません")
                return ""
            
            # CSV出力用のフィールド定義
            all_fields = [
                'stock_code', 'stock_name', 'logic_type', 'detection_date',
                'price_at_detection', 'volume_at_detection', 'market_cap_at_detection',
                'performance_after_1d', 'performance_after_1w', 'performance_after_1m',
                'max_gain', 'max_loss', 'outcome_classification', 'manual_score',
                'manual_score_reason', 'lessons_learned', 'created_at'
            ]
            
            # 出力フィールドの決定
            if include_fields:
                fields_to_export = [f for f in include_fields if f in all_fields]
            else:
                fields_to_export = all_fields
            
            # フィールドの日本語ヘッダー
            field_headers = {
                'stock_code': '銘柄コード',
                'stock_name': '銘柄名',
                'logic_type': 'ロジック種別',
                'detection_date': '検出日時',
                'price_at_detection': '検出時価格',
                'volume_at_detection': '検出時出来高',
                'market_cap_at_detection': '検出時時価総額',
                'performance_after_1d': '1日後パフォーマンス(%)',
                'performance_after_1w': '1週間後パフォーマンス(%)',
                'performance_after_1m': '1ヶ月後パフォーマンス(%)',
                'max_gain': '最大利益(%)',
                'max_loss': '最大損失(%)',
                'outcome_classification': '結果分類',
                'manual_score': '手動スコア',
                'manual_score_reason': '手動スコア理由',
                'lessons_learned': '学習事項・改善点',
                'created_at': 'アーカイブ作成日時'
            }
            
            # CSV生成
            output = io.StringIO()
            writer = csv.writer(output)
            
            # ヘッダー行
            headers = [field_headers.get(field, field) for field in fields_to_export]
            writer.writerow(headers)
            
            # データ行
            for archive in archives:
                row = []
                for field in fields_to_export:
                    value = archive.get(field)
                    
                    # データ型に応じた変換
                    if value is None:
                        row.append('')
                    elif field in ['detection_date', 'created_at'] and isinstance(value, datetime):
                        row.append(value.strftime(date_format))
                    elif field.endswith('_at') and isinstance(value, str):
                        # 文字列形式の日時
                        try:
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            row.append(dt.strftime(date_format))
                        except:
                            row.append(value)
                    elif isinstance(value, float) and field.startswith('performance') or field in ['max_gain', 'max_loss', 'price_at_detection', 'market_cap_at_detection']:
                        # 数値フィールド
                        row.append(f"{value:.{decimal_places}f}" if value is not None else '')
                    else:
                        row.append(str(value))
                
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(f"CSV エクスポート完了: {len(archives)}件", {
                'exported_count': len(archives),
                'fields_count': len(fields_to_export)
            })
            
            tracker.end({'exported_count': len(archives), 'fields_count': len(fields_to_export)})
            return csv_content
            
        except ArchiveServiceError:
            raise
        except Exception as e:
            logger.error(f"CSV エクスポート中に予期しないエラー: {e}")
            raise ArchiveServiceError(
                "CSV エクスポート中に予期しないエラーが発生しました",
                "EXPORT_ERROR",
                {'error': str(e)}
            )