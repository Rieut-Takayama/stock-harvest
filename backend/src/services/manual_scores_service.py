"""
手動スコア評価サービス
Stock Harvest AI - ビジネスロジック層
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from ..repositories.manual_scores_repository import ManualScoresRepository, ManualScoresRepositoryError
from ..validators.manual_scores_validators import ManualScoresValidator, ScoreValidationError
from ..lib.logger import logger, PerformanceTracker
# Python型定義
from typing import Literal
ManualScoreValue = Literal['S', 'A+', 'A', 'B', 'C']


class ManualScoresServiceError(Exception):
    """手動スコア評価サービスエラー"""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code or "SERVICE_ERROR"
        self.details = details or {}
        super().__init__(message)


class ManualScoresService:
    """手動スコア評価サービス"""
    
    def __init__(self):
        """サービス初期化"""
        self.repository = ManualScoresRepository()
        logger.debug("ManualScoresService初期化完了")
    
    async def create_score_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """スコア評価作成"""
        tracker = PerformanceTracker("create_score_evaluation")
        
        try:
            # バリデーション
            validated_data = ManualScoresValidator.validate_evaluation_request(evaluation_data)
            
            # 既存の評価があるかチェック
            existing_score = await self.repository.get_score_by_stock(
                validated_data['stock_code'],
                validated_data['logic_type']
            )
            
            # 既存評価がある場合は警告
            if existing_score and existing_score.get('status') == 'active':
                logger.warning(f"既存のアクティブなスコア評価があります: {validated_data['stock_code']}")
                # 既存評価を superseded に変更
                await self.repository.update_score_evaluation(existing_score['id'], {
                    'status': 'superseded',
                    'change_reason': '新しいスコア評価により置換',
                    'changed_by': validated_data.get('evaluated_by', 'user')
                })
            
            # 評価者情報の設定
            validated_data['evaluated_by'] = validated_data.get('evaluated_by', 'user')
            
            # 市場コンテキストの自動生成（簡易版）
            if not validated_data.get('market_context'):
                validated_data['market_context'] = {
                    'evaluation_timestamp': datetime.now().isoformat(),
                    'market_session': self._get_market_session(),
                    'evaluation_source': 'manual_input'
                }
            
            # スコア評価作成
            score_id = await self.repository.create_score_evaluation(validated_data)
            
            # 作成されたスコア評価を取得して返す
            created_score = await self.repository.get_score_by_id(score_id)
            
            logger.info(f"スコア評価作成サービス完了: {score_id}", {
                'score_id': score_id,
                'stock_code': validated_data['stock_code'],
                'score': validated_data['score'],
                'logic_type': validated_data['logic_type']
            })
            
            tracker.end({'score_id': score_id})
            return {
                'success': True,
                'score_id': score_id,
                'evaluation': created_score,
                'message': 'スコア評価を正常に作成しました'
            }
            
        except ScoreValidationError as e:
            logger.warning(f"スコア評価作成バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価作成リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価作成中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価の作成中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_score_evaluation(self, stock_code: str, logic_type: Optional[str] = None) -> Dict[str, Any]:
        """銘柄のスコア評価取得"""
        tracker = PerformanceTracker("get_score_evaluation")
        
        try:
            # 銘柄コードのバリデーション
            validated_stock_code = ManualScoresValidator.validate_stock_code(stock_code)
            
            # ロジックタイプのバリデーション
            if logic_type:
                validated_logic_type = ManualScoresValidator.validate_logic_type(logic_type)
            else:
                validated_logic_type = None
            
            # スコア評価取得
            evaluation = await self.repository.get_score_by_stock(validated_stock_code, validated_logic_type)
            
            if not evaluation:
                logger.debug(f"スコア評価が見つかりません: {validated_stock_code}")
                return {
                    'success': True,
                    'evaluation': None,
                    'ai_calculating': self._is_ai_calculating(validated_stock_code),
                    'message': 'スコア評価が見つかりません'
                }
            
            # AI計算状態の確認
            ai_calculating = self._is_ai_calculating(validated_stock_code)
            
            logger.debug(f"スコア評価取得サービス完了: {validated_stock_code}")
            tracker.end({'stock_code': validated_stock_code})
            return {
                'success': True,
                'evaluation': evaluation,
                'ai_calculating': ai_calculating
            }
            
        except ScoreValidationError as e:
            logger.warning(f"スコア評価取得バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価取得リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価取得中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def update_score_evaluation(self, score_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """スコア評価更新"""
        tracker = PerformanceTracker("update_score_evaluation")
        
        try:
            # ID のバリデーション
            if not score_id or not isinstance(score_id, str):
                raise ManualScoresServiceError(
                    "スコアIDが無効です",
                    "INVALID_ID"
                )
            
            # 更新データのバリデーション
            validated_updates = ManualScoresValidator.validate_update_request(update_data)
            
            # 更新者情報の設定
            validated_updates['changed_by'] = update_data.get('changed_by', 'user')
            
            # 更新実行
            success = await self.repository.update_score_evaluation(score_id, validated_updates)
            
            if not success:
                logger.warning(f"スコア評価の更新に失敗: {score_id}")
                raise ManualScoresServiceError(
                    "スコア評価の更新に失敗しました",
                    "UPDATE_FAILED"
                )
            
            # 更新後のデータを取得
            updated_evaluation = await self.repository.get_score_by_id(score_id)
            
            logger.info(f"スコア評価更新サービス完了: {score_id}", {
                'score_id': score_id,
                'updated_fields': [k for k in validated_updates.keys() if k != 'changed_by'],
                'change_reason': validated_updates.get('change_reason', '')
            })
            
            tracker.end({'score_id': score_id, 'updated_fields': len(validated_updates)})
            return {
                'success': True,
                'score_id': score_id,
                'evaluation': updated_evaluation,
                'updated_fields': [k for k in validated_updates.keys() if k not in ['changed_by', 'change_reason']],
                'message': 'スコア評価を正常に更新しました'
            }
            
        except ManualScoresServiceError:
            raise
        except ScoreValidationError as e:
            logger.warning(f"スコア評価更新バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価更新リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価更新中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価更新中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def search_score_evaluations(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """スコア評価検索"""
        tracker = PerformanceTracker("search_score_evaluations")
        
        try:
            # バリデーション
            validated_params = ManualScoresValidator.validate_search_request(search_params)
            
            # 検索実行
            evaluations, total_count = await self.repository.search_score_evaluations(validated_params)
            
            # ページネーション情報計算
            page = validated_params.get('page', 1)
            limit = validated_params.get('limit', 20)
            has_next = (page * limit) < total_count
            
            logger.info(f"スコア評価検索サービス完了: {len(evaluations)}件取得", {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'returned_count': len(evaluations)
            })
            
            tracker.end({'total_count': total_count, 'returned_count': len(evaluations)})
            return {
                'success': True,
                'evaluations': evaluations,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'limit': limit,
                    'has_next': has_next,
                    'total_pages': (total_count + limit - 1) // limit
                },
                'search_params': validated_params
            }
            
        except ScoreValidationError as e:
            logger.warning(f"スコア評価検索バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価検索リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価検索中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価検索中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_score_history(self, stock_code: str, compact: bool = True) -> Dict[str, Any]:
        """銘柄のスコア評価履歴取得"""
        tracker = PerformanceTracker("get_score_history")
        
        try:
            # 銘柄コードのバリデーション
            validated_stock_code = ManualScoresValidator.validate_stock_code(stock_code)
            
            # 履歴取得
            history_limit = 5 if compact else 20
            history = await self.repository.get_score_history(validated_stock_code, history_limit)
            
            # コンパクト形式の場合は要約情報を生成
            if compact and history:
                summary = {
                    'latest_score': history[0]['score'] if history else None,
                    'evaluation_count': len(history),
                    'last_evaluated_at': history[0]['evaluated_at'] if history else None,
                    'scores_distribution': self._calculate_score_distribution(history)
                }
            else:
                summary = None
            
            logger.debug(f"スコア評価履歴取得サービス完了: {validated_stock_code}, {len(history)}件")
            tracker.end({'stock_code': validated_stock_code, 'count': len(history)})
            return {
                'success': True,
                'stock_code': validated_stock_code,
                'history': history,
                'summary': summary,
                'compact': compact
            }
            
        except ScoreValidationError as e:
            logger.warning(f"スコア評価履歴取得バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価履歴取得リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価履歴取得中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価履歴取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_ai_calculation_status(self, stock_code: str) -> Dict[str, Any]:
        """AI スコア計算状態取得"""
        tracker = PerformanceTracker("get_ai_calculation_status")
        
        try:
            # 銘柄コードのバリデーション
            validated_stock_code = ManualScoresValidator.validate_stock_code(stock_code)
            
            # AI計算状態の確認（今回はモック実装）
            is_calculating = self._is_ai_calculating(validated_stock_code)
            
            if is_calculating:
                # 計算中の場合の詳細情報
                status = {
                    'is_calculating': True,
                    'stock_code': validated_stock_code,
                    'started_at': (datetime.now() - timedelta(minutes=2)).isoformat(),
                    'estimated_completion': (datetime.now() + timedelta(minutes=1)).isoformat(),
                    'progress_percentage': 75,
                    'current_step': 'テクニカル指標分析中'
                }
            else:
                status = {
                    'is_calculating': False,
                    'stock_code': validated_stock_code,
                    'last_calculation_at': None
                }
            
            logger.debug(f"AI スコア計算状態取得完了: {validated_stock_code}")
            tracker.end({'stock_code': validated_stock_code, 'is_calculating': is_calculating})
            return {
                'success': True,
                'status': status
            }
            
        except ScoreValidationError as e:
            logger.warning(f"AI スコア計算状態取得バリデーションエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "VALIDATION_ERROR",
                {'field': e.field, 'validation_code': e.code}
            )
        except Exception as e:
            logger.error(f"AI スコア計算状態取得中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "AI スコア計算状態取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    async def get_evaluation_statistics(self) -> Dict[str, Any]:
        """スコア評価統計取得"""
        tracker = PerformanceTracker("get_evaluation_statistics")
        
        try:
            # 統計取得
            stats = await self.repository.get_evaluation_stats()
            
            # 追加分析情報の計算
            if stats['total_evaluations'] > 0:
                # スコア品質指標の計算
                high_confidence_count = stats['confidence_distribution'].get('high', 0)
                confidence_ratio = (high_confidence_count / stats['total_evaluations']) * 100
                
                # フォローアップ率
                follow_up_ratio = (stats['follow_up_pending_count'] / stats['total_evaluations']) * 100
                
                # 学習事例率
                learning_ratio = (stats['learning_cases_count'] / stats['total_evaluations']) * 100
                
                stats['quality_metrics'] = {
                    'high_confidence_ratio': round(confidence_ratio, 2),
                    'follow_up_ratio': round(follow_up_ratio, 2),
                    'learning_cases_ratio': round(learning_ratio, 2)
                }
            else:
                stats['quality_metrics'] = {
                    'high_confidence_ratio': 0.0,
                    'follow_up_ratio': 0.0,
                    'learning_cases_ratio': 0.0
                }
            
            logger.info("スコア評価統計取得サービス完了", {
                'total_evaluations': stats['total_evaluations']
            })
            
            tracker.end({'total_evaluations': stats['total_evaluations']})
            return {
                'success': True,
                'statistics': stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except ManualScoresRepositoryError as e:
            logger.error(f"スコア評価統計取得リポジトリエラー: {e.message}")
            raise ManualScoresServiceError(
                e.message,
                "REPOSITORY_ERROR",
                e.details
            )
        except Exception as e:
            logger.error(f"スコア評価統計取得中に予期しないエラー: {e}")
            raise ManualScoresServiceError(
                "スコア評価統計取得中に予期しないエラーが発生しました",
                "UNEXPECTED_ERROR",
                {'error': str(e)}
            )
    
    def _is_ai_calculating(self, stock_code: str) -> bool:
        """AI 計算状態の確認（モック実装）"""
        # 今回は簡易実装として、特定の銘柄コードで計算中を模擬
        # 実際には外部システムやキャッシュから状態を取得する
        calculating_stocks = ['7203', '9984']  # テスト用
        return stock_code in calculating_stocks
    
    def _get_market_session(self) -> str:
        """現在の市場セッションを取得"""
        now = datetime.now()
        hour = now.hour
        
        if 9 <= hour < 11:
            return 'morning_session'
        elif 11 <= hour < 12:
            return 'lunch_break'
        elif 12 <= hour < 15:
            return 'afternoon_session'
        else:
            return 'after_hours'
    
    def _calculate_score_distribution(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """スコア分布の計算"""
        distribution = {'S': 0, 'A+': 0, 'A': 0, 'B': 0, 'C': 0}
        
        for item in history:
            score = item.get('score')
            if score in distribution:
                distribution[score] += 1
        
        return distribution