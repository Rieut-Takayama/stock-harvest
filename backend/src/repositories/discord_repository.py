"""
Discord通知設定リポジトリ
Stock Harvest AI - Discord通知機能
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from ..models.discord_models import (
    DiscordConfigModel,
    DiscordNotificationHistory,
    ConnectionStatus,
    NotificationFormat
)
from ..lib.logger import logger


class DiscordRepository:
    """Discord通知設定データアクセスクラス"""
    
    def __init__(self, database_url: str):
        """
        リポジトリの初期化
        
        Args:
            database_url: データベース接続URL (SQLite)
        """
        self.database_url = database_url.replace("sqlite:///", "")
        logger.debug(f'DiscordRepository初期化: {self.database_url}')
    
    @contextmanager
    def get_connection(self):
        """データベース接続の取得"""
        conn = None
        try:
            conn = sqlite3.connect(self.database_url)
            conn.row_factory = sqlite3.Row  # カラム名でアクセス可能
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f'データベース接続エラー: {e}')
            raise
        finally:
            if conn:
                conn.close()
    
    async def get_discord_config(self) -> Optional[DiscordConfigModel]:
        """
        Discord通知設定を取得
        
        Returns:
            DiscordConfigModel: Discord設定 (存在しない場合はNone)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        id, webhook_url, is_enabled, channel_name, server_name,
                        notification_types, mention_role, notification_format,
                        rate_limit_per_hour, last_notification_at, notification_count_today,
                        total_notifications_sent, error_count, last_error_message,
                        last_error_at, connection_status, webhook_test_result,
                        custom_message_template, created_at, updated_at
                    FROM discord_config 
                    ORDER BY id DESC LIMIT 1
                """)
                
                row = cursor.fetchone()
                if not row:
                    logger.info('Discord設定が見つかりません')
                    return None
                
                # notification_types を文字列からリストに変換
                notification_types = []
                if row['notification_types']:
                    notification_types = row['notification_types'].split(',')
                
                config = DiscordConfigModel(
                    id=row['id'],
                    webhookUrl=row['webhook_url'],
                    isEnabled=bool(row['is_enabled']),
                    channelName=row['channel_name'],
                    serverName=row['server_name'],
                    notificationTypes=notification_types,
                    mentionRole=row['mention_role'],
                    notificationFormat=NotificationFormat(row['notification_format'] or 'standard'),
                    rateLimitPerHour=row['rate_limit_per_hour'] or 60,
                    lastNotificationAt=self._parse_datetime(row['last_notification_at']),
                    notificationCountToday=row['notification_count_today'] or 0,
                    totalNotificationsSent=row['total_notifications_sent'] or 0,
                    errorCount=row['error_count'] or 0,
                    lastErrorMessage=row['last_error_message'],
                    lastErrorAt=self._parse_datetime(row['last_error_at']),
                    connectionStatus=ConnectionStatus(row['connection_status'] or 'disconnected'),
                    webhookTestResult=self._parse_json(row['webhook_test_result']),
                    customMessageTemplate=row['custom_message_template'],
                    createdAt=self._parse_datetime(row['created_at']),
                    updatedAt=self._parse_datetime(row['updated_at'])
                )
                
                logger.info(f'Discord設定を取得: ID={config.id}')
                return config
                
        except Exception as e:
            logger.error(f'Discord設定取得エラー: {e}')
            raise
    
    async def create_discord_config(self, config_data: Dict[str, Any]) -> DiscordConfigModel:
        """
        Discord通知設定を作成
        
        Args:
            config_data: 設定データ
            
        Returns:
            DiscordConfigModel: 作成された設定
        """
        try:
            with self.get_connection() as conn:
                # 既存設定を削除 (単一設定のため)
                conn.execute("DELETE FROM discord_config")
                
                # 新設定を挿入
                notification_types_str = ','.join(config_data.get('notificationTypes', []))
                now = datetime.now().isoformat()
                
                cursor = conn.execute("""
                    INSERT INTO discord_config (
                        webhook_url, is_enabled, channel_name, server_name,
                        notification_types, mention_role, notification_format,
                        rate_limit_per_hour, notification_count_today, 
                        total_notifications_sent, error_count, connection_status,
                        custom_message_template, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    config_data['webhookUrl'],
                    config_data.get('isEnabled', True),
                    config_data['channelName'],
                    config_data['serverName'],
                    notification_types_str,
                    config_data.get('mentionRole'),
                    config_data.get('notificationFormat', 'standard'),
                    config_data.get('rateLimitPerHour', 60),
                    0,  # notification_count_today
                    0,  # total_notifications_sent
                    0,  # error_count
                    config_data.get('connectionStatus', 'disconnected'),
                    config_data.get('customMessageTemplate'),
                    now,  # created_at
                    now   # updated_at
                ))
                
                config_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f'Discord設定を作成: ID={config_id}')
                
                # 作成した設定を取得して返す
                return await self.get_discord_config()
                
        except Exception as e:
            logger.error(f'Discord設定作成エラー: {e}')
            raise
    
    async def update_discord_config(self, config_id: int, update_data: Dict[str, Any]) -> DiscordConfigModel:
        """
        Discord通知設定を更新
        
        Args:
            config_id: 設定ID
            update_data: 更新データ
            
        Returns:
            DiscordConfigModel: 更新された設定
        """
        try:
            with self.get_connection() as conn:
                # 動的にUPDATE文を構築
                update_fields = []
                update_values = []
                
                for key, value in update_data.items():
                    if key == 'notificationTypes':
                        update_fields.append('notification_types = ?')
                        update_values.append(','.join(value) if value else '')
                    elif key == 'isEnabled':
                        update_fields.append('is_enabled = ?')
                        update_values.append(value)
                    elif key == 'webhookUrl':
                        update_fields.append('webhook_url = ?')
                        update_values.append(value)
                    elif key == 'channelName':
                        update_fields.append('channel_name = ?')
                        update_values.append(value)
                    elif key == 'serverName':
                        update_fields.append('server_name = ?')
                        update_values.append(value)
                    elif key == 'mentionRole':
                        update_fields.append('mention_role = ?')
                        update_values.append(value)
                    elif key == 'notificationFormat':
                        update_fields.append('notification_format = ?')
                        update_values.append(value)
                    elif key == 'customMessageTemplate':
                        update_fields.append('custom_message_template = ?')
                        update_values.append(value)
                    elif key == 'connectionStatus':
                        update_fields.append('connection_status = ?')
                        update_values.append(value)
                    elif key == 'webhookTestResult':
                        update_fields.append('webhook_test_result = ?')
                        update_values.append(self._serialize_json(value))
                
                if update_fields:
                    update_fields.append('updated_at = ?')
                    update_values.append(datetime.now().isoformat())
                    update_values.append(config_id)  # WHERE条件用
                    
                    sql = f"""
                        UPDATE discord_config 
                        SET {', '.join(update_fields)}
                        WHERE id = ?
                    """
                    
                    conn.execute(sql, update_values)
                    conn.commit()
                    
                    logger.info(f'Discord設定を更新: ID={config_id}')
                
                # 更新された設定を取得して返す
                return await self.get_discord_config()
                
        except Exception as e:
            logger.error(f'Discord設定更新エラー: {e}')
            raise
    
    async def increment_notification_count(self, config_id: int) -> bool:
        """
        通知送信カウンターを増加
        
        Args:
            config_id: 設定ID
            
        Returns:
            bool: 更新成功時True
        """
        try:
            with self.get_connection() as conn:
                now = datetime.now()
                conn.execute("""
                    UPDATE discord_config 
                    SET 
                        notification_count_today = notification_count_today + 1,
                        total_notifications_sent = total_notifications_sent + 1,
                        last_notification_at = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (now.isoformat(), now.isoformat(), config_id))
                
                conn.commit()
                
                logger.debug(f'Discord通知カウンターを増加: ID={config_id}')
                return True
                
        except Exception as e:
            logger.error(f'Discord通知カウンター更新エラー: {e}')
            return False
    
    async def increment_error_count(self, config_id: int, error_message: str) -> bool:
        """
        エラーカウンターを増加
        
        Args:
            config_id: 設定ID
            error_message: エラーメッセージ
            
        Returns:
            bool: 更新成功時True
        """
        try:
            with self.get_connection() as conn:
                now = datetime.now()
                conn.execute("""
                    UPDATE discord_config 
                    SET 
                        error_count = error_count + 1,
                        last_error_message = ?,
                        last_error_at = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (error_message, now.isoformat(), now.isoformat(), config_id))
                
                conn.commit()
                
                logger.warning(f'Discordエラーカウンターを増加: ID={config_id}, エラー={error_message}')
                return True
                
        except Exception as e:
            logger.error(f'Discordエラーカウンター更新エラー: {e}')
            return False
    
    async def reset_daily_counter(self) -> bool:
        """
        日次カウンターをリセット
        
        Returns:
            bool: リセット成功時True
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE discord_config 
                    SET 
                        notification_count_today = 0,
                        updated_at = ?
                """, (datetime.now().isoformat(),))
                
                conn.commit()
                
                logger.info('Discord日次カウンターをリセット')
                return True
                
        except Exception as e:
            logger.error(f'Discord日次カウンターリセットエラー: {e}')
            return False
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """
        通知統計を取得
        
        Returns:
            Dict: 統計データ
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        notification_count_today,
                        total_notifications_sent,
                        error_count,
                        rate_limit_per_hour,
                        last_notification_at
                    FROM discord_config 
                    ORDER BY id DESC LIMIT 1
                """)
                
                row = cursor.fetchone()
                if not row:
                    return {
                        'todayCount': 0,
                        'totalSent': 0,
                        'errorCount': 0,
                        'hourlyLimit': 60,
                        'lastSentAt': None
                    }
                
                return {
                    'todayCount': row['notification_count_today'] or 0,
                    'totalSent': row['total_notifications_sent'] or 0,
                    'errorCount': row['error_count'] or 0,
                    'hourlyLimit': row['rate_limit_per_hour'] or 60,
                    'lastSentAt': self._parse_datetime(row['last_notification_at'])
                }
                
        except Exception as e:
            logger.error(f'Discord通知統計取得エラー: {e}')
            return {
                'todayCount': 0,
                'totalSent': 0,
                'errorCount': 0,
                'hourlyLimit': 60,
                'lastSentAt': None
            }
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """文字列をdatetimeに変換"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            logger.warning(f'無効な日時形式: {dt_str}')
            return None
    
    def _parse_json(self, json_str: Optional[str]) -> Optional[Dict[str, Any]]:
        """文字列をJSONに変換"""
        if not json_str:
            return None
        try:
            import json
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f'無効なJSON形式: {json_str}')
            return None
    
    def _serialize_json(self, data: Any) -> Optional[str]:
        """データをJSON文字列に変換"""
        if data is None:
            return None
        try:
            import json
            return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            logger.warning(f'JSON変換失敗: {data}')
            return None