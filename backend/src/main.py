"""
Stock Harvest AI バックエンドアプリケーション
FastAPI メインエントリーポイント
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# データベース
from .database.config import connect_db, disconnect_db

# コントローラー
from .controllers.system_controller import router as system_router
from .controllers.contact_controller import router as contact_router
from .controllers.alerts_controller import router as alerts_router
from .controllers.scan_controller import router as scan_router
from .controllers.charts_controller import router as charts_router
from .controllers.signals_controller import router as signals_router
from .controllers.simple_scan_controller import router as simple_scan_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理
    """
    # 起動時
    logger.info("🚀 Stock Harvest AI バックエンド起動開始")
    
    # データベース接続
    db_connected = await connect_db()
    if not db_connected:
        logger.error("❌ データベース接続失敗 - アプリケーションを終了します")
        raise RuntimeError("Database connection failed")
    
    logger.info("✅ アプリケーション起動完了")
    
    yield
    
    # 終了時
    logger.info("🛑 アプリケーション終了処理開始")
    await disconnect_db()
    logger.info("✅ アプリケーション終了完了")

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Stock Harvest AI API",
    description="株式スキャン・アラートシステムのバックエンドAPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3247",  # フロントエンド開発サーバー
        "https://stock-harvest-ai.vercel.app",  # 本番フロントエンド
        os.getenv("FRONTEND_URL", "http://localhost:3247")
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(system_router)
app.include_router(contact_router)
app.include_router(alerts_router)
app.include_router(scan_router)
app.include_router(charts_router)
app.include_router(signals_router)
app.include_router(simple_scan_router, prefix="/api/scan")

# ルートエンドポイント
@app.get("/")
async def root():
    """
    API ルートエンドポイント
    """
    return {
        "message": "Stock Harvest AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "system_info": "/api/system/info",
            "system_status": "/api/system/status", 
            "contact_faq": "/api/contact/faq",
            "contact_submit": "/api/contact/submit",
            "alerts_list": "/api/alerts",
            "alerts_create": "/api/alerts",
            "line_notification": "/api/notifications/line",
            "scan_execute": "/api/scan/execute",
            "scan_status": "/api/scan/status",
            "scan_results": "/api/scan/results",
            "signals_manual_execute": "/api/signals/manual-execute",
            "signals_history": "/api/signals/history",
            "chart_data": "/api/charts/data/{stockCode}",
            "chart_health": "/api/charts/health"
        }
    }

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """
    基本的なヘルスチェック
    """
    return {
        "status": "healthy",
        "service": "stock-harvest-ai-backend"
    }

# グローバル例外ハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    グローバル例外処理
    """
    logger.error(f"🚨 未処理例外: {type(exc).__name__}: {str(exc)}")
    logger.error(f"リクエストパス: {request.url.path}")
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "内部サーバーエラーが発生しました",
            "error": str(exc),
            "path": request.url.path,
            "type": type(exc).__name__
        }
    )

# リクエストログ
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    リクエストログ
    """
    logger.info(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Response: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT_BACKEND", 8432)),
        reload=True
    )