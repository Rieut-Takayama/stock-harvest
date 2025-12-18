"""
Stock Harvest AI バックエンドアプリケーション
FastAPI メインエントリーポイント
"""

import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# 統一ログライブラリを使用
from .lib.logger import logger, transaction_scope, track_performance

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
from .controllers.archive_controller import router as archive_router
from .controllers.manual_scores_controller import router as manual_scores_router
from .controllers.data_source_controller import router as data_source_router

# 売買支援API ルート
from .routes.trading_routes import router as trading_router, history_router

# Discord通知ルート
from .routes.discord_routes import router as discord_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理
    """
    with transaction_scope("application_startup"):
        # 起動時
        logger.info("Stock Harvest AI バックエンド起動開始")
        
        # データベース接続
        with track_performance("database_startup_connection"):
            db_connected = await connect_db()
            if not db_connected:
                logger.error("データベース接続失敗 - アプリケーションを終了します")
                raise RuntimeError("Database connection failed")
        
        logger.info("アプリケーション起動完了", {
            "app_name": "Stock Harvest AI",
            "version": "1.0.0",
            "environment": os.getenv("NODE_ENV", "development")
        })
        
        yield
        
        # 終了時
        with transaction_scope("application_shutdown"):
            logger.info("アプリケーション終了処理開始")
            await disconnect_db()
            logger.info("アプリケーション終了完了")

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

# 新機能ルーター追加
app.include_router(archive_router)
app.include_router(manual_scores_router)

# データソース基盤API ルーター追加
app.include_router(data_source_router)

# 売買支援API ルーター追加
app.include_router(trading_router)
app.include_router(history_router)

# Discord通知 ルーター追加
app.include_router(discord_router)

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
            "chart_health": "/api/charts/health",
            "trading_entry_optimization": "/api/trading/entry-optimization",
            "trading_ifdoco_guide": "/api/trading/ifdoco-guide",
            "trading_performance": "/api/trading/performance",
            "trading_history": "/api/history/trades",
            "signal_history": "/api/history/signals",
            "archive_search": "/api/archive/search",
            "archive_stats": "/api/archive/stats",
            "archive_export": "/api/archive/export/csv",
            "scores_create": "/api/scores/manual",
            "scores_search": "/api/scores/search",
            "scores_stats": "/api/scores/stats",
            "discord_config": "/api/notifications/discord",
            "discord_test": "/api/notifications/discord/test",
            "discord_send": "/api/notifications/discord/send",
            "discord_stats": "/api/notifications/discord/stats",
            "data_source_listing_update": "/api/data-source/listing-dates/update",
            "data_source_listing_targets": "/api/data-source/listing-dates/targets",
            "data_source_price_limits": "/api/data-source/price-limits/calculate",
            "data_source_stock_data": "/api/data-source/stock-data/{stock_code}",
            "data_source_health": "/api/data-source/health"
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
    logger.error("未処理例外が発生", {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "request_path": request.url.path,
        "request_method": request.method
    })
    
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
    with transaction_scope(f"{request.method}_{request.url.path}"):
        start_time = time.time()
        logger.info("リクエスト受信", {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params)
        })
        
        response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000  # ms
        logger.info("レスポンス送信", {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "response_time_ms": round(duration, 2)
        })
        
        return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT_BACKEND", 8432)),
        reload=True
    )