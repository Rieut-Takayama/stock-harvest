"""
銘柄アーカイブコントローラー
Stock Harvest AI - API エンドポイント制御
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..services.archive_service import ArchiveService, ArchiveServiceError
from ..models.archive_models import (
    ArchiveCreateRequestModel,
    ArchiveUpdateRequestModel,
    ArchiveSearchRequestModel,
    ArchiveSearchResponseModel,
    ArchivePerformanceStatsModel,
    ArchiveCSVExportRequestModel
)
from ..lib.logger import logger
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ArchiveController:
    """銘柄アーカイブコントローラー"""
    
    def __init__(self):
        """コントローラー初期化"""
        self.service = ArchiveService()
        self.router = APIRouter(prefix="/api/archive", tags=["Archive"])
        self._register_routes()
        logger.debug("ArchiveController初期化完了")
    
    def _register_routes(self):
        """ルート登録"""
        
        @self.router.post("/stocks", response_model=Dict[str, Any])
        async def create_archive_entry(request: ArchiveCreateRequestModel):
            """アーカイブエントリ作成"""
            try:
                logger.info("アーカイブエントリ作成リクエスト受信", {
                    'stock_code': request.stock_code,
                    'logic_type': request.logic_type
                })
                
                result = await self.service.create_archive_entry(request.dict())
                
                logger.info("アーカイブエントリ作成レスポンス送信", {
                    'success': result['success'],
                    'archive_id': result.get('archive_id')
                })
                
                return result
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブエントリ作成サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブエントリ作成中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブエントリの作成中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/search", response_model=ArchiveSearchResponseModel)
        async def search_archives(
            stock_code: Optional[str] = Query(None, description="銘柄コード"),
            logic_type: Optional[str] = Query(None, description="ロジック種別"),
            date_from: Optional[datetime] = Query(None, description="検索開始日"),
            date_to: Optional[datetime] = Query(None, description="検索終了日"),
            outcome_classification: Optional[str] = Query(None, description="結果分類"),
            manual_score: Optional[ManualScoreValue] = Query(None, description="手動スコア"),
            page: int = Query(1, ge=1, description="ページ番号"),
            limit: int = Query(20, ge=1, le=100, description="1ページあたりの件数")
        ):
            """アーカイブ検索"""
            try:
                # クエリパラメータを辞書に変換
                search_params = {
                    'stock_code': stock_code,
                    'logic_type': logic_type,
                    'date_from': date_from,
                    'date_to': date_to,
                    'outcome_classification': outcome_classification,
                    'manual_score': manual_score,
                    'page': page,
                    'limit': limit
                }
                
                # None の値を除去
                search_params = {k: v for k, v in search_params.items() if v is not None}
                
                logger.info("アーカイブ検索リクエスト受信", search_params)
                
                result = await self.service.search_archives(search_params)
                
                # レスポンスモデルに適合する形式に変換
                response = ArchiveSearchResponseModel(
                    success=result['success'],
                    archives=result['archives'],
                    total=result['pagination']['total'],
                    page=result['pagination']['page'],
                    limit=result['pagination']['limit'],
                    has_next=result['pagination']['has_next']
                )
                
                logger.info("アーカイブ検索レスポンス送信", {
                    'total_count': response.total,
                    'returned_count': len(response.archives)
                })
                
                return response
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブ検索サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブ検索中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブ検索中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/stocks/{archive_id}", response_model=Dict[str, Any])
        async def get_archive_details(archive_id: str):
            """アーカイブ詳細取得"""
            try:
                logger.info(f"アーカイブ詳細取得リクエスト受信: {archive_id}")
                
                result = await self.service.get_archive_details(archive_id)
                
                logger.debug(f"アーカイブ詳細取得レスポンス送信: {archive_id}")
                
                return result
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブ詳細取得サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブ詳細取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブ詳細取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.put("/stocks/{archive_id}", response_model=Dict[str, Any])
        async def update_archive(archive_id: str, request: ArchiveUpdateRequestModel):
            """アーカイブ更新"""
            try:
                logger.info(f"アーカイブ更新リクエスト受信: {archive_id}")
                
                # None でない項目のみを更新データに含める
                update_data = {k: v for k, v in request.dict().items() if v is not None}
                
                if not update_data:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            'error': '更新するデータが指定されていません',
                            'code': 'NO_UPDATE_DATA'
                        }
                    )
                
                result = await self.service.update_archive_performance(archive_id, update_data)
                
                logger.info(f"アーカイブ更新レスポンス送信: {archive_id}", {
                    'success': result['success'],
                    'updated_fields': result.get('updated_fields', [])
                })
                
                return result
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブ更新サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブ更新中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブ更新中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.delete("/stocks/{archive_id}", response_model=Dict[str, Any])
        async def delete_archive(archive_id: str):
            """アーカイブ削除"""
            try:
                logger.info(f"アーカイブ削除リクエスト受信: {archive_id}")
                
                result = await self.service.delete_archive(archive_id)
                
                logger.info(f"アーカイブ削除レスポンス送信: {archive_id}")
                
                return result
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブ削除サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブ削除中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブ削除中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/stats", response_model=Dict[str, Any])
        async def get_performance_statistics():
            """パフォーマンス統計取得"""
            try:
                logger.info("パフォーマンス統計取得リクエスト受信")
                
                result = await self.service.get_performance_statistics()
                
                logger.info("パフォーマンス統計取得レスポンス送信", {
                    'total_archived': result.get('statistics', {}).get('total_archived', 0)
                })
                
                return result
                
            except ArchiveServiceError as e:
                logger.error(f"パフォーマンス統計取得サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"パフォーマンス統計取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'パフォーマンス統計取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/export/csv", response_class=Response)
        async def export_archives_csv(
            stock_code: Optional[str] = Query(None, description="銘柄コード"),
            logic_type: Optional[str] = Query(None, description="ロジック種別"),
            date_from: Optional[datetime] = Query(None, description="検索開始日"),
            date_to: Optional[datetime] = Query(None, description="検索終了日"),
            outcome_classification: Optional[str] = Query(None, description="結果分類"),
            manual_score: Optional[ManualScoreValue] = Query(None, description="手動スコア"),
            include_fields: Optional[str] = Query(None, description="出力フィールド（カンマ区切り）"),
            date_format: str = Query("%Y-%m-%d %H:%M:%S", description="日付フォーマット"),
            decimal_places: int = Query(2, ge=0, le=10, description="小数点以下桁数")
        ):
            """アーカイブCSV出力"""
            try:
                # 検索パラメータの構築
                search_params = {
                    'stock_code': stock_code,
                    'logic_type': logic_type,
                    'date_from': date_from,
                    'date_to': date_to,
                    'outcome_classification': outcome_classification,
                    'manual_score': manual_score,
                    'page': 1,
                    'limit': 10000  # CSV出力時は大量取得
                }
                
                # None の値を除去
                search_params = {k: v for k, v in search_params.items() if v is not None}
                
                # エクスポートオプション
                export_options = {
                    'date_format': date_format,
                    'decimal_places': decimal_places,
                    'include_fields': include_fields.split(',') if include_fields else []
                }
                
                logger.info("アーカイブCSV出力リクエスト受信", {
                    'search_params': search_params,
                    'export_options': export_options
                })
                
                csv_content = await self.service.export_to_csv(search_params, export_options)
                
                if not csv_content:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            'error': '出力対象のデータがありません',
                            'code': 'NO_DATA'
                        }
                    )
                
                # ファイル名生成
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"archive_export_{timestamp}.csv"
                
                logger.info(f"アーカイブCSV出力完了: {filename}")
                
                return Response(
                    content=csv_content,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}",
                        "Content-Type": "text/csv; charset=utf-8"
                    }
                )
                
            except ArchiveServiceError as e:
                logger.error(f"アーカイブCSV出力サービスエラー: {e.message}")
                status_code = self._get_http_status_code(e.code)
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        'error': e.message,
                        'code': e.code,
                        'details': e.details
                    }
                )
            except Exception as e:
                logger.error(f"アーカイブCSV出力中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'アーカイブCSV出力中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
    
    def _get_http_status_code(self, error_code: str) -> int:
        """エラーコードからHTTPステータスコードを取得"""
        status_code_mapping = {
            'VALIDATION_ERROR': 400,
            'INVALID_ID': 400,
            'NO_UPDATE_DATA': 400,
            'NOT_FOUND': 404,
            'DELETED': 404,
            'UPDATE_FAILED': 409,
            'DELETE_FAILED': 409,
            'REPOSITORY_ERROR': 500,
            'DATABASE_ERROR': 500,
            'EXPORT_ERROR': 500,
            'UNEXPECTED_ERROR': 500
        }
        
        return status_code_mapping.get(error_code, 500)


# コントローラーインスタンス生成
archive_controller = ArchiveController()
router = archive_controller.router