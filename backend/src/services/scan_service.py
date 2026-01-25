"""
スキャンサービス（統合・オーケストレーション）
各専門サービスを組み合わせてスキャン機能を提供
公開API、エラーハンドリング、結果統合を担当
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..repositories.scan_repository import ScanRepository
from .stock_data_service_enhanced import StockDataServiceEnhanced
from .technical_analysis_service import TechnicalAnalysisService
from .logic_detection_service import LogicDetectionService
from .logic_a_strict_service import LogicAStrictService
from ..lib.logger import logger


class ScanService:
    """統合スキャンサービス"""
    
    def __init__(self, scan_repository: ScanRepository):
        self.scan_repository = scan_repository

        # 専門サービスの依存性注入
        self.stock_data_service = StockDataServiceEnhanced()
        self.technical_analysis_service = TechnicalAnalysisService()
        self.logic_detection_service = LogicDetectionService()
        self.logic_a_strict_service = LogicAStrictService()
    
    async def start_scan(self) -> Dict:
        """
        全銘柄スキャンを開始する
        """
        try:
            # スキャンIDを生成（マイクロ秒とUUID一部を追加して一意性を保証）
            now = datetime.now()
            unique_suffix = str(uuid.uuid4())[:8]
            scan_id = f"scan_{now.strftime('%Y%m%d_%H%M%S')}_{unique_suffix}"
            
            # スキャン実行記録をデータベースに保存
            scan_execution = {
                'id': scan_id,
                'status': 'running',
                'progress': 0,
                'total_stocks': 0,
                'processed_stocks': 0,
                'current_stock': None,
                'estimated_time': None,
                'message': 'スキャンを開始しています...',
                'logic_a_count': 0,
                'logic_a_enhanced_count': 0,
                'logic_b_count': 0,
                'logic_b_enhanced_count': 0,
                'error_message': None
            }
            
            await self.scan_repository.create_scan_execution(scan_execution)
            
            # 非同期でスキャンを実行
            asyncio.create_task(self._execute_scan(scan_id))
            
            return {
                'scanId': scan_id,
                'message': '全銘柄スキャンを開始しました'
            }
            
        except Exception as e:
            logger.error(f"スキャン開始エラー: {str(e)}")
            raise Exception(f"スキャン開始に失敗しました: {str(e)}")
    
    async def get_scan_status(self) -> Dict:
        """
        現在のスキャン状況を取得する（API仕様書準拠）

        戻り値:
            isRunning: スキャン実行中フラグ
            progress: 進捗率（0-100）
            totalStocks: 対象銘柄総数
            processedStocks: 処理済み銘柄数
            currentStock: 現在処理中の銘柄コード
            estimatedTime: 推定残り時間（秒）
            message: ステータスメッセージ
        """
        try:
            logger.debug("スキャン状態取得開始")

            # 最新のスキャン実行を取得
            latest_scan = await self.scan_repository.get_latest_scan_execution()

            # スキャン実行履歴が存在しない場合（アイドル状態）
            if not latest_scan:
                logger.info("スキャン履歴なし - アイドル状態")
                return {
                    'isRunning': False,
                    'progress': 0,
                    'totalStocks': 0,
                    'processedStocks': 0,
                    'currentStock': None,
                    'estimatedTime': None,
                    'message': 'スキャンが実行されていません'
                }

            # 進行中のスキャンがある場合のステータス変換
            scan_status = latest_scan.get('status', 'unknown')
            is_running = scan_status == 'running'

            # API仕様書準拠のレスポンス形式
            response = {
                'isRunning': is_running,
                'progress': latest_scan.get('progress', 0),
                'totalStocks': latest_scan.get('total_stocks', 0),
                'processedStocks': latest_scan.get('processed_stocks', 0),
                'currentStock': latest_scan.get('current_stock'),
                'estimatedTime': latest_scan.get('estimated_time'),
                'message': latest_scan.get('message', 'ステータス不明')
            }

            # ステータスに応じたログ出力
            if is_running:
                logger.info(f"スキャン実行中: 進捗 {response['progress']}%, {response['processedStocks']}/{response['totalStocks']} 銘柄処理済み")
            elif scan_status == 'completed':
                logger.info(f"スキャン完了: {response['processedStocks']} 銘柄処理済み")
            elif scan_status == 'failed':
                logger.warning(f"スキャン失敗: エラーメッセージ={latest_scan.get('error_message', '不明')}")
            else:
                logger.info(f"スキャン状態: {scan_status}")

            return response

        except Exception as e:
            logger.error(f"スキャン状況取得エラー: {str(e)}", exc_info=True)
            raise Exception(f"スキャン状況の取得に失敗しました: {str(e)}")
    
    async def get_scan_results(self) -> Dict:
        """
        最新のスキャン結果を取得する
        """
        try:
            # 完了した最新のスキャンを取得
            completed_scan = await self.scan_repository.get_latest_completed_scan()
            
            if not completed_scan:
                return {
                    'scanId': '',
                    'completedAt': '',
                    'totalProcessed': 0,
                    'logicA': {
                        'detected': 0,
                        'stocks': []
                    },
                    'logicB': {
                        'detected': 0,
                        'stocks': []
                    }
                }
            
            scan_id = completed_scan['id']
            
            # スキャン結果を取得 (API仕様書準拠: logic_aとlogic_bのみ)
            logic_a_results = await self.scan_repository.get_scan_results_by_logic(scan_id, 'logic_a')
            logic_a_enhanced_results = await self.scan_repository.get_scan_results_by_logic(scan_id, 'logic_a_enhanced')
            logic_b_results = await self.scan_repository.get_scan_results_by_logic(scan_id, 'logic_b')
            logic_b_enhanced_results = await self.scan_repository.get_scan_results_by_logic(scan_id, 'logic_b_enhanced')
            
            # API仕様書準拠のため、通常版と強化版をマージ
            combined_logic_a = logic_a_results + logic_a_enhanced_results
            combined_logic_b = logic_b_results + logic_b_enhanced_results
            
            # completed_atの形式を統一（datetime → str）
            completed_at_str = ''
            if completed_scan['completed_at']:
                if isinstance(completed_scan['completed_at'], str):
                    completed_at_str = completed_scan['completed_at']
                else:
                    completed_at_str = completed_scan['completed_at'].isoformat()

            return {
                'scanId': scan_id,
                'completedAt': completed_at_str,
                'totalProcessed': completed_scan['processed_stocks'],
                'logicA': {
                    'detected': len(combined_logic_a),
                    'stocks': [self._format_stock_data(result) for result in combined_logic_a]
                },
                'logicB': {
                    'detected': len(combined_logic_b),
                    'stocks': [self._format_stock_data(result) for result in combined_logic_b]
                }
            }
            
        except Exception as e:
            logger.error(f"スキャン結果取得エラー: {str(e)}")
            raise Exception(f"スキャン結果の取得に失敗しました: {str(e)}")
    
    async def _execute_scan(self, scan_id: str):
        """
        実際のスキャン処理を非同期で実行
        各専門サービスを協調させて実行
        """
        try:
            # 銘柄リストを取得 (強化版: 実データソース対応)
            stock_list = self.stock_data_service.get_sample_stock_list()
            total_stocks = len(stock_list)
            logic_a_detected = []
            logic_a_enhanced_detected = []
            logic_b_detected = []
            logic_b_enhanced_detected = []
            
            logger.info(f"スキャン開始: 対象銘柄数 {total_stocks}件")
            
            # スキャン開始時の状態更新
            await self.scan_repository.update_scan_execution(scan_id, {
                'total_stocks': total_stocks,
                'message': 'スキャン実行中...',
                'estimated_time': total_stocks * 2  # 1銘柄2秒として推定
            })
            
            # 各銘柄をスキャン
            for i, stock in enumerate(stock_list):
                try:
                    # 進捗更新
                    await self._update_scan_progress(scan_id, i, total_stocks, stock)
                    
                    # 株価データ取得
                    stock_data = await self.stock_data_service.fetch_stock_data(
                        stock['code'], stock['name']
                    )
                    
                    if not stock_data:
                        logger.debug(f"銘柄 {stock['code']} のデータ取得失敗 - スキップ")
                        continue
                    
                    # データ妥当性検証 (強化版)
                    validation_result = await self._validate_stock_data_enhanced(stock_data)
                    if not validation_result['is_valid']:
                        logger.debug(f"銘柄 {stock['code']} データ検証失敗: {validation_result['reason']}")
                        continue
                    
                    # テクニカル分析実行
                    raw_data = stock_data.get('raw_data')
                    technical_signals = self.technical_analysis_service.generate_technical_signals(
                        price_data=raw_data,
                        stock_data=stock_data
                    )
                    
                    # テクニカルシグナルを統合
                    stock_data['signals'] = technical_signals
                    
                    # ロジックA検出（従来版）
                    if await self.logic_detection_service.detect_logic_a(stock_data):
                        logic_a_detected.append(stock_data)
                        await self._save_scan_result(scan_id, stock_data, 'logic_a')

                    # ロジックA厳密版検出（5つの条件判定）
                    logic_a_strict_result = await self.logic_a_strict_service.detect_strict_stop_high_sticking(stock_data)
                    if logic_a_strict_result['detected']:
                        stock_data['strict_logic_result'] = logic_a_strict_result
                        logger.info(f"🎯 ロジックA厳密版検出: {stock_data['code']} {stock_data['name']}")
                        # 厳密版は強化版として扱う
                        logic_a_enhanced_detected.append(stock_data)
                        await self._save_scan_result(scan_id, stock_data, 'logic_a_enhanced')

                    # ロジックA強化版検出（既存の強化版も残す）
                    logic_a_enhanced_result = await self.logic_detection_service.detect_logic_a_enhanced(stock_data)
                    if logic_a_enhanced_result['detected']:
                        stock_data['enhanced_signals'] = logic_a_enhanced_result
                        logic_a_enhanced_detected.append(stock_data)
                        await self._save_scan_result(scan_id, stock_data, 'logic_a_enhanced')
                    
                    # ロジックB検出（従来版）
                    if await self.logic_detection_service.detect_logic_b(stock_data):
                        logic_b_detected.append(stock_data)
                        await self._save_scan_result(scan_id, stock_data, 'logic_b')
                    
                    # ロジックB強化版検出（黒字転換銘柄精密検出）
                    logic_b_enhanced_result = await self.logic_detection_service.detect_logic_b_enhanced(stock_data)
                    if logic_b_enhanced_result['detected']:
                        stock_data['enhanced_signals'] = logic_b_enhanced_result
                        logic_b_enhanced_detected.append(stock_data)
                        await self._save_scan_result(scan_id, stock_data, 'logic_b_enhanced')
                    
                    # API制限を考慮した待機 (動的調整)
                    await self._dynamic_rate_limit(i, total_stocks)
                    
                except Exception as e:
                    logger.warning(f"銘柄 {stock['code']} の処理でエラー: {str(e)}", exc_info=True)
                    continue
            
            # スキャン完了
            await self._complete_scan(scan_id, total_stocks, logic_a_detected, logic_a_enhanced_detected, logic_b_detected, logic_b_enhanced_detected)
            
        except Exception as e:
            logger.error(f"スキャン実行エラー {scan_id}: {str(e)}")
            await self._fail_scan(scan_id, str(e))
    
    async def _update_scan_progress(self, scan_id: str, current_index: int, total_stocks: int, current_stock: Dict):
        """スキャン進捗を更新"""
        progress = int((current_index / total_stocks) * 100)
        remaining_time = (total_stocks - current_index) * 2
        
        await self.scan_repository.update_scan_execution(scan_id, {
            'progress': progress,
            'processed_stocks': current_index + 1,
            'current_stock': current_stock['code'],
            'estimated_time': remaining_time,
            'message': f'{current_stock["name"]}({current_stock["code"]})を分析中...'
        })
    
    async def _complete_scan(self, scan_id: str, total_stocks: int, logic_a_detected: List, logic_a_enhanced_detected: List, logic_b_detected: List, logic_b_enhanced_detected: List):
        """スキャン完了処理"""
        await self.scan_repository.update_scan_execution(scan_id, {
            'status': 'completed',
            'progress': 100,
            'processed_stocks': total_stocks,
            'current_stock': None,
            'estimated_time': 0,
            'message': 'スキャンが完了しました',
            'logic_a_count': len(logic_a_detected),
            'logic_a_enhanced_count': len(logic_a_enhanced_detected),
            'logic_b_count': len(logic_b_detected),
            'logic_b_enhanced_count': len(logic_b_enhanced_detected),
            'completed_at': datetime.now()
        })
        
        logger.info(f"スキャン {scan_id} が完了: ロジックA={len(logic_a_detected)}件, ロジックA強化版={len(logic_a_enhanced_detected)}件, ロジックB={len(logic_b_detected)}件, ロジックB強化版={len(logic_b_enhanced_detected)}件")
    
    async def _fail_scan(self, scan_id: str, error_message: str):
        """スキャン失敗処理"""
        await self.scan_repository.update_scan_execution(scan_id, {
            'status': 'failed',
            'message': 'スキャンでエラーが発生しました',
            'error_message': error_message,
            'completed_at': datetime.now()
        })
    
    async def _save_scan_result(self, scan_id: str, stock_data: Dict, logic_type: str):
        """
        スキャン結果をデータベースに保存
        """
        try:
            result = {
                'id': f"{scan_id}_{stock_data['code']}_{logic_type}",
                'scan_id': scan_id,
                'stock_code': stock_data['code'],
                'stock_name': stock_data['name'],
                'price': stock_data['price'],
                'change': stock_data['change'],
                'change_rate': stock_data['changeRate'],
                'volume': stock_data['volume'],
                'logic_type': logic_type,
                'technical_signals': stock_data['signals'],
                'market_cap': None
            }
            
            await self.scan_repository.create_scan_result(result)
            
        except Exception as e:
            logger.error(f"スキャン結果保存エラー: {str(e)}")
    
    def _format_stock_data(self, db_result: Dict) -> Dict:
        """
        データベース結果をAPI応答形式に変換
        """
        return {
            'code': db_result['stock_code'],
            'name': db_result['stock_name'],
            'price': float(db_result['price']),
            'change': float(db_result['change']),
            'changeRate': float(db_result['change_rate']),
            'volume': int(db_result['volume'])
        }
    
    # 新機能：設定管理
    async def get_logic_configs(self) -> Dict:
        """ロジック検出の設定を取得"""
        return self.logic_detection_service.get_logic_configs()
    
    async def update_logic_config(self, logic_type: str, **kwargs) -> Dict:
        """ロジック検出の設定を更新"""
        try:
            if logic_type == 'logic_a':
                self.logic_detection_service.update_logic_a_config(**kwargs)
            elif logic_type == 'logic_b':
                self.logic_detection_service.update_logic_b_config(**kwargs)
            else:
                raise ValueError(f"未知のロジックタイプ: {logic_type}")
            
            return {
                'success': True,
                'message': f'{logic_type}の設定を更新しました',
                'updated_config': self.logic_detection_service.get_logic_configs()
            }
            
        except Exception as e:
            logger.error(f"ロジック設定更新エラー: {str(e)}")
            raise Exception(f"設定更新に失敗しました: {str(e)}")
    
    # 新しいヘルパーメソッド
    async def _validate_stock_data_enhanced(self, stock_data: Dict) -> Dict:
        """
        強化版データ検証 - より詳細なバリデーション
        """
        try:
            # 基本フィールドの存在確認
            required_fields = ['code', 'name', 'price', 'change', 'changeRate', 'volume']
            missing_fields = [field for field in required_fields if field not in stock_data or stock_data[field] is None]
            
            if missing_fields:
                return {
                    'is_valid': False, 
                    'reason': f'必須フィールド不足: {", ".join(missing_fields)}'
                }
            
            # データの合理性チェック
            price = stock_data.get('price', 0)
            volume = stock_data.get('volume', 0)
            change_rate = stock_data.get('changeRate', 0)
            
            if price <= 0:
                return {'is_valid': False, 'reason': '価格が無効'}
            
            if volume < 0:
                return {'is_valid': False, 'reason': '出来高が無効'}
            
            if abs(change_rate) > 50:  # 50%を超える変動は異常
                return {'is_valid': False, 'reason': '変動率が異常'}
            
            return {'is_valid': True, 'reason': 'データ検証成功'}
            
        except Exception as e:
            return {'is_valid': False, 'reason': f'検証処理エラー: {str(e)}'}
    
    async def _dynamic_rate_limit(self, current_index: int, total_stocks: int) -> None:
        """
        動的レート制限 - 進捗に応じて待機時間を調整
        """
        try:
            # 進捗率に応じて待機時間を調整
            progress_ratio = current_index / total_stocks
            
            if progress_ratio < 0.1:  # 最初の10%は慎重に
                await asyncio.sleep(2)
            elif progress_ratio < 0.5:  # 50%までは通常
                await asyncio.sleep(1)
            else:  # 後半は高速化
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.warning(f"動的レート制限エラー: {str(e)}")
            await asyncio.sleep(1)  # フォールバック