"""
お問い合わせ関連のバリデーター
Pydanticモデルを使用した厳密な型検証
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal


class ContactFormValidator(BaseModel):
    """
    問合せフォームのバリデーター
    API仕様書: docs/api-specs/contact-support-api.md
    """
    type: Literal['technical', 'feature', 'bug', 'other'] = Field(
        ...,
        description="問合せタイプ"
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="件名"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="問合せ内容"
    )
    email: EmailStr = Field(
        ...,
        description="メールアドレス"
    )
    priority: Literal['low', 'medium', 'high'] = Field(
        default='medium',
        description="優先度"
    )

    @field_validator('subject')
    def validate_subject(cls, v: str) -> str:
        """件名のバリデーション"""
        v = v.strip()
        if not v:
            raise ValueError('件名は必須です')
        if len(v) > 200:
            raise ValueError('件名は200文字以内で入力してください')
        return v

    @field_validator('content')
    def validate_content(cls, v: str) -> str:
        """問合せ内容のバリデーション"""
        v = v.strip()
        if not v:
            raise ValueError('問合せ内容は必須です')
        if len(v) < 10:
            raise ValueError('問合せ内容は10文字以上で入力してください')
        if len(v) > 5000:
            raise ValueError('問合せ内容は5000文字以内で入力してください')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "type": "technical",
                "subject": "ログインできない",
                "content": "ログインページでエラーが発生します。詳細は以下の通りです...",
                "email": "user@example.com",
                "priority": "medium"
            }
        }


class ContactFormResponse(BaseModel):
    """
    問合せフォーム送信レスポンス
    """
    success: bool = Field(..., description="成功フラグ")
    message: str = Field(..., description="メッセージ")
    inquiryId: str = Field(None, description="問合せID")
    submittedAt: str = Field(None, description="送信日時")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "お問い合わせを受け付けました。2営業日以内にご返信いたします。",
                "inquiryId": "inq-abc123def456",
                "submittedAt": "2025-12-14T10:30:00Z"
            }
        }
