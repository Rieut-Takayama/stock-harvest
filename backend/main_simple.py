"""
Stock Harvest AI 簡易版バックエンド - デプロイ用
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from simple_scan_logic import scan_engine

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPIアプリ作成
app = FastAPI(
    title="Stock Harvest AI API",
    description="AI株式スキャニングシステム",
    version="1.0.0"
)

# CORS設定
allowed_origins = [
    "http://localhost:3247",
    "http://localhost:3248", 
    "https://*.netlify.app",
    "*"  # 開発用
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# レスポンス型定義
class ScanRequest(BaseModel):
    logicA: bool = True
    logicB: bool = True

class StockData(BaseModel):
    code: str
    name: str
    price: float
    change: float
    changeRate: float
    volume: int

class ScanResults(BaseModel):
    scanId: str
    completedAt: str
    totalProcessed: int
    logicA: Dict[str, Any]
    logicB: Dict[str, Any]

class ScanStatus(BaseModel):
    isRunning: bool
    progress: int
    totalStocks: int
    processedStocks: int
    currentStock: Optional[str]
    estimatedTime: int
    message: str

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Stock Harvest AI Backend is running", "status": "OK"}

@app.get("/api/system/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/scan/execute")
async def execute_scan(request: ScanRequest):
    """スキャン実行"""
    try:
        logger.info(f"スキャン実行開始: Logic A={request.logicA}, Logic B={request.logicB}")
        
        if scan_engine.is_scanning:
            raise HTTPException(status_code=409, detail="スキャンが既に実行中です")
        
        # スキャン実行
        result = await scan_engine.execute_scan(
            logic_a=request.logicA,
            logic_b=request.logicB
        )
        
        logger.info(f"スキャン完了: {result['scanId']}")
        return {"scanId": result["scanId"], "status": "started"}
        
    except Exception as e:
        logger.error(f"スキャン実行エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/status")
async def get_scan_status():
    """スキャン状況取得"""
    try:
        status = scan_engine.get_scan_status()
        return status
    except Exception as e:
        logger.error(f"スキャン状況取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/results")
async def get_scan_results():
    """スキャン結果取得"""
    try:
        results = scan_engine.get_scan_results()
        return results
    except Exception as e:
        logger.error(f"スキャン結果取得エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラ"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8432))
    logger.info(f"🚀 Stock Harvest AI 簡易版バックエンド起動 (Port: {port})")
    uvicorn.run(app, host="0.0.0.0", port=port)