"""
システム関連のサービス層
ビジネスロジックを担当
"""

from typing import Dict, Any
import logging
from ..repositories.system_repository import SystemRepository

logger = logging.getLogger(__name__)

class SystemService:
    
    def __init__(self):
        self.system_repo = SystemRepository()
    
    async def get_system_information(self) -> Dict[str, Any]:
        """
        システム情報を取得（ビジネスロジック付き）
        """
        try:
            logger.info("🔍 システム情報サービス開始")
            
            # リポジトリからシステム情報を取得
            system_info = await self.system_repo.get_system_info()
            
            if not system_info:
                # デフォルトのシステム情報を返す
                logger.warning("⚠️ システム情報が見つからないため、デフォルト値を使用")
                system_info = {
                    "version": "v1.0.0",
                    "status": "healthy",
                    "lastScanAt": "未実行",
                    "activeAlerts": 0,
                    "totalUsers": 0,
                    "databaseStatus": "connected",
                    "lastUpdated": "2025-11-08T00:00:00Z",
                    "statusDisplay": "正常稼働中"
                }
            
            # ステータス表示の調整
            if system_info["status"] == "healthy":
                system_info["statusDisplay"] = "正常稼働中"
            elif system_info["status"] == "degraded":
                system_info["statusDisplay"] = "一部機能制限中"
            elif system_info["status"] == "down":
                system_info["statusDisplay"] = "メンテナンス中"
            
            logger.info(f"✅ システム情報取得完了: {system_info['version']}")
            return system_info
            
        except Exception as e:
            logger.error(f"❌ システム情報サービスエラー: {e}")
            raise
    
    async def get_health_check(self) -> Dict[str, Any]:
        """
        ヘルスチェック（ビジネスロジック付き）
        """
        try:
            logger.info("🏥 ヘルスチェックサービス開始")
            
            # ヘルスチェック実行
            health_status = await self.system_repo.get_health_status()
            
            # 健全性に基づくレスポンス調整
            if health_status["healthy"]:
                health_status["message"] = "すべてのサービスが正常に動作しています"
                health_status["severity"] = "info"
            else:
                health_status["message"] = "一部のサービスに問題があります"
                health_status["severity"] = "warning"
            
            logger.info(f"✅ ヘルスチェック完了: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"❌ ヘルスチェックサービスエラー: {e}")
            # エラーでもヘルスチェック結果を返す
            return {
                "healthy": False,
                "status": "unhealthy",
                "message": f"ヘルスチェック実行エラー: {str(e)}",
                "severity": "error",
                "checks": {},
                "error": str(e)
            }
    
    async def update_system_health(self, status: str, message: str = None) -> bool:
        """
        システムヘルス状態を更新
        """
        try:
            logger.info(f"🔄 システムヘルス更新: {status}")
            
            # メッセージの自動生成
            if not message:
                status_messages = {
                    "healthy": "正常稼働中",
                    "degraded": "一部機能制限中", 
                    "down": "メンテナンス中"
                }
                message = status_messages.get(status, "ステータス不明")
            
            # リポジトリ経由で更新
            result = await self.system_repo.update_system_status(status, message)
            
            logger.info("✅ システムヘルス更新完了")
            return result
            
        except Exception as e:
            logger.error(f"❌ システムヘルス更新エラー: {e}")
            raise