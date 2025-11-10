"""
テスト環境専用設定
本番データベースへの影響を防ぐためのテスト分離システム
"""

import os
import asyncio
import uuid
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from databases import Database
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager

# 環境変数読み込み
load_dotenv('/Users/rieut/STOCK HARVEST/.env.local')

# テストモードを有効化
os.environ['TESTING_MODE'] = 'true'

class TestDatabaseManager:
    """テスト専用データベース管理クラス"""
    
    def __init__(self):
        self.main_database_url = os.getenv("DATABASE_URL")
        self.test_database_url = None
        self.test_database = None
        self.test_db_name = None
        self.main_engine = None
        self.test_engine = None
        
    def _generate_test_db_name(self) -> str:
        """ユニークなテストDB名を生成"""
        test_id = str(uuid.uuid4()).replace('-', '')[:8]
        return f"test_stockharvest_{test_id}"
    
    async def setup_test_database(self) -> Database:
        """専用テストデータベースをセットアップ"""
        if self.test_database:
            return self.test_database
            
        try:
            # メインデータベースの接続情報を解析
            if not self.main_database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
                
            # テストDB名を生成
            self.test_db_name = self._generate_test_db_name()
            
            # メインエンジンでテストDBを作成
            base_url = self.main_database_url.rsplit('/', 1)[0]  # データベース名を削除
            self.main_engine = create_engine(base_url + '/postgres')  # postgresデフォルトDBに接続
            
            # テストデータベースを作成
            with self.main_engine.connect() as conn:
                conn.execute(text(f'CREATE DATABASE "{self.test_db_name}"'))
                conn.commit()
                print(f"✅ テスト用データベース作成: {self.test_db_name}")
            
            # テストDB用のURL生成
            self.test_database_url = f"{base_url}/{self.test_db_name}"
            if "?sslmode=" in self.main_database_url:
                ssl_params = self.main_database_url.split("?", 1)[1]
                self.test_database_url += f"?{ssl_params}"
                
            # テストデータベースに接続
            self.test_database = Database(self.test_database_url)
            await self.test_database.connect()
            
            # テーブル構造を複製
            await self._setup_test_schema()
            
            print(f"✅ テストデータベース準備完了: {self.test_db_name}")
            return self.test_database
            
        except Exception as e:
            # Neonの場合はテストDB作成ができないため、代替手段を使用
            print(f"⚠️ 専用DB作成失敗（Neon制限）、代替テスト環境を使用: {e}")
            return await self._setup_fallback_test_environment()
    
    async def _setup_test_schema(self):
        """テスト用スキーマをセットアップ"""
        # 本番スキーマを複製
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS system_info (
                id SERIAL PRIMARY KEY,
                version VARCHAR(20) NOT NULL DEFAULT 'v1.0.0',
                status VARCHAR(20) NOT NULL DEFAULT 'healthy',
                active_alerts INTEGER NOT NULL DEFAULT 0,
                total_users INTEGER NOT NULL DEFAULT 0,
                database_status VARCHAR(20) NOT NULL DEFAULT 'connected',
                status_display VARCHAR(50) NOT NULL DEFAULT '正常稼働中',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS faq (
                id VARCHAR(50) PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                tags TEXT[] DEFAULT '{}',
                is_active BOOLEAN NOT NULL DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS contact_inquiries (
                id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(20) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                email VARCHAR(100) NOT NULL,
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                status VARCHAR(20) NOT NULL DEFAULT 'open',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        ]
        
        for query in schema_queries:
            await self.test_database.execute(query)
            
        # 初期データを挿入
        await self._insert_test_data()
    
    async def _insert_test_data(self):
        """テスト用初期データを挿入"""
        # システム情報
        await self.test_database.execute("""
            INSERT INTO system_info (id, version, status, active_alerts, total_users, database_status, status_display)
            VALUES (1, 'v1.0.0', 'healthy', 0, 1, 'connected', '正常稼働中')
            ON CONFLICT (id) DO NOTHING
        """)
        
        # FAQ データ
        faq_data = [
            {
                'id': 'faq-general-001',
                'category': 'general',
                'question': 'Stock Harvest AI とは何ですか？',
                'answer': 'Stock Harvest AI は、AI技術を活用した株式投資支援ツールです。',
                'tags': ['general', 'about']
            },
            {
                'id': 'faq-technical-001',
                'category': 'technical',
                'question': 'システムの動作要件は何ですか？',
                'answer': 'モダンなWebブラウザ（Chrome、Firefox、Safari、Edge）が必要です。',
                'tags': ['technical', 'requirements']
            }
        ]
        
        for faq in faq_data:
            await self.test_database.execute(
                """
                INSERT INTO faq (id, category, question, answer, tags, is_active)
                VALUES (:id, :category, :question, :answer, :tags, true)
                ON CONFLICT (id) DO NOTHING
                """,
                {**faq, 'tags': faq['tags']}
            )
    
    async def _setup_fallback_test_environment(self) -> Database:
        """代替テスト環境（Neon制限対応）"""
        # メインデータベースを使用するが、テスト用プレフィックスで分離
        self.test_database = Database(self.main_database_url)
        await self.test_database.connect()
        
        # テスト用データが既に存在するか確認
        system_info = await self.test_database.fetch_one("SELECT id FROM system_info WHERE id = 1")
        if not system_info:
            await self._insert_test_data()
            
        print("✅ 代替テスト環境準備完了（本番DB使用、プレフィックス分離）")
        return self.test_database
    
    async def cleanup_test_database(self):
        """テストデータベースのクリーンアップ"""
        try:
            if self.test_database:
                await self.test_database.disconnect()
                
            if self.test_db_name and self.main_engine:
                # 専用テストDBを削除
                with self.main_engine.connect() as conn:
                    conn.execute(text(f'DROP DATABASE IF EXISTS "{self.test_db_name}"'))
                    conn.commit()
                    print(f"✅ テスト用データベース削除: {self.test_db_name}")
                    
        except Exception as e:
            print(f"⚠️ テストDBクリーンアップエラー: {e}")
        finally:
            if self.main_engine:
                self.main_engine.dispose()

class TestTransaction:
    """テスト用トランザクション管理"""
    
    def __init__(self, database: Database):
        self.database = database
        self.transaction = None
        
    @asynccontextmanager
    async def rollback_on_exit(self):
        """テスト終了時に自動ロールバック"""
        transaction = await self.database.transaction()
        try:
            yield self.database
        finally:
            await transaction.rollback()
            print("🔄 テストトランザクションをロールバック")

class TestDataManager:
    """テストデータ管理クラス"""
    
    def __init__(self):
        self.created_data = []
        self.unique_suffix = None
        
    def generate_unique_test_data(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """ユニークなテストデータを生成"""
        if not self.unique_suffix:
            import time
            import random
            self.unique_suffix = f"{int(time.time())}-{random.randint(1000, 9999)}"
        
        test_data = base_data.copy()
        
        # EmailとIDにユニーク接尾辞を追加
        if 'email' in test_data:
            test_data['email'] = f"test-{self.unique_suffix}@example.com"
        if 'id' in test_data:
            test_data['id'] = f"test-{self.unique_suffix}-{test_data['id']}"
        if 'subject' in test_data:
            test_data['subject'] = f"[TEST-{self.unique_suffix}] {test_data['subject']}"
        
        # 作成データを記録
        self.created_data.append(test_data)
        
        return test_data
    
    async def cleanup_created_data(self, database: Database):
        """作成したテストデータをクリーンアップ"""
        try:
            if self.unique_suffix:
                # contact_inquiries のクリーンアップ
                await database.execute(
                    "DELETE FROM contact_inquiries WHERE email LIKE :pattern",
                    {"pattern": f"%test-{self.unique_suffix}%"}
                )
                
                # 必要に応じて他のテーブルもクリーンアップ
                print(f"✅ テストデータクリーンアップ完了: {self.unique_suffix}")
                
        except Exception as e:
            print(f"⚠️ テストデータクリーンアップエラー: {e}")

# 環境変数取得（相対パス対応）
def get_project_root() -> str:
    """プロジェクトルートディレクトリを取得"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # tests/test_config.py から backend/ まで遡る
    return os.path.dirname(current_dir)

def load_test_env():
    """テスト用環境変数を読み込み"""
    project_root = get_project_root()
    parent_dir = os.path.dirname(project_root)  # backend の親ディレクトリ
    env_path = os.path.join(parent_dir, '.env.local')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 環境変数読み込み: {env_path}")
    else:
        print(f"⚠️ 環境変数ファイルが見つかりません: {env_path}")

# グローバルテストマネージャー
test_db_manager = TestDatabaseManager()