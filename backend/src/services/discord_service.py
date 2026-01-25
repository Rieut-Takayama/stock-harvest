"""
Discord通知サービス
Stock Harvest AI - Discord通知機能
"""
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from ..models.discord_models import (
    DiscordConfigModel,
    DiscordConfigCreateRequest,
    DiscordConfigUpdateRequest,
    DiscordNotificationMessage,
    DiscordWebhookTestResult,
    ConnectionStatus,
    NotificationFormat
)
from ..repositories.discord_repository import DiscordRepository
from ..validators.discord_validators import (
    DiscordWebhookValidator,
    DiscordNotificationValidator,
    DiscordRateLimitValidator,
    DiscordConfigValidator
)
from ..lib.logger import logger
from ..lib.logger import PerformanceTracker


class DiscordNotificationService:
    """Discord通知サービスクラス"""
    
    def __init__(self, database_url: str):
        """
        サービスの初期化
        
        Args:
            database_url: データベース接続URL
        """
        self.repository = DiscordRepository(database_url)
        self.rate_limit_cache = {}  # メモリ内レート制限キャッシュ
        logger.info('DiscordNotificationService初期化完了')
    
    async def get_discord_config(self) -> Optional[DiscordConfigModel]:
        """
        Discord通知設定を取得
        
        Returns:
            DiscordConfigModel: Discord設定 (存在しない場合はNone)
        """
        try:
            tracker = PerformanceTracker('Discord設定取得')
            config = await self.repository.get_discord_config()
            tracker.end({'設定存在': config is not None})
            
            if config:
                logger.info(f'Discord設定を取得: チャンネル={config.channel_name}')
            else:
                logger.info('Discord設定が存在しません')
            
            return config
            
        except Exception as e:
            logger.error(f'Discord設定取得エラー: {e}')
            raise
    
    async def create_discord_config(self, request: DiscordConfigCreateRequest) -> DiscordConfigModel:
        """
        Discord通知設定を作成
        
        Args:
            request: 作成リクエスト
            
        Returns:
            DiscordConfigModel: 作成された設定
        """
        try:
            tracker = PerformanceTracker('Discord設定作成')
            
            # バリデーション実行
            logger.debug('Discord設定バリデーション開始')
            validator = DiscordConfigValidator(
                webhook_url=request.webhook_url,
                channel_name=request.channel_name,
                server_name=request.server_name,
                notification_types=request.notification_types,
                mention_role=request.mention_role,
                notification_format=request.notification_format.value,
                custom_message_template=request.custom_message_template
            )
            tracker.end({'バリデーション': '成功'})
            
            # Webhook接続テスト
            test_tracker = PerformanceTracker('Webhook接続テスト')
            webhook_test = DiscordWebhookValidator.test_webhook_connection(request.webhook_url)
            test_tracker.end({'テスト成功': webhook_test['success']})
            
            if not webhook_test['success']:
                logger.error(f'Webhook接続テスト失敗: {webhook_test["message"]}')
                raise ValueError(f'Discord Webhook接続に失敗しました: {webhook_test["message"]}')
            
            # 設定データ準備
            config_data = {
                'webhook_url': request.webhook_url,
                'is_enabled': True,
                'channel_name': request.channel_name,
                'server_name': request.server_name,
                'notification_types': request.notification_types,
                'mention_role': request.mention_role,
                'notification_format': request.notification_format.value,
                'custom_message_template': request.custom_message_template,
                'connection_status': ConnectionStatus.CONNECTED.value,
                'webhook_test_result': webhook_test
            }
            
            # データベース保存
            config = await self.repository.create_discord_config(config_data)
            
            logger.info(f'Discord設定を作成: チャンネル={config.channel_name}, サーバー={config.server_name}')
            return config
            
        except ValueError as ve:
            logger.warning(f'Discord設定作成バリデーションエラー: {ve}')
            raise
        except Exception as e:
            logger.error(f'Discord設定作成エラー: {e}')
            raise
    
    async def update_discord_config(self, update_request: DiscordConfigUpdateRequest) -> DiscordConfigModel:
        """
        Discord通知設定を更新
        
        Args:
            update_request: 更新リクエスト
            
        Returns:
            DiscordConfigModel: 更新された設定
        """
        try:
            tracker = PerformanceTracker('Discord設定更新')
            
            # 現在の設定を取得
            current_config = await self.repository.get_discord_config()
            if not current_config:
                logger.error('更新対象のDiscord設定が存在しません')
                raise ValueError('Discord設定が存在しません。まず設定を作成してください。')
            
            # 更新データを準備
            update_data = {}

            if update_request.webhook_url is not None:
                # Webhook URL変更の場合は接続テスト
                if update_request.webhook_url != current_config.webhook_url:
                    test_result = DiscordWebhookValidator.test_webhook_connection(update_request.webhook_url)
                    if not test_result['success']:
                        raise ValueError(f'新しいWebhook URLへの接続に失敗しました: {test_result["message"]}')

                    update_data['webhook_url'] = update_request.webhook_url
                    update_data['connection_status'] = ConnectionStatus.CONNECTED.value
                    update_data['webhook_test_result'] = test_result

            if update_request.is_enabled is not None:
                update_data['is_enabled'] = update_request.is_enabled

            if update_request.channel_name is not None:
                update_data['channel_name'] = update_request.channel_name.strip()

            if update_request.server_name is not None:
                update_data['server_name'] = update_request.server_name.strip()

            if update_request.notification_types is not None:
                update_data['notification_types'] = update_request.notification_types

            if update_request.mention_role is not None:
                update_data['mention_role'] = update_request.mention_role

            if update_request.notification_format is not None:
                update_data['notification_format'] = update_request.notification_format.value

            if update_request.custom_message_template is not None:
                update_data['custom_message_template'] = update_request.custom_message_template
            
            # データベース更新
            updated_config = await self.repository.update_discord_config(current_config.id, update_data)
            
            tracker.end({'更新項目数': len(update_data)})
            logger.info(f'Discord設定を更新: ID={current_config.id}, 更新項目={list(update_data.keys())}')
            
            return updated_config
            
        except ValueError as ve:
            logger.warning(f'Discord設定更新バリデーションエラー: {ve}')
            raise
        except Exception as e:
            logger.error(f'Discord設定更新エラー: {e}')
            raise
    
    async def test_discord_webhook(self, webhook_url: Optional[str] = None) -> DiscordWebhookTestResult:
        """
        Discord Webhook 接続テストを実行
        
        Args:
            webhook_url: テスト対象のWebhook URL (Noneの場合は設定済みURLを使用)
            
        Returns:
            DiscordWebhookTestResult: テスト結果
        """
        try:
            # Webhook URL決定
            if webhook_url is None:
                config = await self.repository.get_discord_config()
                if not config or not config.webhook_url:
                    return DiscordWebhookTestResult(
                        success=False,
                        message='テスト対象のWebhook URLが設定されていません',
                        tested_at=datetime.now()
                    )
                webhook_url = config.webhook_url
            
            # 接続テスト実行
            tracker = PerformanceTracker('Discord Webhook接続テスト')
            test_result = DiscordWebhookValidator.test_webhook_connection(webhook_url)
            tracker.end({'テスト成功': test_result['success']})
            
            # 結果をモデルに変換
            result = DiscordWebhookTestResult(
                success=test_result['success'],
                message=test_result['message'],
                response_status=test_result['responseStatus'],
                response_data=test_result['responseData'],
                error_detail=test_result['errorDetail'],
                tested_at=test_result['testedAt']
            )
            
            # 設定が存在する場合はテスト結果を保存
            if webhook_url and await self.repository.get_discord_config():
                await self.repository.update_discord_config(
                    config.id,
                    {
                        'webhook_test_result': test_result,
                        'connection_status': ConnectionStatus.CONNECTED.value if test_result['success']
                                            else ConnectionStatus.ERROR.value
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f'Discord Webhookテストエラー: {e}')
            return DiscordWebhookTestResult(
                success=False,
                message=f'テスト実行エラー: {str(e)}',
                error_detail=str(e),
                tested_at=datetime.now()
            )
    
    async def send_notification(self, notification: DiscordNotificationMessage) -> Dict[str, Any]:
        """
        Discord通知を送信
        
        Args:
            notification: 通知メッセージ
            
        Returns:
            Dict: 送信結果
        """
        result = {
            'success': False,
            'message': '',
            'sent_at': datetime.now(),
            'rate_limited': False
        }
        
        try:
            tracker = PerformanceTracker('Discord通知送信')
            
            # 設定取得
            config = await self.repository.get_discord_config()
            if not config or not config.is_enabled:
                result['message'] = 'Discord通知が無効または未設定です'
                logger.warning('Discord通知送信スキップ: 設定無効')
                return result

            if not config.webhook_url:
                result['message'] = 'Discord Webhook URLが設定されていません'
                logger.warning('Discord通知送信スキップ: WebhookURL未設定')
                return result
            
            # レート制限チェック
            rate_check = await self._check_rate_limit(config)
            if not rate_check['allowed']:
                result['rate_limited'] = True
                result['message'] = rate_check['reason']
                logger.warning(f'Discord通知送信スキップ: レート制限 - {rate_check["reason"]}')
                return result
            
            # 通知タイプチェック
            if notification.logic_type not in config.notification_types:
                result['message'] = f'通知タイプ {notification.logic_type} が無効です'
                logger.debug(f'Discord通知送信スキップ: 無効な通知タイプ {notification.logic_type}')
                return result

            # メッセージフォーマット
            message_content = DiscordNotificationValidator.format_stock_notification(
                stock_code=notification.stock_code,
                stock_name=notification.stock_name,
                logic_type=notification.logic_type,
                price=notification.price,
                change_rate=notification.change_rate,
                volume=notification.volume,
                format_type=config.notification_format.value,
                custom_template=config.custom_message_template
            )
            
            # Discord Webhookペイロード構築
            webhook_payload = {
                'content': message_content,
                'username': 'Stock Harvest AI',
                'avatar_url': 'https://via.placeholder.com/64x64.png?text=SH'
            }
            
            # メンションロール追加
            if config.mention_role and config.mention_role.strip():
                mention = config.mention_role.strip()
                if mention.isdigit() and len(mention) >= 17:
                    # Discord role ID の場合
                    webhook_payload['content'] = f"<@&{mention}> {webhook_payload['content']}"
                elif mention.startswith('<@&') and mention.endswith('>'):
                    # Discord mention 形式の場合
                    webhook_payload['content'] = f"{mention} {webhook_payload['content']}"
            
            # Discord API呼び出し
            response = requests.post(
                config.webhook_url,
                json=webhook_payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 204:
                # 送信成功
                result['success'] = True
                result['message'] = 'Discord通知を送信しました'
                
                # カウンター更新
                await self.repository.increment_notification_count(config.id)
                
                tracker.end({'送信成功': True, '銘柄': notification.stock_code})
                logger.info(f'Discord通知送信成功: {notification.stock_code} - {notification.logic_type}')
                
            else:
                # 送信失敗
                result['message'] = f'Discord API エラー: HTTP {response.status_code}'
                error_detail = f'HTTP {response.status_code}: {response.text}'
                
                # エラーカウンター更新
                await self.repository.increment_error_count(config.id, error_detail)
                
                logger.error(f'Discord通知送信失敗: {response.status_code} - {response.text}')
            
        except requests.exceptions.Timeout:
            result['message'] = 'Discord通知送信タイムアウト'
            await self._handle_notification_error(config, 'Discord通知送信タイムアウト')
            logger.error('Discord通知送信タイムアウト')
            
        except requests.exceptions.ConnectionError:
            result['message'] = 'Discord接続エラー'
            await self._handle_notification_error(config, 'Discord接続エラー')
            logger.error('Discord通知送信 接続エラー')
            
        except Exception as e:
            result['message'] = f'Discord通知送信エラー: {str(e)}'
            await self._handle_notification_error(config, str(e))
            logger.error(f'Discord通知送信エラー: {e}')
        
        return result
    
    async def send_stock_match_notification(
        self,
        stock_code: str,
        stock_name: str,
        logic_type: str,
        price: float,
        change_rate: float,
        volume: int,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        株式ロジック合致通知を送信
        
        Args:
            stock_code: 銘柄コード
            stock_name: 銘柄名
            logic_type: ロジックタイプ ('logic_a_match' | 'logic_b_match')
            price: 株価
            change_rate: 変動率
            volume: 出来高
            additional_info: 追加情報
            
        Returns:
            Dict: 送信結果
        """
        notification = DiscordNotificationMessage(
            stock_code=stock_code,
            stock_name=stock_name,
            logic_type=logic_type,
            price=price,
            change_rate=change_rate,
            volume=volume,
            detection_time=datetime.now(),
            additional_info=additional_info
        )
        
        return await self.send_notification(notification)
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """
        Discord通知統計を取得
        
        Returns:
            Dict: 通知統計
        """
        try:
            stats = await self.repository.get_notification_stats()
            
            # 現在の時刻情報を追加
            now = datetime.now()
            stats['current_time'] = now.isoformat()

            # レート制限状況を計算
            if stats['last_sent_at']:
                last_sent = stats['last_sent_at']
                time_since_last = (now - last_sent).total_seconds()
                stats['time_since_last_notification'] = time_since_last
            else:
                stats['time_since_last_notification'] = None

            # 今日の利用可能通知数を計算
            config = await self.repository.get_discord_config()
            if config:
                remaining_today = max(0, (config.rate_limit_per_hour * 24) - stats['today_count'])
                stats['remaining_today'] = remaining_today
                stats['is_enabled'] = config.is_enabled
                stats['rate_limit_per_hour'] = config.rate_limit_per_hour
            else:
                stats['remaining_today'] = 0
                stats['is_enabled'] = False
                stats['rate_limit_per_hour'] = 60

            logger.debug(f'Discord通知統計: 今日={stats["today_count"]}, 総数={stats["total_sent"]}')
            return stats
            
        except Exception as e:
            logger.error(f'Discord通知統計取得エラー: {e}')
            return {
                'today_count': 0,
                'total_sent': 0,
                'error_count': 0,
                'remaining_today': 0,
                'is_enabled': False,
                'time_since_last_notification': None,
                'last_sent_at': None
            }
    
    async def _check_rate_limit(self, config: DiscordConfigModel) -> Dict[str, Any]:
        """レート制限をチェック"""
        now = datetime.now()
        config_id = config.id
        
        # 時間内送信数をカウント (簡易実装: メモリキャッシュ)
        hour_key = f"{config_id}_{now.hour}"
        
        if hour_key not in self.rate_limit_cache:
            self.rate_limit_cache[hour_key] = {
                'count': 0,
                'hour': now.hour
            }
        
        # 時間が変わった場合はリセット
        if self.rate_limit_cache[hour_key]['hour'] != now.hour:
            self.rate_limit_cache[hour_key] = {
                'count': 0,
                'hour': now.hour
            }
        
        current_hour_count = self.rate_limit_cache[hour_key]['count']
        
        # レート制限チェック
        rate_check = DiscordRateLimitValidator.check_rate_limit(
            current_count=current_hour_count,
            hourly_limit=config.rate_limit_per_hour,
            daily_count=config.notification_count_today,
            daily_limit=config.rate_limit_per_hour * 24
        )
        
        # 送信許可の場合はカウンターを増加
        if rate_check['allowed']:
            self.rate_limit_cache[hour_key]['count'] += 1
        
        return rate_check
    
    async def _handle_notification_error(self, config: DiscordConfigModel, error_message: str):
        """通知エラーハンドリング"""
        try:
            if config:
                await self.repository.increment_error_count(config.id, error_message)
                
                # 連続エラーが多い場合は接続状態を更新
                if config.error_count >= 5:
                    await self.repository.update_discord_config(
                        config.id,
                        {'connection_status': ConnectionStatus.ERROR.value}
                    )
                    logger.warning(f'Discord設定のステータスをERRORに変更: 連続エラー数={config.error_count}')
        except Exception as e:
            logger.error(f'Discord通知エラーハンドリング失敗: {e}')
    
    async def reset_daily_counters(self):
        """日次カウンターリセット (日次バッチ処理用)"""
        try:
            await self.repository.reset_daily_counter()
            # メモリキャッシュもクリア
            self.rate_limit_cache.clear()
            logger.info('Discord通知の日次カウンターをリセットしました')
        except Exception as e:
            logger.error(f'Discord日次カウンターリセットエラー: {e}')
            raise
    
    async def disable_notifications(self) -> bool:
        """
        Discord通知を無効にする
        
        Returns:
            bool: 無効化成功時True
        """
        try:
            config = await self.repository.get_discord_config()
            if config:
                await self.repository.update_discord_config(config.id, {'is_enabled': False})
                logger.info('Discord通知を無効にしました')
                return True
            return False
        except Exception as e:
            logger.error(f'Discord通知無効化エラー: {e}')
            return False
    
    async def enable_notifications(self) -> bool:
        """
        Discord通知を有効にする
        
        Returns:
            bool: 有効化成功時True
        """
        try:
            config = await self.repository.get_discord_config()
            if config:
                await self.repository.update_discord_config(config.id, {'is_enabled': True})
                logger.info('Discord通知を有効にしました')
                return True
            return False
        except Exception as e:
            logger.error(f'Discord通知有効化エラー: {e}')
            return False