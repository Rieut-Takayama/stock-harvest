"""
システム関連のリポジトリ層
データベースアクセスを担当
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..database.config import database
from ..lib.logger import logger, track_performance

class SystemRepository:
    
    async def get_system_info(self) -> Optional[Dict[str, Any]]:
        """
        システム情報を取得
        """
        with track_performance("get_system_info_query"):
            try:
                logger.info("システム情報取得開始")
                
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
                        "lastScanAt": result["last_scan_at"] if result["last_scan_at"] else "未実行",
                        "activeAlerts": result["active_alerts"],
                        "totalUsers": result["total_users"],
                        "databaseStatus": result["database_status"],
                        "lastUpdated": result["last_updated"],
                        "statusDisplay": result["status_display"]
                    }
                    logger.info("システム情報取得成功", {
                        "version": system_info["version"],
                        "status": system_info["status"],
                        "record_id": result["id"]
                    })
                    return system_info
                else:
                    logger.warning("システム情報レコードが見つかりません")
                    return None
                    
            except Exception as e:
                logger.error("システム情報取得エラー", {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "query": "system_info table fetch"
                })
                raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        システムヘルスチェック
        """
        with track_performance("get_health_status_check"):
            try:
                logger.info("ヘルスチェック開始")
                
                # データベース接続確認（レスポンス時間計測付き）
                with track_performance("db_health_check") as db_tracker:
                    db_check = await database.fetch_one("SELECT 1 as status")
                    db_healthy = db_check is not None
                    db_response_time = db_tracker.end()
                
                # システム情報の取得を試行（レスポンス時間計測付き）
                with track_performance("system_data_check") as sys_tracker:
                    system_check = await self.get_system_info()
                    system_healthy = system_check is not None
                    sys_response_time = sys_tracker.end()
                
                overall_healthy = db_healthy and system_healthy
                
                health_status = {
                    "healthy": overall_healthy,
                    "checks": {
                        "database": {
                            "status": "pass" if db_healthy else "fail",
                            "message": "データベース接続正常" if db_healthy else "データベース接続失敗",
                            "response_time": db_response_time
                        },
                        "system_data": {
                            "status": "pass" if system_healthy else "fail", 
                            "message": "システムデータ取得正常" if system_healthy else "システムデータ取得失敗",
                            "response_time": sys_response_time
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "status": "healthy" if overall_healthy else "unhealthy"
                }
                
                logger.info("ヘルスチェック完了", {
                    "status": health_status["status"],
                    "healthy": overall_healthy,
                    "checks_count": len(health_status["checks"]),
                    "total_response_time": db_response_time + sys_response_time
                })
                return health_status
                
            except Exception as e:
                logger.error("ヘルスチェックエラー", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                return {
                    "healthy": False,
                    "checks": {
                        "database": {
                            "status": "fail",
                            "message": f"エラー: {str(e)}",
                            "response_time": 0.0
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
        with track_performance("update_system_status_query"):
            try:
                logger.info("システムステータス更新", {
                    "new_status": status,
                    "new_display": status_display
                })
                
                query = """
                UPDATE system_info 
                SET status = :status, status_display = :status_display, last_updated = NOW()
                WHERE id = 1
                """
                
                await database.execute(
                    query, 
                    {"status": status, "status_display": status_display}
                )
                
                logger.info("システムステータス更新完了", {
                    "status": status,
                    "status_display": status_display
                })
                return True
                
            except Exception as e:
                logger.error("システムステータス更新エラー", {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "attempted_status": status,
                    "attempted_display": status_display
                })
                raise