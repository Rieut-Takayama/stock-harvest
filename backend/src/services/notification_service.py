"""
通知サービス - LINE Notify連携
Stock Harvest AI用通知システム

機能:
- LINE Notify送信
- 通知テンプレート管理
- 送信履歴記録
- エラーハンドリング
- レート制限対応
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from urllib.parse import quote

from ..repositories.alerts_repository import AlertsRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """通知サービス"""
    
    def __init__(self):
        self.line_notify_url = "https://notify-api.line.me/api/notify"
        self.line_token = os.getenv('LINE_NOTIFY_TOKEN', '')
        self.alerts_repo = AlertsRepository()
        
        # レート制限設定
        self.rate_limit = {
            'max_requests_per_hour': 1000,  # LINE Notify制限
            'requests_sent': 0,
            'last_reset': datetime.now()
        }
        
        # 通知テンプレート
        self.templates = {
            'signal_alert': "🚨 売買シグナル発生\n\n📊 {stock_name} ({stock_code})\n💰 現在価格: ¥{price:,.0f}\n📈 シグナル: {action}\n🎯 強度: {strength}%\n⭐ 信頼度: {confidence:.1%}\n\n💡 {recommendation}\n\n⏰ {timestamp}",
            'price_alert': "📈 価格アラート\n\n📊 {stock_name} ({stock_code})\n💰 現在価格: ¥{price:,.0f}\n📊 変動: {change:+.0f}円 ({change_rate:+.1f}%)\n🎯 条件: {condition}\n\n⏰ {timestamp}",
            'logic_alert': "🎯 ロジック検出アラート\n\n📊 {stock_name} ({stock_code})\n🔍 検出ロジック: {logic_type}\n💰 現在価格: ¥{price:,.0f}\n📈 変動率: {change_rate:+.1f}%\n📊 出来高: {volume:,}\n\n💡 {details}\n\n⏰ {timestamp}",
            'performance_summary': "📊 デイリーパフォーマンス\n\n📅 日付: {date}\n🎯 総シグナル: {total_signals}件\n📈 勝率: {win_rate:.1f}%\n💰 損益: ¥{profit_loss:+,.0f}\n📊 PF: {profit_factor:.2f}\n\n⏰ {timestamp}",
            'error_alert': "⚠️ システムエラー\n\n🔴 エラー種別: {error_type}\n📝 詳細: {error_message}\n⏰ 発生時刻: {timestamp}",
            'system_status': "🔔 システム状況\n\n🟢 ステータス: {status}\n📊 アクティブアラート: {active_alerts}件\n👥 ユーザー数: {total_users}\n💾 DB状態: {database_status}\n\n⏰ {timestamp}"
        }
    
    async def send_signal_alert(self, signal_data: Dict, alert_settings: Dict = None) -> bool:
        """
        売買シグナルアラート送信
        """
        try:
            # レート制限チェック
            if not await self._check_rate_limit():
                logger.warning("レート制限により通知送信をスキップ")
                return False
            
            # メッセージ作成
            message = self._format_signal_message(signal_data)
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            if success:
                # 送信履歴記録
                await self._record_notification_history({
                    'type': 'signal_alert',
                    'stock_code': signal_data.get('stock_code', ''),
                    'message': message,
                    'status': 'sent'
                })
                logger.info(f"シグナルアラート送信完了: {signal_data.get('stock_code', '')}")
            else:
                # エラー記録
                await self._record_notification_history({
                    'type': 'signal_alert',
                    'stock_code': signal_data.get('stock_code', ''),
                    'message': message,
                    'status': 'failed'
                })
            
            return success
            
        except Exception as e:
            logger.error(f"シグナルアラート送信エラー: {str(e)}")
            return False
    
    async def send_price_alert(self, stock_data: Dict, alert_condition: Dict) -> bool:
        """
        価格アラート送信
        """
        try:
            # レート制限チェック
            if not await self._check_rate_limit():
                return False
            
            # メッセージ作成
            message = self._format_price_message(stock_data, alert_condition)
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            # 送信履歴記録
            await self._record_notification_history({
                'type': 'price_alert',
                'stock_code': stock_data.get('code', ''),
                'message': message,
                'status': 'sent' if success else 'failed'
            })
            
            return success
            
        except Exception as e:
            logger.error(f"価格アラート送信エラー: {str(e)}")
            return False
    
    async def send_logic_alert(self, stock_data: Dict, logic_result: Dict) -> bool:
        """
        ロジック検出アラート送信
        """
        try:
            # レート制限チェック
            if not await self._check_rate_limit():
                return False
            
            # メッセージ作成
            message = self._format_logic_message(stock_data, logic_result)
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            # 送信履歴記録
            await self._record_notification_history({
                'type': 'logic_alert',
                'stock_code': stock_data.get('code', ''),
                'message': message,
                'status': 'sent' if success else 'failed'
            })
            
            return success
            
        except Exception as e:
            logger.error(f"ロジック検出アラート送信エラー: {str(e)}")
            return False
    
    async def send_performance_summary(self, performance_data: Dict) -> bool:
        """
        パフォーマンスサマリー送信
        """
        try:
            # レート制限チェック
            if not await self._check_rate_limit():
                return False
            
            # メッセージ作成
            message = self._format_performance_message(performance_data)
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            # 送信履歴記録
            await self._record_notification_history({
                'type': 'performance_summary',
                'stock_code': '',
                'message': message,
                'status': 'sent' if success else 'failed'
            })
            
            return success
            
        except Exception as e:
            logger.error(f"パフォーマンスサマリー送信エラー: {str(e)}")
            return False
    
    async def send_error_alert(self, error_type: str, error_message: str) -> bool:
        """
        エラーアラート送信
        """
        try:
            # 重要なエラーのみ送信
            if not self._is_critical_error(error_type):
                return True
            
            # レート制限チェック（エラーは優先）
            if not await self._check_rate_limit(priority=True):
                return False
            
            # メッセージ作成
            message = self.templates['error_alert'].format(
                error_type=error_type,
                error_message=error_message[:100],  # メッセージを制限
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            return success
            
        except Exception as e:
            logger.error(f"エラーアラート送信エラー: {str(e)}")
            return False
    
    async def send_system_status(self, system_info: Dict) -> bool:
        """
        システム状況通知送信
        """
        try:
            # レート制限チェック
            if not await self._check_rate_limit():
                return False
            
            # メッセージ作成
            message = self.templates['system_status'].format(
                status=system_info.get('status_display', '不明'),
                active_alerts=system_info.get('active_alerts', 0),
                total_users=system_info.get('total_users', 0),
                database_status=system_info.get('database_status', '不明'),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # LINE Notify送信
            success = await self._send_line_notify(message)
            
            return success
            
        except Exception as e:
            logger.error(f"システム状況通知送信エラー: {str(e)}")
            return False
    
    async def _send_line_notify(self, message: str, image_file: str = None) -> bool:
        """
        LINE Notify API呼び出し
        """
        try:
            if not self.line_token:
                logger.warning("LINE Notifyトークンが設定されていません")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.line_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'message': message
            }
            
            # 画像添付（オプション）
            files = None
            if image_file and os.path.exists(image_file):
                files = {'imageFile': open(image_file, 'rb')}
            
            async with aiohttp.ClientSession() as session:
                if files:
                    # マルチパート形式で送信
                    data_form = aiohttp.FormData()
                    data_form.add_field('message', message)
                    data_form.add_field('imageFile', files['imageFile'])
                    
                    async with session.post(
                        self.line_notify_url,
                        headers={'Authorization': f'Bearer {self.line_token}'},
                        data=data_form,
                        timeout=30
                    ) as response:
                        result = response.status == 200
                else:
                    # 通常のフォーム送信
                    async with session.post(
                        self.line_notify_url,
                        headers=headers,
                        data=data,
                        timeout=30
                    ) as response:
                        result = response.status == 200
                
                if result:
                    self.rate_limit['requests_sent'] += 1
                    logger.debug("LINE Notify送信成功")
                else:
                    error_text = await response.text()
                    logger.warning(f"LINE Notify送信失敗: {response.status} - {error_text}")
                
                return result
                
        except Exception as e:
            logger.error(f"LINE Notify送信エラー: {str(e)}")
            return False
        finally:
            if files:
                for file in files.values():
                    if hasattr(file, 'close'):
                        file.close()
    
    def _format_signal_message(self, signal_data: Dict) -> str:
        """
        シグナルメッセージフォーマット
        """
        try:
            # 推奨事項生成
            recommendation = self._generate_signal_recommendation(signal_data)
            
            message = self.templates['signal_alert'].format(
                stock_name=signal_data.get('stock_name', ''),
                stock_code=signal_data.get('stock_code', ''),
                price=signal_data.get('current_price', 0),
                action=signal_data.get('action', ''),
                strength=signal_data.get('signal_strength', 0),
                confidence=signal_data.get('confidence', 0),
                recommendation=recommendation,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return message
            
        except Exception as e:
            logger.warning(f"シグナルメッセージフォーマットエラー: {str(e)}")
            return f"シグナル通知エラー: {str(e)}"
    
    def _format_price_message(self, stock_data: Dict, alert_condition: Dict) -> str:
        """
        価格アラートメッセージフォーマット
        """
        try:
            message = self.templates['price_alert'].format(
                stock_name=stock_data.get('name', ''),
                stock_code=stock_data.get('code', ''),
                price=stock_data.get('price', 0),
                change=stock_data.get('change', 0),
                change_rate=stock_data.get('changeRate', 0),
                condition=self._format_alert_condition(alert_condition),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return message
            
        except Exception as e:
            logger.warning(f"価格メッセージフォーマットエラー: {str(e)}")
            return f"価格アラート通知エラー: {str(e)}"
    
    def _format_logic_message(self, stock_data: Dict, logic_result: Dict) -> str:
        """
        ロジック検出メッセージフォーマット
        """
        try:
            logic_type_map = {
                'logic_a': 'ロジックA（ストップ高）',
                'logic_a_enhanced': 'ロジックA強化版',
                'logic_b': 'ロジックB（転換）'
            }
            
            logic_display = logic_type_map.get(
                logic_result.get('logic_type', ''), 
                '不明'
            )
            
            details = logic_result.get('details', '条件達成')
            if len(details) > 50:
                details = details[:50] + '...'
            
            message = self.templates['logic_alert'].format(
                stock_name=stock_data.get('name', ''),
                stock_code=stock_data.get('code', ''),
                logic_type=logic_display,
                price=stock_data.get('price', 0),
                change_rate=stock_data.get('changeRate', 0),
                volume=stock_data.get('volume', 0),
                details=details,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return message
            
        except Exception as e:
            logger.warning(f"ロジックメッセージフォーマットエラー: {str(e)}")
            return f"ロジック検出通知エラー: {str(e)}"
    
    def _format_performance_message(self, performance_data: Dict) -> str:
        """
        パフォーマンスメッセージフォーマット
        """
        try:
            message = self.templates['performance_summary'].format(
                date=performance_data.get('date', ''),
                total_signals=performance_data.get('total_signals', 0),
                win_rate=performance_data.get('win_rate', 0),
                profit_loss=performance_data.get('total_profit_loss', 0),
                profit_factor=performance_data.get('profit_factor', 0),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return message
            
        except Exception as e:
            logger.warning(f"パフォーマンスメッセージフォーマットエラー: {str(e)}")
            return f"パフォーマンス通知エラー: {str(e)}"
    
    def _generate_signal_recommendation(self, signal_data: Dict) -> str:
        """
        シグナル推奨事項生成
        """
        try:
            action = signal_data.get('action', '')
            strength = signal_data.get('signal_strength', 0)
            executable = signal_data.get('executable', False)
            
            if not executable:
                return "⚠️ リスク・リワード条件未達のため実行非推奨"
            
            if action == 'STRONG_BUY':
                return "🚀 強力な買いシグナル。エントリーを検討"
            elif action == 'BUY':
                return "📈 買いシグナル。適切なタイミングでエントリー"
            elif action == 'SELL':
                return "📉 売りシグナル。ポジション縮小を検討"
            elif action == 'STRONG_SELL':
                return "🔻 強力な売りシグナル。即座にポジション縮小"
            elif action == 'WATCH':
                return "👀 監視継続。条件改善を待つ"
            else:
                return "ℹ️ 詳細な分析が必要"
                
        except Exception:
            return "ℹ️ 推奨事項生成エラー"
    
    def _format_alert_condition(self, condition: Dict) -> str:
        """
        アラート条件フォーマット
        """
        try:
            condition_type = condition.get('type', '')
            
            if condition_type == 'price_above':
                return f"価格上抜け: ¥{condition.get('target_price', 0):,.0f}"
            elif condition_type == 'price_below':
                return f"価格下抜け: ¥{condition.get('target_price', 0):,.0f}"
            elif condition_type == 'change_rate_above':
                return f"変動率上抜け: {condition.get('target_rate', 0):+.1f}%"
            elif condition_type == 'volume_surge':
                return f"出来高急増: {condition.get('volume_ratio', 0):.1f}倍"
            else:
                return str(condition)
                
        except Exception:
            return "条件フォーマットエラー"
    
    def _is_critical_error(self, error_type: str) -> bool:
        """
        重要なエラーかどうか判定
        """
        critical_errors = {
            'database_connection',
            'api_service_down', 
            'authentication_failure',
            'data_corruption',
            'memory_exhaustion',
            'disk_full'
        }
        return error_type in critical_errors
    
    async def _check_rate_limit(self, priority: bool = False) -> bool:
        """
        レート制限チェック
        """
        try:
            current_time = datetime.now()
            
            # 1時間経過でリセット
            if current_time - self.rate_limit['last_reset'] >= timedelta(hours=1):
                self.rate_limit['requests_sent'] = 0
                self.rate_limit['last_reset'] = current_time
            
            # 優先度が高い場合は多少緩める
            max_requests = self.rate_limit['max_requests_per_hour']
            if priority:
                max_requests = int(max_requests * 1.1)  # 10%余裕
            
            return self.rate_limit['requests_sent'] < max_requests
            
        except Exception as e:
            logger.warning(f"レート制限チェックエラー: {str(e)}")
            return True  # エラー時は送信を許可
    
    async def _record_notification_history(self, notification_data: Dict) -> None:
        """
        通知履歴記録
        """
        try:
            # データベースに通知履歴を保存
            # 実装簡易版：ログ出力のみ
            logger.info(f"通知履歴: {notification_data}")
            
            # 必要に応じてalerts_repositoryに保存機能を追加
            
        except Exception as e:
            logger.warning(f"通知履歴記録エラー: {str(e)}")
    
    async def test_notification(self) -> bool:
        """
        通知テスト
        """
        try:
            test_message = f"🔔 Stock Harvest AI 通知テスト\n\n接続確認完了\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            success = await self._send_line_notify(test_message)
            
            if success:
                logger.info("通知テスト成功")
            else:
                logger.warning("通知テスト失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"通知テストエラー: {str(e)}")
            return False
    
    def get_notification_stats(self) -> Dict:
        """
        通知統計取得
        """
        try:
            return {
                'line_token_configured': bool(self.line_token),
                'requests_sent_this_hour': self.rate_limit['requests_sent'],
                'max_requests_per_hour': self.rate_limit['max_requests_per_hour'],
                'remaining_requests': max(0, self.rate_limit['max_requests_per_hour'] - self.rate_limit['requests_sent']),
                'rate_limit_reset_time': self.rate_limit['last_reset'].isoformat(),
                'available_templates': list(self.templates.keys())
            }
            
        except Exception as e:
            logger.warning(f"通知統計取得エラー: {str(e)}")
            return {'error': str(e)}