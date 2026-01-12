"""
お問い合わせ関連のコントローラー層
HTTPリクエスト処理を担当
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import ValidationError
from ..lib.logger import logger, transaction_scope, PerformanceTracker
from ..services.contact_service import ContactService
from ..validators.contact_validators import ContactFormValidator, ContactFormResponse

# ルーター作成
router = APIRouter(prefix="/api/contact", tags=["contact"])

# サービス初期化
contact_service = ContactService()

@router.get("/faq")
async def get_faq_list() -> List[Dict[str, Any]]:
    """
    FAQ一覧取得エンドポイント

    Returns:
        List[FAQ]: FAQ項目のリスト
    """
    with transaction_scope("GET /api/contact/faq"):
        tracker = PerformanceTracker("FAQ取得", logger)

        try:
            logger.info("FAQ一覧取得リクエスト受信")

            # サービスからFAQ一覧を取得
            faq_list = await contact_service.get_faq_list()

            tracker.end({"faq_count": len(faq_list)})
            logger.info("FAQ一覧レスポンス送信", {"count": len(faq_list)})

            return faq_list

        except Exception as e:
            logger.error("FAQ取得エラー", {"error": str(e), "error_type": type(e).__name__})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "FAQ一覧の取得に失敗しました",
                    "error": str(e),
                    "endpoint": "/api/contact/faq"
                }
            )

@router.post("/submit", response_model=ContactFormResponse)
async def submit_contact_form(form_data: ContactFormValidator) -> ContactFormResponse:
    """
    お問い合わせフォーム送信エンドポイント

    Args:
        form_data: お問い合わせフォームデータ（Pydanticバリデーション済み）

    Returns:
        ContactFormResponse: 送信結果
    """
    with transaction_scope("POST /api/contact/submit"):
        tracker = PerformanceTracker("問合せフォーム送信", logger)

        try:
            logger.info("問合せフォーム送信リクエスト受信", {
                "type": form_data.type,
                "subject": form_data.subject[:50],  # 最初の50文字のみログ
                "priority": form_data.priority
            })

            # サービスでお問い合わせ処理
            result = await contact_service.submit_contact_form({
                "type": form_data.type,
                "subject": form_data.subject,
                "content": form_data.content,
                "email": form_data.email,
                "priority": form_data.priority
            })

            tracker.end({
                "inquiry_id": result.get("inquiry_id"),
                "type": form_data.type
            })

            logger.info("問合せフォーム送信完了", {
                "inquiry_id": result.get("inquiry_id")
            })

            return ContactFormResponse(
                success=True,
                message="お問い合わせを受け付けました。2営業日以内にご返信いたします。",
                inquiryId=result.get("inquiry_id"),
                submittedAt=result.get("submitted_at")
            )

        except ValidationError as e:
            logger.warning("バリデーションエラー", {
                "errors": e.errors(),
                "body": e.json()
            })
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "入力データが不正です",
                    "errors": e.errors(),
                    "endpoint": "/api/contact/submit"
                }
            )
        except HTTPException:
            # FastAPIのHTTPExceptionはそのまま再スロー
            raise
        except Exception as e:
            logger.error("問合せフォーム送信エラー", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "お問い合わせの送信に失敗しました",
                    "error": str(e),
                    "endpoint": "/api/contact/submit"
                }
            )