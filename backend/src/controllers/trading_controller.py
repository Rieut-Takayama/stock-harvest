"""
売買支援関連コントローラー
Stock Harvest AI プロジェクト用
"""

from typing import Dict, Any
from fastapi import HTTPException, Query, Body
from decimal import Decimal
from datetime import datetime

from ..services.trading_service import TradingService
from ..models.trading_models import (
    EntryOptimizationRequest,
    EntryOptimizationResponse,
    IfdocoGuideRequest,
    IfdocoGuideResponse,
    TradingHistoryFilter,
    TradingHistoryResponse,
    SignalHistoryFilter,
    SignalHistoryResponse,
    TradingApiResponse,
    TradingApiError
)
from ..validators.trading_validators import (
    EntryOptimizationValidator,
    IfdocoGuideValidator,
    TradingHistoryValidator,
    SignalHistoryValidator
)
from ..lib.logger import logger, PerformanceTracker


class TradingController:
    """売買支援コントローラー"""

    def __init__(self):
        self.trading_service = TradingService()

    async def optimize_entry_point(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        エントリーポイント最適化エンドポイント
        POST /api/trading/entry-optimization
        """
        tracker = PerformanceTracker("エントリーポイント最適化API")
        
        try:
            logger.info("エントリーポイント最適化API呼び出し")
            
            # リクエストデータのバリデーション
            validated_data = EntryOptimizationValidator.validate_request(request_data)
            
            # リクエストオブジェクト作成
            request = EntryOptimizationRequest(**validated_data)
            
            # サービス層呼び出し
            result = await self.trading_service.optimize_entry_point(request)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': result.dict(),
                'message': 'エントリーポイント最適化が完了しました',
                'timestamp': datetime.now()
            }
            
            logger.info(f"エントリーポイント最適化API完了: {request.stock_code}")
            tracker.end({'stock_code': request.stock_code, 'success': True})
            
            return response_data
            
        except ValueError as ve:
            logger.warning(f"エントリーポイント最適化API バリデーションエラー: {ve}")
            tracker.end({'success': False, 'error': 'validation'})
            
            error_response = {
                'success': False,
                'error_code': 'VALIDATION_ERROR',
                'error_message': str(ve),
                'timestamp': datetime.now()
            }
            return error_response
            
        except Exception as e:
            logger.error(f"エントリーポイント最適化API エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': 'エントリーポイント最適化中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    async def generate_ifdoco_guide(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        IFDOCO注文ガイド生成エンドポイント
        POST /api/trading/ifdoco-guide
        """
        tracker = PerformanceTracker("IFDOCO注文ガイドAPI")
        
        try:
            logger.info("IFDOCO注文ガイドAPI呼び出し")
            
            # リクエストデータのバリデーション
            validated_data = IfdocoGuideValidator.validate_request(request_data)
            
            # リクエストオブジェクト作成
            request = IfdocoGuideRequest(**validated_data)
            
            # サービス層呼び出し
            result = await self.trading_service.generate_ifdoco_guide(request)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': result.dict(),
                'message': 'IFDOCO注文ガイドが生成されました',
                'timestamp': datetime.now()
            }
            
            logger.info(f"IFDOCO注文ガイドAPI完了: {request.stock_code}")
            tracker.end({'stock_code': request.stock_code, 'success': True})
            
            return response_data
            
        except ValueError as ve:
            logger.warning(f"IFDOCO注文ガイドAPI バリデーションエラー: {ve}")
            tracker.end({'success': False, 'error': 'validation'})
            
            error_response = {
                'success': False,
                'error_code': 'VALIDATION_ERROR',
                'error_message': str(ve),
                'timestamp': datetime.now()
            }
            return error_response
            
        except Exception as e:
            logger.error(f"IFDOCO注文ガイドAPI エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': 'IFDOCO注文ガイド生成中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    async def get_trading_history(self, 
                                stock_code: str = Query(None, description="銘柄コード"), 
                                logic_type: str = Query(None, description="ロジック種別"),
                                trade_type: str = Query(None, description="取引種別"),
                                status: str = Query(None, description="ステータス"),
                                date_from: str = Query(None, description="開始日"),
                                date_to: str = Query(None, description="終了日"),
                                min_profit_loss: float = Query(None, description="最小損益"),
                                max_profit_loss: float = Query(None, description="最大損益"),
                                page: int = Query(1, description="ページ番号", ge=1),
                                limit: int = Query(20, description="取得件数", ge=1, le=100)
                                ) -> Dict[str, Any]:
        """
        売買履歴取得エンドポイント
        GET /api/history/trades
        """
        tracker = PerformanceTracker("売買履歴取得API")
        
        try:
            logger.info("売買履歴取得API呼び出し")
            
            # クエリパラメータをフィルタ辞書に変換
            filter_data = {
                'stock_code': stock_code,
                'logic_type': logic_type,
                'trade_type': trade_type,
                'status': status,
                'date_from': date_from,
                'date_to': date_to,
                'min_profit_loss': min_profit_loss,
                'max_profit_loss': max_profit_loss,
                'page': page,
                'limit': limit
            }
            
            # バリデーション
            validated_filter = TradingHistoryValidator.validate_filter(filter_data)
            
            # フィルタオブジェクト作成
            filters = TradingHistoryFilter(**validated_filter)
            
            # サービス層呼び出し
            result = await self.trading_service.get_trading_history(filters)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': result.dict(),
                'message': f'{result.total}件の売買履歴を取得しました',
                'timestamp': datetime.now()
            }
            
            logger.info(f"売買履歴取得API完了: {result.total}件")
            tracker.end({'total_count': result.total, 'success': True})
            
            return response_data
            
        except ValueError as ve:
            logger.warning(f"売買履歴取得API バリデーションエラー: {ve}")
            tracker.end({'success': False, 'error': 'validation'})
            
            error_response = {
                'success': False,
                'error_code': 'VALIDATION_ERROR',
                'error_message': str(ve),
                'timestamp': datetime.now()
            }
            return error_response
            
        except Exception as e:
            logger.error(f"売買履歴取得API エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': '売買履歴取得中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    async def get_signal_history(self,
                               stock_code: str = Query(None, description="銘柄コード"),
                               signal_type: str = Query(None, description="シグナル種別"),
                               status: str = Query(None, description="ステータス"),
                               confidence_min: float = Query(None, description="最小信頼度", ge=0, le=1),
                               date_from: str = Query(None, description="開始日"),
                               date_to: str = Query(None, description="終了日"),
                               page: int = Query(1, description="ページ番号", ge=1),
                               limit: int = Query(20, description="取得件数", ge=1, le=100)
                               ) -> Dict[str, Any]:
        """
        シグナル履歴取得エンドポイント
        GET /api/history/signals
        """
        tracker = PerformanceTracker("シグナル履歴取得API")
        
        try:
            logger.info("シグナル履歴取得API呼び出し")
            
            # クエリパラメータをフィルタ辞書に変換
            filter_data = {
                'stock_code': stock_code,
                'signal_type': signal_type,
                'status': status,
                'confidence_min': confidence_min,
                'date_from': date_from,
                'date_to': date_to,
                'page': page,
                'limit': limit
            }
            
            # バリデーション
            validated_filter = SignalHistoryValidator.validate_filter(filter_data)
            
            # フィルタオブジェクト作成
            filters = SignalHistoryFilter(**validated_filter)
            
            # サービス層呼び出し
            result = await self.trading_service.get_signal_history(filters)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': result.dict(),
                'message': f'{result.total}件のシグナル履歴を取得しました',
                'timestamp': datetime.now()
            }
            
            logger.info(f"シグナル履歴取得API完了: {result.total}件")
            tracker.end({'total_count': result.total, 'success': True})
            
            return response_data
            
        except ValueError as ve:
            logger.warning(f"シグナル履歴取得API バリデーションエラー: {ve}")
            tracker.end({'success': False, 'error': 'validation'})
            
            error_response = {
                'success': False,
                'error_code': 'VALIDATION_ERROR',
                'error_message': str(ve),
                'timestamp': datetime.now()
            }
            return error_response
            
        except Exception as e:
            logger.error(f"シグナル履歴取得API エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': 'シグナル履歴取得中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    async def create_trading_record(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        売買記録作成エンドポイント（内部使用）
        POST /api/trading/record
        """
        tracker = PerformanceTracker("売買記録作成API")
        
        try:
            logger.info("売買記録作成API呼び出し")
            
            # 基本的なバリデーション
            if not request_data.get('stock_code'):
                raise ValueError("銘柄コードが必要です")
            
            if not request_data.get('trade_type'):
                raise ValueError("取引種別が必要です")
            
            # TradingRepositoryを直接呼び出し
            trade_id = await self.trading_service.trading_repo.create_trading_record(request_data)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': {'trade_id': trade_id},
                'message': '売買記録が作成されました',
                'timestamp': datetime.now()
            }
            
            logger.info(f"売買記録作成API完了: {trade_id}")
            tracker.end({'trade_id': trade_id, 'success': True})
            
            return response_data
            
        except ValueError as ve:
            logger.warning(f"売買記録作成API バリデーションエラー: {ve}")
            tracker.end({'success': False, 'error': 'validation'})
            
            error_response = {
                'success': False,
                'error_code': 'VALIDATION_ERROR',
                'error_message': str(ve),
                'timestamp': datetime.now()
            }
            return error_response
            
        except Exception as e:
            logger.error(f"売買記録作成API エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': '売買記録作成中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    async def get_trading_performance_summary(self,
                                            analysis_period: str = Query('3m', description="分析期間"),
                                            logic_type: str = Query(None, description="ロジック種別"),
                                            benchmark: str = Query('nikkei225', description="ベンチマーク")
                                            ) -> Dict[str, Any]:
        """
        パフォーマンスサマリー取得エンドポイント
        GET /api/trading/performance
        """
        tracker = PerformanceTracker("パフォーマンスサマリー取得API")
        
        try:
            logger.info("パフォーマンスサマリー取得API呼び出し")
            
            # 基本的な統計情報を取得
            filter_data = {
                'logic_type': logic_type,
                'date_from': self._get_analysis_start_date(analysis_period),
                'date_to': datetime.now(),
                'page': 1,
                'limit': 1  # サマリーのみ必要
            }
            
            validated_filter = TradingHistoryValidator.validate_filter(filter_data)
            summary_stats = await self.trading_service.trading_repo.get_trading_summary_stats(validated_filter)
            
            # レスポンス形成
            response_data = {
                'success': True,
                'data': {
                    'analysis_period': analysis_period,
                    'summary': summary_stats,
                    'benchmark': benchmark,
                    'generated_at': datetime.now()
                },
                'message': 'パフォーマンスサマリーを取得しました',
                'timestamp': datetime.now()
            }
            
            logger.info("パフォーマンスサマリー取得API完了")
            tracker.end({'success': True})
            
            return response_data
            
        except Exception as e:
            logger.error(f"パフォーマンスサマリー取得API エラー: {e}", exc_info=True)
            tracker.end({'success': False, 'error': 'internal'})
            
            error_response = {
                'success': False,
                'error_code': 'INTERNAL_SERVER_ERROR',
                'error_message': 'パフォーマンスサマリー取得中にエラーが発生しました',
                'error_details': {'original_error': str(e)},
                'timestamp': datetime.now()
            }
            return error_response

    # ヘルパーメソッド

    def _get_analysis_start_date(self, period: str) -> datetime:
        """分析期間の開始日を計算"""
        now = datetime.now()
        
        period_mapping = {
            '1w': 7,
            '1m': 30,
            '3m': 90,
            '6m': 180,
            '1y': 365
        }
        
        days = period_mapping.get(period, 90)  # デフォルト3ヶ月
        return now.replace(day=1) if period == '1m' else (now - timedelta(days=days))

    def _format_error_response(self, error_code: str, error_message: str, 
                             details: Dict[str, Any] = None) -> Dict[str, Any]:
        """エラーレスポンス形成"""
        return {
            'success': False,
            'error_code': error_code,
            'error_message': error_message,
            'error_details': details or {},
            'timestamp': datetime.now()
        }

    def _format_success_response(self, data: Any, message: str = None) -> Dict[str, Any]:
        """成功レスポンス形成"""
        return {
            'success': True,
            'data': data,
            'message': message or 'リクエストが正常に処理されました',
            'timestamp': datetime.now()
        }