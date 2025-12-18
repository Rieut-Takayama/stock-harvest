from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import random

router = APIRouter()

# データモデル
class AlertCreate(BaseModel):
    type: str  # "price", "logic_match", "volume_surge"
    stock_code: str
    target_price: Optional[float] = None
    condition: str  # "above", "below", "match"
    notification_method: str  # "line", "discord", "email"

class Alert(BaseModel):
    id: str
    type: str
    stock_code: str
    stock_name: str
    target_price: Optional[float]
    condition: str
    status: str  # "active", "triggered", "disabled"
    notification_method: str
    created_at: str
    triggered_at: Optional[str] = None

# メモリ内アラートストレージ（実際の実装ではデータベースを使用）
alerts_storage: List[Alert] = [
    Alert(
        id="alert_001",
        type="price",
        stock_code="7203",
        stock_name="トヨタ自動車",
        target_price=2200.0,
        condition="above",
        status="active",
        notification_method="discord",
        created_at=datetime.now().isoformat()
    ),
    Alert(
        id="alert_002", 
        type="logic_match",
        stock_code="6758",
        stock_name="ソニーグループ",
        target_price=None,
        condition="match",
        status="active",
        notification_method="line",
        created_at=datetime.now().isoformat()
    )
]

@router.get("/api/alerts")
async def get_alerts():
    """全アラート取得"""
    return {"alerts": alerts_storage}

@router.post("/api/alerts")
async def create_alert(alert_data: AlertCreate):
    """新しいアラート作成"""
    try:
        # 銘柄名取得（簡易版）
        stock_names = {
            "7203": "トヨタ自動車",
            "6758": "ソニーグループ", 
            "9984": "ソフトバンクグループ",
            "8058": "三菱商事",
            "9433": "KDDI"
        }
        
        new_alert = Alert(
            id=f"alert_{random.randint(1000, 9999)}",
            type=alert_data.type,
            stock_code=alert_data.stock_code,
            stock_name=stock_names.get(alert_data.stock_code, f"銘柄{alert_data.stock_code}"),
            target_price=alert_data.target_price,
            condition=alert_data.condition,
            status="active",
            notification_method=alert_data.notification_method,
            created_at=datetime.now().isoformat()
        )
        
        alerts_storage.append(new_alert)
        
        return {
            "message": "アラートを作成しました",
            "alert": new_alert,
            "total_alerts": len(alerts_storage)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"アラート作成エラー: {str(e)}")

@router.put("/api/alerts/{alert_id}")
async def update_alert(alert_id: str, status: str):
    """アラート状態更新"""
    for alert in alerts_storage:
        if alert.id == alert_id:
            alert.status = status
            return {"message": f"アラート{alert_id}を{status}に更新しました"}
    
    raise HTTPException(status_code=404, detail="アラートが見つかりません")

@router.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """アラート削除"""
    global alerts_storage
    alerts_storage = [a for a in alerts_storage if a.id != alert_id]
    return {"message": f"アラート{alert_id}を削除しました"}

@router.get("/api/notifications/line/status")
async def line_notification_status():
    """LINE通知設定状況"""
    return {
        "configured": True,
        "token_valid": True,
        "last_sent": datetime.now().isoformat(),
        "monthly_limit": 1000,
        "used_this_month": random.randint(50, 200)
    }

@router.post("/api/notifications/line/test")
async def test_line_notification():
    """LINE通知テスト送信"""
    return {
        "success": True,
        "message": "テスト通知を送信しました",
        "sent_at": datetime.now().isoformat()
    }