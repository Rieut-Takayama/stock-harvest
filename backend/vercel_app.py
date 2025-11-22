"""
Stock Harvest AI - Vercel用シンプルバックエンド
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any

# FastAPIアプリ作成
app = FastAPI(
    title="Stock Harvest AI API",
    description="AI株式スキャニングシステム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデル
class LoginRequest(BaseModel):
    username: str
    password: str

class StockData(BaseModel):
    code: str
    name: str
    price: float
    change: float
    changeRate: float
    volume: int

# ヘルスチェック
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Stock Harvest AI"}

# 認証エンドポイント
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    # デモ認証
    if request.username == "demo" and request.password == "demo":
        return {
            "token": "demo_token_12345",
            "user": {
                "id": 1,
                "username": "demo",
                "email": "demo@example.com"
            }
        }
    raise HTTPException(status_code=401, detail="認証に失敗しました")

# ダッシュボードデータ
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    return {
        "totalStocks": 1205,
        "gainers": 245,
        "losers": 167,
        "unchanged": 793,
        "lastUpdate": "2025-11-21T21:45:00Z"
    }

# スキャン開始
@app.post("/api/scan/start")
async def start_scan():
    return {
        "success": True,
        "message": "スキャンを開始しました",
        "scanId": "scan_demo_12345"
    }

# スキャン結果
@app.get("/api/scan/results")
async def get_scan_results():
    return {
        "results": [
            {
                "code": "7203",
                "name": "トヨタ自動車",
                "price": 2456.0,
                "change": 45.0,
                "changeRate": 1.87,
                "volume": 12450000,
                "signals": ["上昇トレンド", "高出来高"]
            },
            {
                "code": "6758",
                "name": "ソニーグループ",
                "price": 13890.0,
                "change": -230.0,
                "changeRate": -1.63,
                "volume": 8760000,
                "signals": ["下降トレンド", "売りシグナル"]
            }
        ],
        "total": 2,
        "lastUpdate": "2025-11-21T21:45:00Z"
    }

# アラート一覧
@app.get("/api/alerts")
async def get_alerts():
    return {
        "alerts": [
            {
                "id": 1,
                "symbol": "7203",
                "type": "price",
                "condition": "price > 2500",
                "status": "active",
                "createdAt": "2025-11-21T10:00:00Z"
            }
        ]
    }

# 問い合わせ送信
@app.post("/api/contact")
async def submit_contact(request: Dict[str, Any]):
    return {
        "success": True,
        "message": "お問い合わせを受け付けました"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)