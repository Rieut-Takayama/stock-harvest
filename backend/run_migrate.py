#!/usr/bin/env python3
"""
データベースマイグレーション実行スクリプト
環境変数を自動ロードしてマイグレーションを実行
"""

import os
import asyncio

def load_env():
    """環境変数をロード"""
    env_path = "../.env.local"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print(f"✅ Environment variables loaded from {env_path}")

if __name__ == "__main__":
    # 環境変数をロード
    load_env()
    
    # マイグレーション実行
    from src.database.migrate import migrate
    asyncio.run(migrate())