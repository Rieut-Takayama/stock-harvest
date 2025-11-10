"""
システム関連のリポジトリ層
データベースアクセスを担当
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..database.config import database
import logging

logger = logging.getLogger(__name__)

class SystemRepository:
    
    async def get_system_info(self) -> Optional[Dict[str, Any]]:
        """
        システム情報を取得
        """
        try:
            logger.info("📊 システム情報取得開始")
            
            query = """
            SELECT id, version, status, last_scan_at, active_alerts, 
                   total_users, database_status, last_updated, status_display
            FROM system_info 
            WHERE id = 1
            """
            
            result = await database.fetch_one(query)
            
            if result:
                system_info = {
                    "version": result["version"],
                    "status": result["status"],
                    "lastScanAt": result["last_scan_at"].isoformat() if result["last_scan_at"] else "未実行",
                    "activeAlerts": result["active_alerts"],
                    "totalUsers": result["total_users"],
                    "databaseStatus": result["database_status"],
                    "lastUpdated": result["last_updated"].isoformat(),
                    "statusDisplay": result["status_display"]
                }
                logger.info(f"✅ システム情報取得成功: {system_info['version']}")
                return system_info
            else:
                logger.warning("⚠️ システム情報レコードが見つかりません")
                return None
                
        except Exception as e:
            logger.error(f"❌ システム情報取得エラー: {e}")
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        システムヘルスチェック
        """
        try:
            logger.info("🏥 ヘルスチェック開始")
            
            # データベース接続確認
            db_check = await database.fetch_one("SELECT 1 as status")
            db_healthy = db_check is not None
            
            # システム情報の取得を試行
            system_check = await self.get_system_info()
            system_healthy = system_check is not None
            
            overall_healthy = db_healthy and system_healthy
            
            health_status = {
                "healthy": overall_healthy,
                "checks": {
                    "database": {
                        "status": "pass" if db_healthy else "fail",
                        "message": "データベース接続正常" if db_healthy else "データベース接続失敗"
                    },
                    "system_data": {
                        "status": "pass" if system_healthy else "fail", 
                        "message": "システムデータ取得正常" if system_healthy else "システムデータ取得失敗"
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "status": "healthy" if overall_healthy else "unhealthy"
            }
            
            logger.info(f"✅ ヘルスチェック完了: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"❌ ヘルスチェックエラー: {e}")
            return {
                "healthy": False,
                "checks": {
                    "database": {
                        "status": "fail",
                        "message": f"エラー: {str(e)}"
                    }
                },
                "timestamp": datetime.now().isoformat(),
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def update_system_status(self, status: str, status_display: str) -> bool:
        """
        システムステータスを更新
        """
        try:
            logger.info(f"🔄 システムステータス更新: {status}")
            
            query = """
            UPDATE system_info 
            SET status = :status, status_display = :status_display, last_updated = NOW()
            WHERE id = 1
            """
            
            await database.execute(
                query, 
                {"status": status, "status_display": status_display}
            )
            
            logger.info("✅ システムステータス更新完了")
            return True
            
        except Exception as e:
            logger.error(f"❌ システムステータス更新エラー: {e}")
            raise