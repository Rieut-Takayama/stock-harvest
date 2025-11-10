"""
アラート管理 Service層
ビジネスロジック・バリデーション・外部API連携
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..repositories.alerts_repository import AlertsRepository, LineNotificationRepository


class AlertsService:
    """アラート管理サービス"""
    
    VALID_ALERT_TYPES = ["price", "logic"]
    VALID_LOGIC_TYPES = ["logic_a", "logic_b"]
    VALID_PRICE_OPERATORS = [">=", "<=", "="]
    
    @staticmethod
    def _validate_stock_code(stock_code: str) -> bool:
        """銘柄コードの形式チェック"""
        if not stock_code or not isinstance(stock_code, str):
            return False
        
        # 日本株式銘柄コード: 4桁の数字
        return bool(re.match(r'^\d{4}$', stock_code))
    
    @staticmethod
    def _validate_alert_request(alert_data: Dict[str, Any]) -> tuple[bool, str]:
        """アラート作成リクエストのバリデーション"""
        # 必須フィールドチェック
        required_fields = ["type", "stockCode"]
        for field in required_fields:
            if field not in alert_data or not alert_data[field]:
                return False, f"Required field '{field}' is missing"
        
        # アラートタイプチェック
        if alert_data["type"] not in AlertsService.VALID_ALERT_TYPES:
            return False, f"Invalid alert type. Must be one of {AlertsService.VALID_ALERT_TYPES}"
        
        # 銘柄コードチェック
        if not AlertsService._validate_stock_code(alert_data["stockCode"]):
            return False, "Invalid stock code format. Must be 4-digit number"
        
        # 価格アラートの場合の特別なバリデーション
        if alert_data["type"] == "price":
            if "condition" not in alert_data:
                return False, "Price alert requires 'condition' field"
            
            condition = alert_data["condition"]
            if not isinstance(condition, dict):
                return False, "Condition must be an object"
            
            # 価格条件の詳細チェック
            if "value" not in condition or not isinstance(condition["value"], (int, float)):
                return False, "Price condition requires numeric 'value' field"
            
            if condition["value"] <= 0:
                return False, "Target price must be greater than 0"
            
            if "operator" not in condition:
                condition["operator"] = ">="  # デフォルト値
            
            if condition["operator"] not in AlertsService.VALID_PRICE_OPERATORS:
                return False, f"Invalid price operator. Must be one of {AlertsService.VALID_PRICE_OPERATORS}"
        
        # ロジックアラートの場合の特別なバリデーション
        elif alert_data["type"] == "logic":
            if "condition" not in alert_data:
                return False, "Logic alert requires 'condition' field"
            
            condition = alert_data["condition"]
            if not isinstance(condition, dict):
                return False, "Condition must be an object"
            
            if "logicType" not in condition:
                return False, "Logic condition requires 'logicType' field"
            
            if condition["logicType"] not in AlertsService.VALID_LOGIC_TYPES:
                return False, f"Invalid logic type. Must be one of {AlertsService.VALID_LOGIC_TYPES}"
        
        return True, "Valid"
    
    @staticmethod
    def _get_stock_name_from_code(stock_code: str) -> str:
        """銘柄コードから銘柄名を取得（モック実装）"""
        # 実際の実装では株価API等から銘柄名を取得
        stock_names = {
            "7203": "トヨタ自動車",
            "9984": "ソフトバンクグループ",
            "6758": "ソニーグループ",
            "8306": "三菱UFJフィナンシャルG",
            "4502": "武田薬品工業"
        }
        
        return stock_names.get(stock_code, f"銘柄{stock_code}")
    
    @staticmethod
    async def get_all_alerts() -> List[Dict[str, Any]]:
        """全アラート取得"""
        try:
            alerts = await AlertsRepository.get_all_alerts()
            return alerts
        except Exception as e:
            print(f"❌ AlertsService.get_all_alerts error: {e}")
            return []
    
    @staticmethod
    async def create_alert(alert_data: Dict[str, Any]) -> tuple[Optional[Dict[str, Any]], str]:
        """アラート作成"""
        try:
            # バリデーション
            is_valid, validation_message = AlertsService._validate_alert_request(alert_data)
            if not is_valid:
                return None, validation_message
            
            # 銘柄名を取得
            stock_name = AlertsService._get_stock_name_from_code(alert_data["stockCode"])
            
            # Repository用のデータを準備
            repository_data = {
                "stock_code": alert_data["stockCode"],
                "stock_name": stock_name,
                "type": alert_data["type"],
                "condition": json.dumps(alert_data["condition"]),  # JSONシリアライズ
                "is_active": True,
                "line_notification_enabled": True
            }
            
            # アラート作成
            created_alert = await AlertsRepository.create_alert(repository_data)
            
            if created_alert:
                return created_alert, "Alert created successfully"
            else:
                return None, "Failed to create alert"
                
        except Exception as e:
            print(f"❌ AlertsService.create_alert error: {e}")
            return None, f"Internal server error: {str(e)}"
    
    @staticmethod
    async def toggle_alert(alert_id: str) -> tuple[Optional[Dict[str, Any]], str]:
        """アラート状態切替"""
        try:
            if not alert_id:
                return None, "Alert ID is required"
            
            updated_alert = await AlertsRepository.toggle_alert_status(alert_id)
            
            if updated_alert:
                status = "activated" if updated_alert["isActive"] else "deactivated"
                return updated_alert, f"Alert {status} successfully"
            else:
                return None, "Alert not found"
                
        except Exception as e:
            print(f"❌ AlertsService.toggle_alert error: {e}")
            return None, f"Internal server error: {str(e)}"
    
    @staticmethod
    async def delete_alert(alert_id: str) -> tuple[bool, str]:
        """アラート削除"""
        try:
            if not alert_id:
                return False, "Alert ID is required"
            
            deleted = await AlertsRepository.delete_alert(alert_id)
            
            if deleted:
                return True, "Alert deleted successfully"
            else:
                return False, "Alert not found"
                
        except Exception as e:
            print(f"❌ AlertsService.delete_alert error: {e}")
            return False, f"Internal server error: {str(e)}"


class LineNotificationService:
    """LINE通知サービス"""
    
    @staticmethod
    def _validate_line_config_request(config_data: Dict[str, Any]) -> tuple[bool, str]:
        """LINE設定更新リクエストのバリデーション"""
        if not config_data:
            return False, "Request body is required"
        
        # トークンが指定されている場合の形式チェック
        if "token" in config_data:
            token = config_data["token"]
            if token and not isinstance(token, str):
                return False, "Token must be a string"
            
            if token and len(token) < 10:
                return False, "Token appears to be too short"
        
        # 接続状態が指定されている場合の形式チェック
        if "isConnected" in config_data:
            if not isinstance(config_data["isConnected"], bool):
                return False, "isConnected must be a boolean"
        
        return True, "Valid"
    
    @staticmethod
    async def get_line_config() -> Optional[Dict[str, Any]]:
        """LINE通知設定取得"""
        try:
            config = await LineNotificationRepository.get_line_config()
            return config
        except Exception as e:
            print(f"❌ LineNotificationService.get_line_config error: {e}")
            return None
    
    @staticmethod
    async def update_line_config(config_data: Dict[str, Any]) -> tuple[Optional[Dict[str, Any]], str]:
        """LINE通知設定更新"""
        try:
            # バリデーション
            is_valid, validation_message = LineNotificationService._validate_line_config_request(config_data)
            if not is_valid:
                return None, validation_message
            
            # Repository用データに変換
            repository_data = {}
            
            if "token" in config_data:
                repository_data["token"] = config_data["token"]
            
            if "isConnected" in config_data:
                repository_data["is_connected"] = config_data["isConnected"]
            
            # 設定更新
            updated_config = await LineNotificationRepository.update_line_config(repository_data)
            
            if updated_config:
                return updated_config, "LINE notification config updated successfully"
            else:
                return None, "Failed to update LINE notification config"
                
        except Exception as e:
            print(f"❌ LineNotificationService.update_line_config error: {e}")
            return None, f"Internal server error: {str(e)}"
    
    @staticmethod
    async def test_line_connection(token: str) -> tuple[bool, str]:
        """LINE接続テスト（モック実装）"""
        try:
            # 実際の実装では LINE Notify APIに接続テストを実行
            if not token or len(token) < 10:
                return False, "Invalid token format"
            
            # モック: 特定のトークンでエラーをシミュレート
            if "invalid" in token.lower():
                await LineNotificationRepository.record_notification_error("Invalid token provided")
                return False, "Token validation failed"
            
            # モック成功ケース
            await LineNotificationRepository.increment_notification_count()
            return True, "Connection test successful"
            
        except Exception as e:
            print(f"❌ LineNotificationService.test_line_connection error: {e}")
            await LineNotificationRepository.record_notification_error(str(e))
            return False, f"Connection test failed: {str(e)}"