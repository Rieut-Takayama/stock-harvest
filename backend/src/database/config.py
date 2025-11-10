"""
データベース設定とコネクション管理
"""

import os
from databases import Database
from sqlalchemy import MetaData, create_engine
from dotenv import load_dotenv

load_dotenv()

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
        print("✅ Database connection established")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def disconnect_db():
    """データベースから切断"""
    try:
        await database.disconnect()
        print("✅ Database disconnected")
    except Exception as e:
        print(f"❌ Database disconnection failed: {e}")

async def get_db_connection():
    """
    新しいデータベース接続を取得
    asyncpgを直接使用
    """
    import asyncpg
    return await asyncpg.connect(DATABASE_URL)

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
        print(f"Database health check failed: {e}")
        return {
            "status": "disconnected", 
            "healthy": False,
            "error": str(e)
        }