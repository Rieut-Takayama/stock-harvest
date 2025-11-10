"""
手動決済シグナル - コントローラー層
Stock Harvest AI プロジェクト
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..services.signals_service import SignalsService


# リクエスト・レスポンス用のPydanticモデル
class ManualSignalRequest(BaseModel):
    type: str  # "stop_loss" または "take_profit"
    stockCode: Optional[str] = None
    reason: Optional[str] = None


class SignalExecutionResponse(BaseModel):
    success: bool
    signalId: str
    executedAt: str
    message: str
    affectedPositions: Optional[int] = None


# APIルーター作成
router = APIRouter(prefix="/api/signals", tags=["signals"])

# サービス層のインスタンス
signals_service = SignalsService()


@router.post("/manual-execute", response_model=SignalExecutionResponse)
async def execute_manual_signal(request: ManualSignalRequest) -> SignalExecutionResponse:
    """
    手動決済シグナル実行エンドポイント
    
    Args:
        request: 手動シグナル実行リクエスト
        
    Returns:
        シグナル実行結果
        
    Raises:
        HTTPException: 入力値エラーまたは実行エラー時
    """
    try:
        # リクエストバリデーション
        if request.type not in ["stop_loss", "take_profit"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid signal type: {request.type}. Must be 'stop_loss' or 'take_profit'"
            )
        
        # 銘柄コードの基本的なバリデーション（4桁数字）
        if request.stockCode and not (request.stockCode.isdigit() and len(request.stockCode) == 4):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stock code format: {request.stockCode}. Must be 4-digit number"
            )
        
        # サービス層でシグナル実行
        result = await signals_service.execute_manual_signal(
            signal_type=request.type,
            stock_code=request.stockCode,
            reason=request.reason
        )
        
        # レスポンス作成
        return SignalExecutionResponse(
            success=result["success"],
            signalId=result["signalId"],
            executedAt=result["executedAt"],
            message=result["message"],
            affectedPositions=result.get("affectedPositions")
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/history")
async def get_signal_history(limit: int = 20) -> Dict[str, Any]:
    """
    シグナル実行履歴取得エンドポイント
    
    Args:
        limit: 取得件数制限（デフォルト: 20）
        
    Returns:
        シグナル実行履歴
    """
    try:
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 100"
            )
        
        result = await signals_service.get_signal_history(limit)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get signal history: {str(e)}"
        )