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
                logger.info(f'Discord設定を取得: チャンネル={config.channelName}')
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
                webhookUrl=request.webhookUrl,
                channelName=request.channelName,
                serverName=request.serverName,
                notificationTypes=request.notificationTypes,
                mentionRole=request.mentionRole,
                notificationFormat=request.notificationFormat.value,
                customMessageTemplate=request.customMessageTemplate
            )
            tracker.end({'バリデーション': '成功'})
            
            # Webhook接続テスト
            test_tracker = PerformanceTracker('Webhook接続テスト')
            webhook_test = DiscordWebhookValidator.test_webhook_connection(request.webhookUrl)
            test_tracker.end({'テスト成功': webhook_test['success']})
            
            if not webhook_test['success']:
                logger.error(f'Webhook接続テスト失敗: {webhook_test["message"]}')
                raise ValueError(f'Discord Webhook接続に失敗しました: {webhook_test["message"]}')
            
            # 設定データ準備
            config_data = {
                'webhookUrl': request.webhookUrl,
                'isEnabled': True,
                'channelName': request.channelName,
                'serverName': request.serverName,
                'notificationTypes': request.notificationTypes,
                'mentionRole': request.mentionRole,
                'notificationFormat': request.notificationFormat.value,
                'customMessageTemplate': request.customMessageTemplate,
                'connectionStatus': ConnectionStatus.CONNECTED.value,
                'webhookTestResult': webhook_test
            }
            
            # データベース保存
            config = await self.repository.create_discord_config(config_data)
            
            logger.info(f'Discord設定を作成: チャンネル={config.channelName}, サーバー={config.serverName}')
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
            
            if update_request.webhookUrl is not None:
                # Webhook URL変更の場合は接続テスト
                if update_request.webhookUrl != current_config.webhookUrl:
                    test_result = DiscordWebhookValidator.test_webhook_connection(update_request.webhookUrl)
                    if not test_result['success']:
                        raise ValueError(f'新しいWebhook URLへの接続に失敗しました: {test_result["message"]}')
                    
                    update_data['webhookUrl'] = update_request.webhookUrl
                    update_data['connectionStatus'] = ConnectionStatus.CONNECTED.value
                    update_data['webhookTestResult'] = test_result
            
            if update_request.isEnabled is not None:
                update_data['isEnabled'] = update_request.isEnabled
            
            if update_request.channelName is not None:
                update_data['channelName'] = update_request.channelName.strip()
            
            if update_request.serverName is not None:
                update_data['serverName'] = update_request.serverName.strip()
            
            if update_request.notificationTypes is not None:
                update_data['notificationTypes'] = update_request.notificationTypes
            
            if update_request.mentionRole is not None:
                update_data['mentionRole'] = update_request.mentionRole
            
            if update_request.notificationFormat is not None:
                update_data['notificationFormat'] = update_request.notificationFormat.value
            
            if update_request.customMessageTemplate is not None:
                update_data['customMessageTemplate'] = update_request.customMessageTemplate
            
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
                if not config or not config.webhookUrl:
                    return DiscordWebhookTestResult(
                        success=False,
                        message='テスト対象のWebhook URLが設定されていません',
                        testedAt=datetime.now()
                    )
                webhook_url = config.webhookUrl
            
            # 接続テスト実行
            tracker = PerformanceTracker('Discord Webhook接続テスト')
            test_result = DiscordWebhookValidator.test_webhook_connection(webhook_url)
            tracker.end({'テスト成功': test_result['success']})
            
            # 結果をモデルに変換
            result = DiscordWebhookTestResult(
                success=test_result['success'],
                message=test_result['message'],
                responseStatus=test_result['responseStatus'],
                responseData=test_result['responseData'],
                errorDetail=test_result['errorDetail'],
                testedAt=test_result['testedAt']
            )
            
            # 設定が存在する場合はテスト結果を保存
            if webhook_url and await self.repository.get_discord_config():
                await self.repository.update_discord_config(
                    config.id, 
                    {
                        'webhookTestResult': test_result,
                        'connectionStatus': ConnectionStatus.CONNECTED.value if test_result['success'] 
                                            else ConnectionStatus.ERROR.value
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f'Discord Webhookテストエラー: {e}')
            return DiscordWebhookTestResult(
                success=False,
                message=f'テスト実行エラー: {str(e)}',
                errorDetail=str(e),
                testedAt=datetime.now()
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
            if not config or not config.isEnabled:
                result['message'] = 'Discord通知が無効または未設定です'
                logger.warning('Discord通知送信スキップ: 設定無効')
                return result
            
            if not config.webhookUrl:
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
            if notification.logicType not in config.notificationTypes:
                result['message'] = f'通知タイプ {notification.logicType} が無効です'
                logger.debug(f'Discord通知送信スキップ: 無効な通知タイプ {notification.logicType}')
                return result
            
            # メッセージフォーマット
            message_content = DiscordNotificationValidator.format_stock_notification(
                stock_code=notification.stockCode,
                stock_name=notification.stockName,
                logic_type=notification.logicType,
                price=notification.price,
                change_rate=notification.changeRate,
                volume=notification.volume,
                format_type=config.notificationFormat.value,
                custom_template=config.customMessageTemplate
            )
            
            # Discord Webhookペイロード構築
            webhook_payload = {
                'content': message_content,
                'username': 'Stock Harvest AI',
                'avatar_url': 'https://via.placeholder.com/64x64.png?text=SH'
            }
            
            # メンションロール追加
            if config.mentionRole and config.mentionRole.strip():
                mention = config.mentionRole.strip()
                if mention.isdigit() and len(mention) >= 17:
                    # Discord role ID の場合
                    webhook_payload['content'] = f"<@&{mention}> {webhook_payload['content']}"
                elif mention.startswith('<@&') and mention.endswith('>'):
                    # Discord mention 形式の場合
                    webhook_payload['content'] = f"{mention} {webhook_payload['content']}"
            
            # Discord API呼び出し
            response = requests.post(
                config.webhookUrl,
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
                
                tracker.end({'送信成功': True, '銘柄': notification.stockCode})
                logger.info(f'Discord通知送信成功: {notification.stockCode} - {notification.logicType}')
                
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
            stockCode=stock_code,
            stockName=stock_name,
            logicType=logic_type,
            price=price,
            changeRate=change_rate,
            volume=volume,
            detectionTime=datetime.now(),
            additionalInfo=additional_info
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
            stats['currentTime'] = now.isoformat()
            
            # レート制限状況を計算
            if stats['lastSentAt']:
                last_sent = stats['lastSentAt']
                time_since_last = (now - last_sent).total_seconds()
                stats['timeSinceLastNotification'] = time_since_last
            else:
                stats['timeSinceLastNotification'] = None
            
            # 今日の利用可能通知数を計算
            config = await self.repository.get_discord_config()
            if config:
                remaining_today = max(0, (config.rateLimitPerHour * 24) - stats['todayCount'])
                stats['remainingToday'] = remaining_today
                stats['isEnabled'] = config.isEnabled
                stats['rateLimitPerHour'] = config.rateLimitPerHour
            else:
                stats['remainingToday'] = 0
                stats['isEnabled'] = False
                stats['rateLimitPerHour'] = 60
            
            logger.debug(f'Discord通知統計: 今日={stats["todayCount"]}, 総数={stats["totalSent"]}')
            return stats
            
        except Exception as e:
            logger.error(f'Discord通知統計取得エラー: {e}')
            return {
                'todayCount': 0,
                'totalSent': 0,
                'errorCount': 0,
                'remainingToday': 0,
                'isEnabled': False,
                'timeSinceLastNotification': None,
                'lastSentAt': None
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
            hourly_limit=config.rateLimitPerHour,
            daily_count=config.notificationCountToday,
            daily_limit=config.rateLimitPerHour * 24
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
                if config.errorCount >= 5:
                    await self.repository.update_discord_config(
                        config.id,
                        {'connectionStatus': ConnectionStatus.ERROR.value}
                    )
                    logger.warning(f'Discord設定のステータスをERRORに変更: 連続エラー数={config.errorCount}')
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
                await self.repository.update_discord_config(config.id, {'isEnabled': False})
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
                await self.repository.update_discord_config(config.id, {'isEnabled': True})
                logger.info('Discord通知を有効にしました')
                return True
            return False
        except Exception as e:
            logger.error(f'Discord通知有効化エラー: {e}')
            return False