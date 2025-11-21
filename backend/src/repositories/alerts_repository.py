"""
アラート管理 Repository層
アラート・LINE通知の CRUD 操作
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database.config import database
from ..database.tables import alerts, line_notification_config


class AlertsRepository:
    """アラート管理リポジトリ"""
    
    @staticmethod
    def _generate_alert_id() -> str:
        """アラートID生成"""
        return f"alert-{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def _row_to_alert(row) -> Dict[str, Any]:
        """データベース行をAlertオブジェクトに変換"""
        if not row:
            return None
        
        return {
            "id": row["id"],
            "stockCode": row["stock_code"],
            "stockName": row["stock_name"],
            "type": row["type"],
            "condition": row["condition"],
            "isActive": row["is_active"],
            "lineNotificationEnabled": row["line_notification_enabled"],
            "createdAt": row["created_at"].isoformat() if row["created_at"] else None
        }
    
    @staticmethod
    async def get_all_alerts() -> List[Dict[str, Any]]:
        """全アラート取得"""
        try:
            query = """
            SELECT id, stock_code, stock_name, type, condition, is_active, 
                   line_notification_enabled, created_at, triggered_count, last_triggered_at
            FROM alerts 
            ORDER BY created_at DESC
            """
            rows = await database.fetch_all(query)
            
            return [AlertsRepository._row_to_alert(row) for row in rows]
        
        except Exception as e:
            # Repository alert fetch error
            return []
    
    @staticmethod
    async def get_alert_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
        """指定IDのアラート取得"""
        try:
            query = """
            SELECT id, stock_code, stock_name, type, condition, is_active, 
                   line_notification_enabled, created_at, triggered_count, last_triggered_at
            FROM alerts 
            WHERE id = :id
            """
            row = await database.fetch_one(query, {"id": alert_id})
            
            return AlertsRepository._row_to_alert(row)
        
        except Exception as e:
            # Repository alert fetch by id error
            return None
    
    @staticmethod
    async def create_alert(alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """アラート作成"""
        try:
            alert_id = AlertsRepository._generate_alert_id()
            
            query = """
            INSERT INTO alerts (id, stock_code, stock_name, type, condition, is_active, line_notification_enabled)
            VALUES (:id, :stock_code, :stock_name, :type, :condition, :is_active, :line_notification_enabled)
            """
            
            await database.execute(query, {
                "id": alert_id,
                "stock_code": alert_data["stock_code"],
                "stock_name": alert_data.get("stock_name", ""),
                "type": alert_data["type"],
                "condition": alert_data["condition"],
                "is_active": alert_data.get("is_active", True),
                "line_notification_enabled": alert_data.get("line_notification_enabled", True)
            })
            
            # 作成されたアラートを返却
            return await AlertsRepository.get_alert_by_id(alert_id)
        
        except Exception as e:
            # Repository alert creation error
            return None
    
    @staticmethod
    async def toggle_alert_status(alert_id: str) -> Optional[Dict[str, Any]]:
        """アラート有効/無効切替"""
        try:
            # 現在の状態を取得
            current_alert = await AlertsRepository.get_alert_by_id(alert_id)
            if not current_alert:
                return None
            
            # 状態を反転
            new_status = not current_alert["isActive"]
            
            query = """
            UPDATE alerts 
            SET is_active = :is_active, updated_at = NOW()
            WHERE id = :id
            """
            
            await database.execute(query, {
                "id": alert_id,
                "is_active": new_status
            })
            
            # 更新されたアラートを返却
            return await AlertsRepository.get_alert_by_id(alert_id)
        
        except Exception as e:
            # Repository alert toggle error
            return None
    
    @staticmethod
    async def delete_alert(alert_id: str) -> bool:
        """アラート削除"""
        try:
            # アラートが存在するかチェック
            existing_alert = await AlertsRepository.get_alert_by_id(alert_id)
            if not existing_alert:
                return False
            
            query = "DELETE FROM alerts WHERE id = :id"
            await database.execute(query, {"id": alert_id})
            
            return True
        
        except Exception as e:
            # Repository alert deletion error
            return False


class LineNotificationRepository:
    """LINE通知設定リポジトリ"""
    
    @staticmethod
    def _row_to_line_config(row) -> Dict[str, Any]:
        """データベース行をLineNotificationConfigに変換"""
        if not row:
            return None
        
        return {
            "isConnected": row["is_connected"],
            "token": "***masked***" if row["token"] else None,  # トークンはマスク
            "status": row["status"],
            "lastNotificationAt": row["last_notification_at"].isoformat() if row["last_notification_at"] else None
        }
    
    @staticmethod
    async def get_line_config() -> Optional[Dict[str, Any]]:
        """LINE通知設定取得"""
        try:
            query = """
            SELECT is_connected, token, status, last_notification_at, 
                   notification_count, error_count
            FROM line_notification_config 
            WHERE id = 1
            """
            row = await database.fetch_one(query)
            
            return LineNotificationRepository._row_to_line_config(row)
        
        except Exception as e:
            # Repository LINE config fetch error
            return None
    
    @staticmethod
    async def update_line_config(config_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """LINE通知設定更新"""
        try:
            # 更新可能フィールドを特定
            update_fields = []
            params = {"id": 1}
            
            # フィールドの重複を避けて処理
            is_connected_set = False
            status_set = False
            
            if "token" in config_data and config_data["token"]:
                update_fields.append("token = :token")
                params["token"] = config_data["token"]
                # トークンが設定されたら接続状態にする
                if not is_connected_set:
                    update_fields.append("is_connected = :is_connected_token")
                    params["is_connected_token"] = True
                    is_connected_set = True
                if not status_set:
                    update_fields.append("status = :status_token")
                    params["status_token"] = "connected"
                    status_set = True
            
            if "is_connected" in config_data and not is_connected_set:
                update_fields.append("is_connected = :is_connected")
                params["is_connected"] = config_data["is_connected"]
                
                # 非接続にする場合はステータスも更新
                if not config_data["is_connected"] and not status_set:
                    update_fields.append("status = :status")
                    params["status"] = "disconnected"
            
            if not update_fields:
                # 更新するフィールドがない場合は現在の設定を返却
                return await LineNotificationRepository.get_line_config()
            
            # updated_at を追加
            update_fields.append("updated_at = NOW()")
            
            query = f"""
            UPDATE line_notification_config 
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            await database.execute(query, params)
            
            # 更新された設定を返却
            return await LineNotificationRepository.get_line_config()
        
        except Exception as e:
            # Repository LINE config update error
            return None
    
    @staticmethod
    async def increment_notification_count() -> bool:
        """通知送信回数を増やす"""
        try:
            query = """
            UPDATE line_notification_config 
            SET notification_count = notification_count + 1,
                last_notification_at = NOW(),
                updated_at = NOW()
            WHERE id = 1
            """
            await database.execute(query)
            return True
        
        except Exception as e:
            # Repository notification count error
            return False
    
    @staticmethod
    async def record_notification_error(error_message: str) -> bool:
        """通知エラーを記録"""
        try:
            query = """
            UPDATE line_notification_config 
            SET error_count = error_count + 1,
                last_error_message = :error_message,
                status = :status,
                updated_at = NOW()
            WHERE id = 1
            """
            await database.execute(query, {
                "error_message": error_message,
                "status": "error"
            })
            return True
        
        except Exception as e:
            # Repository notification error record failed
            return False