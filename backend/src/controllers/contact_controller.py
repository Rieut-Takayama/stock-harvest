"""
お問い合わせ関連のコントローラー層
HTTPリクエスト処理を担当
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
import logging
from ..services.contact_service import ContactService

logger = logging.getLogger(__name__)

# ルーター作成
router = APIRouter(prefix="/api/contact", tags=["contact"])

# リクエストモデル
class ContactFormRequest(BaseModel):
    type: str  # 'technical', 'feature', 'bug', 'other'
    subject: str
    content: str
    email: str
    priority: str = 'medium'  # 'low', 'medium', 'high'

# サービス初期化
contact_service = ContactService()

@router.get("/faq")
async def get_faq_list():
    """
    FAQ一覧取得エンドポイント
    
    Returns:
        List[FAQ]: FAQ項目のリスト
    """
    try:
        logger.info("📋 GET /api/contact/faq リクエスト受信")
        
        # サービスからFAQ一覧を取得
        faq_list = await contact_service.get_faq_list()
        
        logger.info(f"✅ FAQ一覧レスポンス送信: {len(faq_list)}件")
        return faq_list
        
    except Exception as e:
        logger.error(f"❌ FAQ取得エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "FAQ一覧の取得に失敗しました",
                "error": str(e),
                "endpoint": "/api/contact/faq"
            }
        )

@router.post("/submit")
async def submit_contact_form(form_data: ContactFormRequest):
    """
    お問い合わせフォーム送信エンドポイント
    
    Args:
        form_data: お問い合わせフォームデータ
        
    Returns:
        dict: 送信結果
    """
    try:
        logger.info("📧 POST /api/contact/submit リクエスト受信")
        logger.info(f"お問い合わせタイプ: {form_data.type}, 件名: {form_data.subject}")
        
        # バリデーション
        if not form_data.subject.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="件名は必須です"
            )
        
        if not form_data.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="お問い合わせ内容は必須です"
            )
        
        # サービスでお問い合わせ処理
        result = await contact_service.submit_contact_form({
            "type": form_data.type,
            "subject": form_data.subject,
            "content": form_data.content,
            "email": form_data.email,
            "priority": form_data.priority
        })
        
        logger.info("✅ お問い合わせ送信完了")
        
        return {
            "success": True,
            "message": "お問い合わせを受け付けました。2営業日以内にご返信いたします。",
            "inquiryId": result.get("inquiry_id"),
            "submittedAt": result.get("submitted_at")
        }
        
    except HTTPException:
        # FastAPIのHTTPExceptionはそのまま再スロー
        raise
    except Exception as e:
        logger.error(f"❌ お問い合わせ送信エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "お問い合わせの送信に失敗しました",
                "error": str(e),
                "endpoint": "/api/contact/submit"
            }
        )