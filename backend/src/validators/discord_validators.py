"""
Discord通知設定バリデーター
Stock Harvest AI - Discord通知機能
"""
import re
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, validator, ValidationError
from datetime import datetime

from ..lib.logger import logger


class DiscordWebhookValidator:
    """Discord Webhook URL バリデーター"""
    
    @staticmethod
    def validate_webhook_format(webhook_url: str) -> bool:
        """
        Webhook URL の基本フォーマットをバリデーション
        
        Args:
            webhook_url: 検証するWebhook URL
            
        Returns:
            bool: 有効な場合True
        """
        if not webhook_url:
            return False
            
        # Discord Webhook URL の基本パターン
        pattern = r'^https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$'
        
        return bool(re.match(pattern, webhook_url))
    
    @staticmethod
    def test_webhook_connection(webhook_url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Webhook URL への実際の接続テストを実行
        
        Args:
            webhook_url: テストするWebhook URL
            timeout: タイムアウト秒数
            
        Returns:
            Dict: テスト結果
        """
        result = {
            'success': False,
            'message': '',
            'responseStatus': None,
            'responseData': None,
            'errorDetail': None,
            'testedAt': datetime.now()
        }
        
        try:
            # Discord Webhook にテストメッセージを送信
            test_payload = {
                'content': '🤖 Stock Harvest AI - Discord通知設定テスト\nこのメッセージが表示されれば、Webhookの設定が正常に完了しています。',
                'username': 'Stock Harvest AI',
                'avatar_url': 'https://via.placeholder.com/64x64.png?text=SH'
            }
            
            logger.debug(f'Discord Webhook 接続テスト開始: {webhook_url[:50]}...')
            
            response = requests.post(
                webhook_url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=timeout
            )
            
            result['responseStatus'] = response.status_code
            
            if response.status_code == 204:
                result['success'] = True
                result['message'] = 'Discord通知設定が正常に完了しました'
                logger.info('Discord Webhook 接続テスト成功')
            else:
                result['success'] = False
                result['message'] = f'Discord Webhook エラー: HTTP {response.status_code}'
                result['errorDetail'] = response.text
                logger.warning(f'Discord Webhook 接続テスト失敗: {response.status_code}')
                
        except requests.exceptions.Timeout:
            result['message'] = 'Discord Webhook への接続がタイムアウトしました'
            result['errorDetail'] = 'Connection timeout'
            logger.error('Discord Webhook 接続テスト タイムアウト')
            
        except requests.exceptions.ConnectionError:
            result['message'] = 'Discord Webhook への接続に失敗しました'
            result['errorDetail'] = 'Connection failed'
            logger.error('Discord Webhook 接続テスト 接続失敗')
            
        except Exception as e:
            result['message'] = f'Discord Webhook テストでエラーが発生しました: {str(e)}'
            result['errorDetail'] = str(e)
            logger.error(f'Discord Webhook 接続テスト エラー: {e}')
        
        return result


class DiscordConfigValidator(BaseModel):
    """Discord設定全体のバリデーター"""
    
    webhookUrl: str
    channelName: str
    serverName: str
    notificationTypes: List[str]
    mentionRole: Optional[str] = None
    notificationFormat: str = "standard"
    customMessageTemplate: Optional[str] = None
    
    @validator('webhookUrl')
    def validate_webhook_url(cls, v: str) -> str:
        """Webhook URL の形式検証"""
        if not DiscordWebhookValidator.validate_webhook_format(v):
            raise ValueError('有効なDiscord Webhook URLを入力してください')
        return v
    
    @validator('channelName', 'serverName')
    def validate_names(cls, v: str) -> str:
        """チャンネル名・サーバー名の検証"""
        if not v or len(v.strip()) == 0:
            raise ValueError('チャンネル名・サーバー名は必須です')
        if len(v.strip()) > 100:
            raise ValueError('名前は100文字以内で入力してください')
        return v.strip()
    
    @validator('notificationTypes')
    def validate_notification_types(cls, v: List[str]) -> List[str]:
        """通知タイプの検証"""
        allowed_types = {
            'logic_a_match': 'ロジックA検出',
            'logic_b_match': 'ロジックB検出',
            'price_alert': '価格アラート',
            'scan_complete': 'スキャン完了',
            'system_error': 'システムエラー'
        }
        
        if not v:
            raise ValueError('少なくとも1つの通知タイプを選択してください')
        
        for notification_type in v:
            if notification_type not in allowed_types:
                raise ValueError(f'無効な通知タイプ: {notification_type}')
        
        return v
    
    @validator('mentionRole')
    def validate_mention_role(cls, v: Optional[str]) -> Optional[str]:
        """メンションロールの検証"""
        if v is None:
            return v
        
        v = v.strip()
        if v == "":
            return None
        
        # Discord role ID または role name の基本検証
        if v.startswith('<@&') and v.endswith('>'):
            # Discord role mention format
            return v
        elif v.isdigit() and len(v) >= 17:
            # Discord role ID format (snowflake)
            return v
        else:
            # Role name format - basic validation
            if len(v) > 100:
                raise ValueError('ロール名は100文字以内で入力してください')
            return v
    
    @validator('notificationFormat')
    def validate_notification_format(cls, v: str) -> str:
        """通知フォーマットの検証"""
        allowed_formats = ['standard', 'compact', 'detailed']
        if v not in allowed_formats:
            raise ValueError(f'無効な通知フォーマット: {v}')
        return v
    
    @validator('customMessageTemplate')
    def validate_custom_template(cls, v: Optional[str]) -> Optional[str]:
        """カスタムメッセージテンプレートの検証"""
        if v is None or v.strip() == "":
            return None
        
        v = v.strip()
        
        # テンプレート長さ制限
        if len(v) > 2000:
            raise ValueError('カスタムメッセージテンプレートは2000文字以内で入力してください')
        
        # 必須プレースホルダーの存在確認
        required_placeholders = ['{stockCode}', '{stockName}']
        for placeholder in required_placeholders:
            if placeholder not in v:
                logger.warning(f'推奨プレースホルダー {placeholder} がテンプレートに含まれていません')
        
        return v


class DiscordNotificationValidator:
    """Discord通知メッセージのバリデーター"""
    
    @staticmethod
    def validate_message_content(content: str) -> bool:
        """
        Discord メッセージ内容のバリデーション
        
        Args:
            content: メッセージ内容
            
        Returns:
            bool: 有効な場合True
        """
        if not content:
            return False
        
        # Discord の文字数制限 (2000文字)
        if len(content) > 2000:
            return False
        
        # 基本的な文字エンコーディングチェック
        try:
            content.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
    
    @staticmethod
    def sanitize_message_content(content: str) -> str:
        """
        Discord メッセージ内容のサニタイズ
        
        Args:
            content: 元のメッセージ内容
            
        Returns:
            str: サニタイズされたメッセージ内容
        """
        if not content:
            return ""
        
        # 長すぎる場合は切り詰める
        if len(content) > 1900:  # 余裕を持って1900文字まで
            content = content[:1900] + "..."
        
        # 不正文字の除去 (制御文字など)
        content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
        
        # Discord markdown のエスケープ処理
        content = content.replace('`', '\\`').replace('*', '\\*').replace('_', '\\_')
        
        return content
    
    @staticmethod
    def format_stock_notification(
        stock_code: str,
        stock_name: str,
        logic_type: str,
        price: float,
        change_rate: float,
        volume: int,
        format_type: str = "standard",
        custom_template: Optional[str] = None
    ) -> str:
        """
        株式情報通知メッセージのフォーマット
        
        Args:
            stock_code: 銘柄コード
            stock_name: 銘柄名
            logic_type: ロジックタイプ
            price: 株価
            change_rate: 変動率
            volume: 出来高
            format_type: フォーマットタイプ
            custom_template: カスタムテンプレート
            
        Returns:
            str: フォーマット済みメッセージ
        """
        try:
            if custom_template:
                # カスタムテンプレートの使用
                message = custom_template.format(
                    stockCode=stock_code,
                    stockName=stock_name,
                    logicType=logic_type,
                    price=price,
                    changeRate=change_rate,
                    volume=volume,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            else:
                # 標準フォーマット
                if format_type == "compact":
                    message = f"🎯 **{logic_type}検出**: {stock_name}({stock_code}) ¥{price:,.0f} ({change_rate:+.1f}%)"
                elif format_type == "detailed":
                    message = f"""
🎯 **Stock Harvest AI - {logic_type}検出**

**銘柄情報**
• 銘柄名: {stock_name}
• 銘柄コード: {stock_code}
• 現在価格: ¥{price:,.0f}
• 変動率: {change_rate:+.1f}%
• 出来高: {volume:,}

**検出時刻**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Stock Harvest AIが自動検出しました*
                    """.strip()
                else:  # standard
                    emoji = "🚀" if change_rate > 0 else "📉"
                    message = f"""
{emoji} **{logic_type}検出** - {stock_name}

**{stock_code}** | ¥{price:,.0f} ({change_rate:+.1f}%)
出来高: {volume:,}

{datetime.now().strftime('%H:%M')} | Stock Harvest AI
                    """.strip()
            
            return DiscordNotificationValidator.sanitize_message_content(message)
            
        except Exception as e:
            logger.error(f'Discord通知メッセージフォーマットエラー: {e}')
            # フォールバック用シンプルメッセージ
            return f"🎯 {logic_type}検出: {stock_name}({stock_code}) ¥{price:,.0f}"


class DiscordRateLimitValidator:
    """Discord レート制限バリデーター"""
    
    @staticmethod
    def check_rate_limit(
        current_count: int,
        hourly_limit: int,
        daily_count: int = 0,
        daily_limit: int = 1440
    ) -> Dict[str, Any]:
        """
        レート制限チェック
        
        Args:
            current_count: 現在の時間内送信数
            hourly_limit: 時間制限
            daily_count: 本日の送信数
            daily_limit: 日次制限
            
        Returns:
            Dict: レート制限結果
        """
        result = {
            'allowed': True,
            'reason': None,
            'remainingHourly': hourly_limit - current_count,
            'remainingDaily': daily_limit - daily_count
        }
        
        if current_count >= hourly_limit:
            result['allowed'] = False
            result['reason'] = f'時間あたり送信制限に達しました ({current_count}/{hourly_limit})'
        elif daily_count >= daily_limit:
            result['allowed'] = False
            result['reason'] = f'1日あたり送信制限に達しました ({daily_count}/{daily_limit})'
        
        return result