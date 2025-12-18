"""
Discord通知設定コントローラー
Stock Harvest AI - Discord通知機能
"""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..models.discord_models import (
    DiscordConfigCreateRequest,
    DiscordConfigUpdateRequest,
    DiscordNotificationMessage,
    NotificationFormat
)
from ..services.discord_service import DiscordNotificationService
from ..lib.logger import logger
from ..lib.logger import PerformanceTracker


class DiscordController:
    """Discord通知設定コントローラークラス"""
    
    def __init__(self, database_url: str):
        """
        コントローラーの初期化
        
        Args:
            database_url: データベース接続URL
        """
        self.discord_service = DiscordNotificationService(database_url)
        self.router = APIRouter()
        self._setup_routes()
        logger.info('DiscordController初期化完了')
    
    def _setup_routes(self):
        """ルート設定"""
        self.router.add_api_route(
            "/api/notifications/discord",
            self.get_discord_config,
            methods=["GET"],
            summary="Discord通知設定取得",
            description="現在のDiscord通知設定を取得します"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord",
            self.create_discord_config,
            methods=["POST"],
            summary="Discord通知設定作成",
            description="新しいDiscord通知設定を作成します"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord",
            self.update_discord_config,
            methods=["PUT"],
            summary="Discord通知設定更新",
            description="既存のDiscord通知設定を更新します"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord/test",
            self.test_discord_webhook,
            methods=["POST"],
            summary="Discord Webhook接続テスト",
            description="Discord Webhookの接続テストを実行します"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord/send",
            self.send_test_notification,
            methods=["POST"],
            summary="Discord テスト通知送信",
            description="Discord通知のテスト送信を行います"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord/stats",
            self.get_notification_stats,
            methods=["GET"],
            summary="Discord通知統計取得",
            description="Discord通知の送信統計を取得します"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord/enable",
            self.enable_notifications,
            methods=["POST"],
            summary="Discord通知有効化",
            description="Discord通知を有効にします"
        )
        
        self.router.add_api_route(
            "/api/notifications/discord/disable",
            self.disable_notifications,
            methods=["POST"],
            summary="Discord通知無効化",
            description="Discord通知を無効にします"
        )
    
    async def get_discord_config(self) -> JSONResponse:
        """Discord通知設定取得"""
        try:
            tracker = PerformanceTracker('Discord設定取得API')
            
            config = await self.discord_service.get_discord_config()
            
            if config:
                response_data = {
                    "success": True,
                    "data": {
                        "id": config.id,
                        "webhookUrl": config.webhookUrl,
                        "isEnabled": config.isEnabled,
                        "channelName": config.channelName,
                        "serverName": config.serverName,
                        "notificationTypes": config.notificationTypes,
                        "mentionRole": config.mentionRole,
                        "notificationFormat": config.notificationFormat.value,
                        "rateLimitPerHour": config.rateLimitPerHour,
                        "lastNotificationAt": config.lastNotificationAt.isoformat() if config.lastNotificationAt else None,
                        "notificationCountToday": config.notificationCountToday,
                        "totalNotificationsSent": config.totalNotificationsSent,
                        "errorCount": config.errorCount,
                        "lastErrorMessage": config.lastErrorMessage,
                        "lastErrorAt": config.lastErrorAt.isoformat() if config.lastErrorAt else None,
                        "connectionStatus": config.connectionStatus.value,
                        "webhookTestResult": config.webhookTestResult,
                        "customMessageTemplate": config.customMessageTemplate,
                        "createdAt": config.createdAt.isoformat() if config.createdAt else None,
                        "updatedAt": config.updatedAt.isoformat() if config.updatedAt else None
                    }
                }
            else:
                response_data = {
                    "success": True,
                    "data": None,
                    "message": "Discord通知設定が存在しません"
                }
            
            tracker.end({"設定存在": config is not None})
            logger.info(f'Discord設定取得API完了: 設定存在={config is not None}')
            
            return JSONResponse(
                content=response_data,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f'Discord設定取得APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Discord設定の取得に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def create_discord_config(self, request: DiscordConfigCreateRequest) -> JSONResponse:
        """Discord通知設定作成"""
        try:
            tracker = PerformanceTracker('Discord設定作成API')
            
            logger.info(f'Discord設定作成開始: チャンネル={request.channelName}')
            
            config = await self.discord_service.create_discord_config(request)
            
            response_data = {
                "success": True,
                "data": {
                    "id": config.id,
                    "webhookUrl": config.webhookUrl,
                    "isEnabled": config.isEnabled,
                    "channelName": config.channelName,
                    "serverName": config.serverName,
                    "notificationTypes": config.notificationTypes,
                    "mentionRole": config.mentionRole,
                    "notificationFormat": config.notificationFormat.value,
                    "connectionStatus": config.connectionStatus.value,
                    "createdAt": config.createdAt.isoformat() if config.createdAt else None
                },
                "message": "Discord通知設定を作成しました"
            }
            
            tracker.end({"作成成功": True, "チャンネル": request.channelName})
            logger.info(f'Discord設定作成API完了: ID={config.id}')
            
            return JSONResponse(
                content=response_data,
                status_code=status.HTTP_201_CREATED
            )
            
        except ValueError as ve:
            logger.warning(f'Discord設定作成バリデーションエラー: {ve}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": str(ve),
                    "error": "validation_error"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except ValidationError as ve:
            logger.warning(f'Discord設定作成リクエストエラー: {ve}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "リクエストデータが正しくありません",
                    "errors": [{"field": err["loc"][-1], "message": err["msg"]} for err in ve.errors()]
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            
        except Exception as e:
            logger.error(f'Discord設定作成APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Discord設定の作成に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def update_discord_config(self, request: DiscordConfigUpdateRequest) -> JSONResponse:
        """Discord通知設定更新"""
        try:
            tracker = PerformanceTracker('Discord設定更新API')
            
            logger.info('Discord設定更新開始')
            
            config = await self.discord_service.update_discord_config(request)
            
            response_data = {
                "success": True,
                "data": {
                    "id": config.id,
                    "webhookUrl": config.webhookUrl,
                    "isEnabled": config.isEnabled,
                    "channelName": config.channelName,
                    "serverName": config.serverName,
                    "notificationTypes": config.notificationTypes,
                    "mentionRole": config.mentionRole,
                    "notificationFormat": config.notificationFormat.value,
                    "connectionStatus": config.connectionStatus.value,
                    "updatedAt": config.updatedAt.isoformat() if config.updatedAt else None
                },
                "message": "Discord通知設定を更新しました"
            }
            
            tracker.end({"更新成功": True})
            logger.info(f'Discord設定更新API完了: ID={config.id}')
            
            return JSONResponse(
                content=response_data,
                status_code=status.HTTP_200_OK
            )
            
        except ValueError as ve:
            logger.warning(f'Discord設定更新バリデーションエラー: {ve}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": str(ve),
                    "error": "validation_error"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except ValidationError as ve:
            logger.warning(f'Discord設定更新リクエストエラー: {ve}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "リクエストデータが正しくありません",
                    "errors": [{"field": err["loc"][-1], "message": err["msg"]} for err in ve.errors()]
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            
        except Exception as e:
            logger.error(f'Discord設定更新APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Discord設定の更新に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def test_discord_webhook(
        self,
        request_data: Optional[Dict[str, str]] = Body(default=None)
    ) -> JSONResponse:
        """Discord Webhook接続テスト"""
        try:
            tracker = PerformanceTracker('Discord WebhookテストAPI')
            
            webhook_url = None
            if request_data and 'webhookUrl' in request_data:
                webhook_url = request_data['webhookUrl']
            
            logger.info(f'Discord Webhookテスト開始: URL指定={webhook_url is not None}')
            
            test_result = await self.discord_service.test_discord_webhook(webhook_url)
            
            response_data = {
                "success": test_result.success,
                "data": {
                    "testResult": {
                        "success": test_result.success,
                        "message": test_result.message,
                        "responseStatus": test_result.responseStatus,
                        "responseData": test_result.responseData,
                        "errorDetail": test_result.errorDetail,
                        "testedAt": test_result.testedAt.isoformat()
                    }
                },
                "message": test_result.message
            }
            
            status_code = status.HTTP_200_OK if test_result.success else status.HTTP_400_BAD_REQUEST
            
            tracker.end({"テスト成功": test_result.success})
            logger.info(f'Discord WebhookテストAPI完了: 成功={test_result.success}')
            
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
            
        except Exception as e:
            logger.error(f'Discord WebhookテストAPIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Webhook接続テストに失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def send_test_notification(
        self,
        request_data: Dict[str, Any] = Body(...)
    ) -> JSONResponse:
        """Discordテスト通知送信"""
        try:
            tracker = PerformanceTracker('Discordテスト通知API')
            
            logger.info('Discordテスト通知送信開始')
            
            # デフォルトのテストデータ
            test_data = {
                'stockCode': request_data.get('stockCode', '7974'),
                'stockName': request_data.get('stockName', '任天堂'),
                'logicType': request_data.get('logicType', 'logic_a_match'),
                'price': float(request_data.get('price', 7500)),
                'changeRate': float(request_data.get('changeRate', 3.2)),
                'volume': int(request_data.get('volume', 1500000))
            }
            
            send_result = await self.discord_service.send_stock_match_notification(
                stock_code=test_data['stockCode'],
                stock_name=test_data['stockName'],
                logic_type=test_data['logicType'],
                price=test_data['price'],
                change_rate=test_data['changeRate'],
                volume=test_data['volume'],
                additional_info={'test': True}
            )
            
            response_data = {
                "success": send_result['success'],
                "data": {
                    "sendResult": send_result,
                    "testData": test_data
                },
                "message": send_result['message']
            }
            
            status_code = status.HTTP_200_OK if send_result['success'] else status.HTTP_400_BAD_REQUEST
            
            tracker.end({"送信成功": send_result['success']})
            logger.info(f'Discordテスト通知API完了: 成功={send_result["success"]}')
            
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
            
        except Exception as e:
            logger.error(f'Discordテスト通知APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "テスト通知の送信に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def get_notification_stats(self) -> JSONResponse:
        """Discord通知統計取得"""
        try:
            tracker = PerformanceTracker('Discord通知統計API')
            
            stats = await self.discord_service.get_notification_stats()
            
            response_data = {
                "success": True,
                "data": stats,
                "message": "Discord通知統計を取得しました"
            }
            
            tracker.end({"統計取得成功": True})
            logger.info('Discord通知統計API完了')
            
            return JSONResponse(
                content=response_data,
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f'Discord通知統計APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "通知統計の取得に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def enable_notifications(self) -> JSONResponse:
        """Discord通知有効化"""
        try:
            tracker = PerformanceTracker('Discord通知有効化API')
            
            success = await self.discord_service.enable_notifications()
            
            if success:
                response_data = {
                    "success": True,
                    "message": "Discord通知を有効にしました"
                }
                status_code = status.HTTP_200_OK
            else:
                response_data = {
                    "success": False,
                    "message": "Discord設定が存在しません"
                }
                status_code = status.HTTP_404_NOT_FOUND
            
            tracker.end({"有効化成功": success})
            logger.info(f'Discord通知有効化API完了: 成功={success}')
            
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
            
        except Exception as e:
            logger.error(f'Discord通知有効化APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Discord通知の有効化に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def disable_notifications(self) -> JSONResponse:
        """Discord通知無効化"""
        try:
            tracker = PerformanceTracker('Discord通知無効化API')
            
            success = await self.discord_service.disable_notifications()
            
            if success:
                response_data = {
                    "success": True,
                    "message": "Discord通知を無効にしました"
                }
                status_code = status.HTTP_200_OK
            else:
                response_data = {
                    "success": False,
                    "message": "Discord設定が存在しません"
                }
                status_code = status.HTTP_404_NOT_FOUND
            
            tracker.end({"無効化成功": success})
            logger.info(f'Discord通知無効化API完了: 成功={success}')
            
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
            
        except Exception as e:
            logger.error(f'Discord通知無効化APIエラー: {e}')
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Discord通知の無効化に失敗しました",
                    "error": str(e)
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )