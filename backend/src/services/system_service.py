"""
システム関連のサービス層
ビジネスロジックを担当
"""

from typing import Dict, Any
from ..lib.logger import logger, track_performance
from ..repositories.system_repository import SystemRepository

class SystemService:
    
    def __init__(self):
        self.system_repo = SystemRepository()
    
    async def get_system_information(self) -> Dict[str, Any]:
        """
        システム情報を取得（ビジネスロジック付き、API仕様書準拠）
        """
        with track_performance("get_system_information_service"):
            try:
                logger.info("システム情報サービス開始")

                # リポジトリからシステム情報を取得
                system_info = await self.system_repo.get_system_info()

                if not system_info:
                    # デフォルトのシステム情報を返す（API仕様書準拠）
                    logger.warning("システム情報が見つからないため、デフォルト値を使用")
                    from datetime import datetime
                    system_info = {
                        "version": "v1.0.0",
                        "lastUpdated": datetime.now().isoformat() + "Z",
                        "status": "operational",
                        "statusDisplay": "正常稼働中"
                    }

                # ステータス表示の調整（ビジネスロジック）
                system_info = self._apply_status_display_logic(system_info)

                logger.info("システム情報取得完了", {
                    "version": system_info.get("version"),
                    "status": system_info.get("status")
                })
                return system_info

            except Exception as e:
                logger.error("システム情報サービスエラー", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                raise
    
    async def get_health_check(self) -> Dict[str, Any]:
        """
        ヘルスチェック（ビジネスロジック付き）
        """
        with track_performance("health_check_service"):
            try:
                logger.info("ヘルスチェックサービス開始")
                
                # ヘルスチェック実行
                health_status = await self.system_repo.get_health_status()
                
                # 健全性に基づくレスポンス調整（ビジネスロジック）
                health_status = self._apply_health_check_logic(health_status)
                
                logger.info("ヘルスチェック完了", {
                    "healthy": health_status.get("healthy"),
                    "status": health_status.get("status"),
                    "checks_passed": sum(1 for check in health_status.get("checks", {}).values() if check.get("status") == "pass")
                })
                return health_status
                
            except Exception as e:
                logger.error("ヘルスチェックサービスエラー", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                
                # エラーでもヘルスチェック結果を返す
                from datetime import datetime
                return {
                    "healthy": False,
                    "status": "unhealthy",
                    "message": f"ヘルスチェック実行エラー: {str(e)}",
                    "severity": "error",
                    "checks": {},
                    "timestamp": datetime.now().isoformat(),
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
            logger.error("システムヘルス更新エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def _apply_status_display_logic(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        ステータス表示のビジネスロジックを適用（API仕様書準拠）
        """
        status = system_info.get("status", "unknown")

        # API仕様書: operational, degraded, down
        status_mappings = {
            "operational": "正常稼働中",
            "degraded": "一部機能制限中",
            "down": "メンテナンス中"
        }

        # デフォルトのステータス表示が設定されていない場合は自動設定
        if not system_info.get("statusDisplay"):
            system_info["statusDisplay"] = status_mappings.get(status, "ステータス不明")

        return system_info
    
    def _apply_health_check_logic(self, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        ヘルスチェックのビジネスロジックを適用
        """
        is_healthy = health_status.get("healthy", False)
        
        # メッセージとセベリティの自動設定
        if is_healthy:
            health_status["message"] = health_status.get("message", "すべてのサービスが正常に動作しています")
            health_status["severity"] = "info"
        else:
            health_status["message"] = health_status.get("message", "一部のサービスに問題があります")
            health_status["severity"] = "warning"
        
        # チェック項目にレスポンス時間情報を追加（パフォーマンス分析用）
        checks = health_status.get("checks", {})
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict) and "response_time" not in check_data:
                # デフォルトのレスポンス時間を設定（実測値がない場合）
                check_data["response_time"] = 0.0
        
        return health_status