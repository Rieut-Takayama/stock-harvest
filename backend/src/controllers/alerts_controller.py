"""
アラート管理 Controller層
FastAPI ルーティング・リクエスト処理・レスポンス生成
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..services.alerts_service import AlertsService, LineNotificationService


# Pydanticモデル定義
class AlertCondition(BaseModel):
    """アラート条件"""
    type: str = Field(..., description="条件タイプ: 'price' or 'logic'")
    operator: str = Field(default=">=", description="比較演算子（価格アラート用）")
    value: float = Field(default=None, description="目標価格（価格アラート用）")
    logicType: str = Field(default=None, description="ロジック種別（ロジックアラート用）")


class AlertCreateRequest(BaseModel):
    """アラート作成リクエスト"""
    type: str = Field(..., description="アラートタイプ: 'price' or 'logic'")
    stockCode: str = Field(..., description="銘柄コード（4桁）")
    targetPrice: float = Field(default=None, description="目標価格（価格アラート用）")
    condition: AlertCondition = Field(..., description="アラート条件")


class LineNotificationConfigRequest(BaseModel):
    """LINE通知設定更新リクエスト"""
    token: str = Field(default=None, description="LINE Notifyトークン")
    isConnected: bool = Field(default=None, description="接続状態")


# ルーター作成
router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts")
async def get_alerts() -> List[Dict[str, Any]]:
    """
    アラート一覧取得
    
    Returns:
        List[Alert]: 設定済みアラートの一覧
    """
    try:
        alerts = await AlertsService.get_all_alerts()
        return alerts
    
    except Exception as e:
        print(f"❌ GET /api/alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


@router.post("/alerts")
async def create_alert(request: AlertCreateRequest) -> Dict[str, Any]:
    """
    アラート作成
    
    Args:
        request: アラート作成データ
        
    Returns:
        Alert: 作成されたアラート情報
    """
    try:
        # リクエストをサービス層の形式に変換
        alert_data = {
            "type": request.type,
            "stockCode": request.stockCode,
            "condition": {
                "type": request.condition.type,
                "operator": request.condition.operator,
                "value": request.condition.value,
                "logicType": request.condition.logicType
            }
        }
        
        # 価格アラートの場合、targetPriceからcondition.valueを設定
        if request.type == "price" and request.targetPrice is not None:
            alert_data["condition"]["value"] = request.targetPrice
        
        created_alert, message = await AlertsService.create_alert(alert_data)
        
        if created_alert:
            return created_alert
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ POST /api/alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        )


@router.put("/alerts/{alert_id}/toggle")
async def toggle_alert(alert_id: str) -> Dict[str, Any]:
    """
    アラート状態切替
    
    Args:
        alert_id: アラートID
        
    Returns:
        Alert: 更新されたアラート情報
    """
    try:
        updated_alert, message = await AlertsService.toggle_alert(alert_id)
        
        if updated_alert:
            return updated_alert
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PUT /api/alerts/{alert_id}/toggle error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle alert"
        )


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str) -> Dict[str, str]:
    """
    アラート削除
    
    Args:
        alert_id: アラートID
        
    Returns:
        dict: 削除結果メッセージ
    """
    try:
        deleted, message = await AlertsService.delete_alert(alert_id)
        
        if deleted:
            return {"message": message}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ DELETE /api/alerts/{alert_id} error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert"
        )


@router.get("/notifications/line")
async def get_line_notification_config() -> Dict[str, Any]:
    """
    LINE通知設定取得
    
    Returns:
        LineNotificationConfig: LINE通知設定
    """
    try:
        config = await LineNotificationService.get_line_config()
        
        if config:
            return config
        else:
            # 初期設定を返却
            return {
                "isConnected": False,
                "token": None,
                "status": "disconnected",
                "lastNotificationAt": None
            }
    
    except Exception as e:
        print(f"❌ GET /api/notifications/line error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve LINE notification config"
        )


@router.put("/notifications/line")
async def update_line_notification_config(request: LineNotificationConfigRequest) -> Dict[str, Any]:
    """
    LINE通知設定更新
    
    Args:
        request: LINE通知設定データ
        
    Returns:
        LineNotificationConfig: 更新されたLINE通知設定
    """
    try:
        # リクエストをサービス層の形式に変換
        config_data = {}
        
        if request.token is not None:
            config_data["token"] = request.token
        
        if request.isConnected is not None:
            config_data["isConnected"] = request.isConnected
        
        # トークンが設定された場合は接続テストを実行
        if request.token and len(request.token.strip()) > 0:
            test_success, test_message = await LineNotificationService.test_line_connection(request.token)
            if not test_success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"LINE connection test failed: {test_message}"
                )
        
        updated_config, message = await LineNotificationService.update_line_config(config_data)
        
        if updated_config:
            return updated_config
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PUT /api/notifications/line error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update LINE notification config"
        )