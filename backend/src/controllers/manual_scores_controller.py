"""
手動スコア評価コントローラー
Stock Harvest AI - API エンドポイント制御
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..services.manual_scores_service import ManualScoresService, ManualScoresServiceError
from ..models.manual_scores_models import (
    ScoreEvaluationRequestModel,
    ScoreUpdateRequestModel,
    ScoreSearchRequestModel,
    ScoreSearchResponseModel,
    ScoreStatsModel,
    AIScoreCalculationStatusModel
)
from ..lib.logger import logger
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ManualScoresController:
    """手動スコア評価コントローラー"""
    
    def __init__(self):
        """コントローラー初期化"""
        self.service = ManualScoresService()
        self.router = APIRouter(prefix="/api/scores", tags=["Manual Scores"])
        self._register_routes()
        logger.debug("ManualScoresController初期化完了")
    
    def _register_routes(self):
        """ルート登録"""
        
        @self.router.post("/manual", response_model=Dict[str, Any])
        async def create_score_evaluation(request: ScoreEvaluationRequestModel):
            """スコア評価作成"""
            try:
                logger.info("スコア評価作成リクエスト受信", {
                    'stock_code': request.stock_code,
                    'score': request.score,
                    'logic_type': request.logic_type
                })
                
                result = await self.service.create_score_evaluation(request.dict())
                
                logger.info("スコア評価作成レスポンス送信", {
                    'success': result['success'],
                    'score_id': result.get('score_id')
                })
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価作成サービスエラー: {e.message}")
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
                logger.error(f"スコア評価作成中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価の作成中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/manual/{stock_code}", response_model=Dict[str, Any])
        async def get_score_evaluation(
            stock_code: str = Path(..., description="銘柄コード"),
            logic_type: Optional[str] = Query(None, description="ロジック種別")
        ):
            """銘柄のスコア評価取得"""
            try:
                logger.info(f"スコア評価取得リクエスト受信: {stock_code}")
                
                result = await self.service.get_score_evaluation(stock_code, logic_type)
                
                logger.debug(f"スコア評価取得レスポンス送信: {stock_code}")
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価取得サービスエラー: {e.message}")
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
                logger.error(f"スコア評価取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.put("/manual/{score_id}", response_model=Dict[str, Any])
        async def update_score_evaluation(
            score_id: str = Path(..., description="スコアID"),
            request: ScoreUpdateRequestModel = None
        ):
            """スコア評価更新"""
            try:
                logger.info(f"スコア評価更新リクエスト受信: {score_id}")
                
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
                
                # change_reason は必須なので特別チェック
                if 'change_reason' not in update_data:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            'error': '変更理由は必須です',
                            'code': 'CHANGE_REASON_REQUIRED'
                        }
                    )
                
                result = await self.service.update_score_evaluation(score_id, update_data)
                
                logger.info(f"スコア評価更新レスポンス送信: {score_id}", {
                    'success': result['success'],
                    'updated_fields': result.get('updated_fields', [])
                })
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価更新サービスエラー: {e.message}")
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
                logger.error(f"スコア評価更新中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価更新中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/search", response_model=ScoreSearchResponseModel)
        async def search_score_evaluations(
            stock_code: Optional[str] = Query(None, description="銘柄コード"),
            logic_type: Optional[str] = Query(None, description="ロジック種別"),
            score: Optional[ManualScoreValue] = Query(None, description="手動スコア"),
            confidence_level: Optional[str] = Query(None, description="確信度"),
            date_from: Optional[datetime] = Query(None, description="評価日開始"),
            date_to: Optional[datetime] = Query(None, description="評価日終了"),
            is_learning_case: Optional[bool] = Query(None, description="学習事例フラグ"),
            follow_up_required: Optional[bool] = Query(None, description="フォローアップ要否"),
            status: Optional[str] = Query(None, description="ステータス"),
            page: int = Query(1, ge=1, description="ページ番号"),
            limit: int = Query(20, ge=1, le=100, description="1ページあたりの件数")
        ):
            """スコア評価検索"""
            try:
                # クエリパラメータを辞書に変換
                search_params = {
                    'stock_code': stock_code,
                    'logic_type': logic_type,
                    'score': score,
                    'confidence_level': confidence_level,
                    'date_from': date_from,
                    'date_to': date_to,
                    'is_learning_case': is_learning_case,
                    'follow_up_required': follow_up_required,
                    'status': status,
                    'page': page,
                    'limit': limit
                }
                
                # None の値を除去
                search_params = {k: v for k, v in search_params.items() if v is not None}
                
                logger.info("スコア評価検索リクエスト受信", search_params)
                
                result = await self.service.search_score_evaluations(search_params)
                
                # レスポンスモデルに適合する形式に変換
                response = ScoreSearchResponseModel(
                    success=result['success'],
                    scores=result['evaluations'],
                    total=result['pagination']['total'],
                    page=result['pagination']['page'],
                    limit=result['pagination']['limit'],
                    has_next=result['pagination']['has_next']
                )
                
                logger.info("スコア評価検索レスポンス送信", {
                    'total_count': response.total,
                    'returned_count': len(response.scores)
                })
                
                return response
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価検索サービスエラー: {e.message}")
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
                logger.error(f"スコア評価検索中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価検索中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/history/{stock_code}", response_model=Dict[str, Any])
        async def get_score_history(
            stock_code: str = Path(..., description="銘柄コード"),
            compact: bool = Query(True, description="コンパクト形式")
        ):
            """銘柄のスコア評価履歴取得"""
            try:
                logger.info(f"スコア評価履歴取得リクエスト受信: {stock_code}")
                
                result = await self.service.get_score_history(stock_code, compact)
                
                logger.debug(f"スコア評価履歴取得レスポンス送信: {stock_code}, {len(result['history'])}件")
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価履歴取得サービスエラー: {e.message}")
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
                logger.error(f"スコア評価履歴取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価履歴取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/ai-status/{stock_code}", response_model=Dict[str, Any])
        async def get_ai_calculation_status(
            stock_code: str = Path(..., description="銘柄コード")
        ):
            """AI スコア計算状態取得"""
            try:
                logger.debug(f"AI スコア計算状態取得リクエスト受信: {stock_code}")
                
                result = await self.service.get_ai_calculation_status(stock_code)
                
                logger.debug(f"AI スコア計算状態取得レスポンス送信: {stock_code}")
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"AI スコア計算状態取得サービスエラー: {e.message}")
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
                logger.error(f"AI スコア計算状態取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'AI スコア計算状態取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        @self.router.get("/stats", response_model=Dict[str, Any])
        async def get_evaluation_statistics():
            """スコア評価統計取得"""
            try:
                logger.info("スコア評価統計取得リクエスト受信")
                
                result = await self.service.get_evaluation_statistics()
                
                logger.info("スコア評価統計取得レスポンス送信", {
                    'total_evaluations': result.get('statistics', {}).get('total_evaluations', 0)
                })
                
                return result
                
            except ManualScoresServiceError as e:
                logger.error(f"スコア評価統計取得サービスエラー: {e.message}")
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
                logger.error(f"スコア評価統計取得中に予期しないエラー: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        'error': 'スコア評価統計取得中に内部エラーが発生しました',
                        'code': 'INTERNAL_ERROR'
                    }
                )
        
        # 旧 API パスとの互換性維持のためのルート
        @self.router.post("/evaluate", response_model=Dict[str, Any])
        async def create_score_evaluation_legacy(request: ScoreEvaluationRequestModel):
            """スコア評価作成（旧APIパス互換性維持）"""
            return await create_score_evaluation(request)
        
        @self.router.get("/{stock_code}", response_model=Dict[str, Any])
        async def get_score_evaluation_legacy(
            stock_code: str = Path(..., description="銘柄コード"),
            logic_type: Optional[str] = Query(None, description="ロジック種別")
        ):
            """銘柄のスコア評価取得（旧APIパス互換性維持）"""
            return await get_score_evaluation(stock_code, logic_type)
        
        @self.router.put("/{score_id}/update", response_model=Dict[str, Any])
        async def update_score_evaluation_legacy(
            score_id: str = Path(..., description="スコアID"),
            request: ScoreUpdateRequestModel = None
        ):
            """スコア評価更新（旧APIパス互換性維持）"""
            return await update_score_evaluation(score_id, request)
        
        @self.router.get("/{stock_code}/history", response_model=Dict[str, Any])
        async def get_score_history_legacy(
            stock_code: str = Path(..., description="銘柄コード"),
            compact: bool = Query(True, description="コンパクト形式")
        ):
            """銘柄のスコア評価履歴取得（旧APIパス互換性維持）"""
            return await get_score_history(stock_code, compact)
        
        @self.router.get("/{stock_code}/history/compact", response_model=Dict[str, Any])
        async def get_score_history_compact_legacy(
            stock_code: str = Path(..., description="銘柄コード")
        ):
            """銘柄のスコア評価履歴取得コンパクト版（旧APIパス互換性維持）"""
            return await get_score_history(stock_code, compact=True)
        
        @self.router.get("/{stock_code}/ai-status", response_model=Dict[str, Any])
        async def get_ai_calculation_status_legacy(
            stock_code: str = Path(..., description="銘柄コード")
        ):
            """AI スコア計算状態取得（旧APIパス互換性維持）"""
            return await get_ai_calculation_status(stock_code)
    
    def _get_http_status_code(self, error_code: str) -> int:
        """エラーコードからHTTPステータスコードを取得"""
        status_code_mapping = {
            'VALIDATION_ERROR': 400,
            'INVALID_ID': 400,
            'NO_UPDATE_DATA': 400,
            'CHANGE_REASON_REQUIRED': 400,
            'NOT_FOUND': 404,
            'UPDATE_FAILED': 409,
            'REPOSITORY_ERROR': 500,
            'DATABASE_ERROR': 500,
            'UNEXPECTED_ERROR': 500
        }
        
        return status_code_mapping.get(error_code, 500)


# コントローラーインスタンス生成
manual_scores_controller = ManualScoresController()
router = manual_scores_controller.router