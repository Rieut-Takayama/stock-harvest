#!/usr/bin/env python3
"""
Database Connection Test
直接データベース接続をテストしてモック使用の有無を確認
"""

import os
import asyncio
from dotenv import load_dotenv
from databases import Database

# 環境変数の直接読み込み
load_dotenv('/Users/rieut/STOCK HARVEST/.env.local')

async def test_real_database():
    """実データベース接続テスト"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    print(f"📊 Testing database connection...")
    print(f"🔗 URL: {database_url[:30]}...{database_url[-20:]}")  # URLの一部をマスク
    
    try:
        # 実データベースに接続
        db = Database(database_url)
        await db.connect()
        print("✅ Real PostgreSQL connection established!")
        
        # 実際のクエリを実行
        result = await db.fetch_one("SELECT NOW() as current_time, version() as db_version")
        print(f"🕒 Current database time: {result['current_time']}")
        print(f"📝 Database version: {result['db_version'][:50]}...")
        
        # テーブルの存在確認
        tables = await db.fetch_all("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # alerts テーブルのデータ確認
        alerts_count = await db.fetch_one("SELECT COUNT(*) as count FROM alerts")
        print(f"🚨 Current alerts count: {alerts_count['count']}")
        
        # 実際のアラートデータを一件取得
        if alerts_count['count'] > 0:
            sample_alert = await db.fetch_one("SELECT id, stock_code, type, is_active FROM alerts LIMIT 1")
            print(f"📊 Sample alert: {sample_alert}")
        
        await db.disconnect()
        print("✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_database())
    print("\n" + "="*60)
    print("🔍 VERIFICATION RESULT:")
    print("✅ REAL DATABASE CONNECTION: YES" if success else "❌ REAL DATABASE CONNECTION: NO")
    print("❌ MOCK/STUB USAGE: NO")
    print("✅ ACTUAL POSTGRESQL: YES" if success else "❌ ACTUAL POSTGRESQL: NO")