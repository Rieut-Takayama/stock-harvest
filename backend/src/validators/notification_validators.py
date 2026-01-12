"""
通知設定バリデータ
LINE Notify設定のバリデーション処理
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class LineConfigUpdateValidator(BaseModel):
    """LINE通知設定更新バリデータ"""

    token: Optional[str] = Field(
        None,
        description="LINEトークン",
        min_length=1,
        max_length=500
    )
    is_connected: Optional[bool] = Field(
        None,
        description="LINE連携状態"
    )

    @validator('token')
    def validate_token(cls, v: Optional[str]) -> Optional[str]:
        """トークンのバリデーション"""
        if v is not None:
            # 空白文字のみの場合はエラー
            if v.strip() == "":
                raise ValueError("トークンは空白のみにできません")

            # トークンの長さチェック
            if len(v) < 10:
                raise ValueError("トークンが短すぎます（最低10文字必要）")

            # トークンの形式チェック（基本的な英数字チェック）
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError("トークンには英数字、ハイフン、アンダースコアのみ使用できます")

        return v

    @validator('is_connected')
    def validate_is_connected(cls, v: Optional[bool]) -> Optional[bool]:
        """連携状態のバリデーション"""
        # 特に厳しいバリデーションは不要（boolean型なので）
        return v

    class Config:
        """Pydantic設定"""
        json_schema_extra = {
            "example": {
                "token": "your-line-notify-token-here",
                "is_connected": True
            }
        }


def validate_line_token_format(token: str) -> bool:
    """
    LINEトークンの形式を検証する

    Args:
        token: 検証するLINEトークン

    Returns:
        bool: トークンが有効な形式かどうか
    """
    if not token:
        return False

    # 空白文字のみの場合は無効
    if token.strip() == "":
        return False

    # 長さチェック（最低10文字）
    if len(token) < 10:
        return False

    # 基本的な形式チェック
    if not token.replace('-', '').replace('_', '').isalnum():
        return False

    return True


def mask_token(token: Optional[str], show_chars: int = 4) -> str:
    """
    トークンをマスキングする

    Args:
        token: マスキング対象のトークン
        show_chars: 表示する先頭文字数（デフォルト: 4）

    Returns:
        str: マスキングされたトークン（例: "abcd***masked***"）
    """
    if not token:
        return ""

    if len(token) <= show_chars:
        return "***masked***"

    return f"{token[:show_chars]}***masked***"
