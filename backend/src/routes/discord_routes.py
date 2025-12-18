"""
Discord通知ルート定義
Stock Harvest AI - Discord通知機能
"""
import os
from fastapi import APIRouter
from ..controllers.discord_controller import DiscordController

# データベースURL取得
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Discordコントローラー初期化
discord_controller = DiscordController(DATABASE_URL)

# APIRouterを取得
router = discord_controller.router

# ルートパスとハンドラーの明示的なマッピング
# (デバッグ・テスト用の確認情報)
ROUTE_MAPPINGS = {
    "GET /api/notifications/discord": "Discord通知設定取得",
    "POST /api/notifications/discord": "Discord通知設定作成",
    "PUT /api/notifications/discord": "Discord通知設定更新",
    "POST /api/notifications/discord/test": "Discord Webhook接続テスト",
    "POST /api/notifications/discord/send": "Discordテスト通知送信",
    "GET /api/notifications/discord/stats": "Discord通知統計取得",
    "POST /api/notifications/discord/enable": "Discord通知有効化",
    "POST /api/notifications/discord/disable": "Discord通知無効化"
}