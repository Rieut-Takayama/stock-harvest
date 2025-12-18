"""
データベース設定とコネクション管理
"""

import os
from databases import Database
from sqlalchemy import MetaData, create_engine
from dotenv import load_dotenv
from ..lib.logger import logger

load_dotenv(dotenv_path='/Users/rieut/STOCK HARVEST/.env.local')

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# データベース接続
database = Database(DATABASE_URL)

# SQLAlchemy エンジン（メタデータとDDL用）
engine = create_engine(DATABASE_URL)

# メタデータ（テーブル定義用）
metadata = MetaData()

async def connect_db():
    """データベースに接続"""
    try:
        await database.connect()
        logger.info("Database connection established")
        return True
    except Exception as e:
        logger.error("Database connection failed", {"error": str(e)})
        return False

async def disconnect_db():
    """データベースから切断"""
    try:
        await database.disconnect()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error("Database disconnection failed", {"error": str(e)})

async def get_db_connection():
    """
    既存のDatabase接続を返す
    SQLite/PostgreSQL両対応
    """
    return database

async def get_db():
    """
    データベース接続を取得する(依存性注入用)
    """
    return database

async def get_database_connection():
    """
    データベース接続を取得する(テスト用エイリアス)
    """
    return database

async def get_db_status():
    """データベース接続状態を確認"""
    try:
        # 簡単なクエリでヘルスチェック
        result = await database.fetch_one("SELECT 1 as status")
        return {
            "status": "connected" if result else "disconnected",
            "healthy": True if result else False
        }
    except Exception as e:
        logger.error("Database health check failed", {"error": str(e)})
        return {
            "status": "disconnected", 
            "healthy": False,
            "error": str(e)
        }