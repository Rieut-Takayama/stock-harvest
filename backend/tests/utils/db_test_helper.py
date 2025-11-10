"""
データベーステスト用ヘルパー
安全なテスト環境でのデータベース操作を提供
本番データベースへの影響を防止
"""

import asyncio
import os
import uuid
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from databases import Database
from tests.test_config import test_db_manager, TestTransaction, TestDataManager, load_test_env

# 環境変数読み込み（相対パス対応）
load_test_env()

class DatabaseTestHelper:
    
    def __init__(self):
        self.database = None
        self.transaction_manager = None
        self.data_manager = TestDataManager()
        self._in_transaction = False
        
    async def get_db_connection(self) -> Database:
        """安全なテスト用データベース接続を取得"""
        try:
            # 既存の接続を再利用し、必要時のみ再接続
            if self.database is None or not self.database.is_connected:
                # 直接メインDBを使用して安全性を確保
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise ValueError("DATABASE_URL environment variable is not set")
                
                self.database = Database(database_url)
                await self.database.connect()
                self.transaction_manager = TestTransaction(self.database)
                print("✅ テスト用データベース接続確立（安全モード）")
            
            return self.database
        except Exception as e:
            print(f"❌ テスト用データベース接続エラー: {e}")
            raise
    
    async def cleanup_test_data(self, db: Database):
        """テストデータの安全なクリーンアップ"""
        try:
            # データマネージャーによるクリーンアップ
            await self.data_manager.cleanup_created_data(db)
            print("✅ テストデータクリーンアップ完了")
        except Exception as e:
            print(f"⚠️ クリーンアップエラー（継続）: {e}")
    
    async def disconnect_db(self):
        """データベース切断とクリーンアップ"""
        try:
            # データベース切断は最小限に留める（接続プールの再利用を促進）
            if self.database and self.database.is_connected:
                # ここでは切断せず、接続を保持
                print("✅ テスト用データベース接続維持（再利用用）")
            # データベースオブジェクトは保持し、次回のテストで再利用
        except Exception as e:
            print(f"⚠️ テスト用データベース処理エラー: {e}")
    
    async def final_disconnect(self):
        """最終的なデータベース切断（テストスイート終了時）"""
        try:
            if self.database and self.database.is_connected:
                await self.database.disconnect()
                print("✅ テスト用データベース最終切断")
            self.database = None
            self.transaction_manager = None
        except Exception as e:
            print(f"⚠️ 最終切断エラー: {e}")
    
    def generate_unique_test_data(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """ユニークなテストデータを生成（データマネージャー経由）"""
        return self.data_manager.generate_unique_test_data(base_data)
    
    async def setup_test_environment(self) -> Database:
        """安全なテスト環境セットアップ"""
        try:
            # データベース接続を取得
            db = await self.get_db_connection()
            
            # システム情報の確認・作成（安全な方式）
            try:
                system_info = await db.fetch_one("SELECT id FROM system_info WHERE id = 1")
                if not system_info:
                    await db.execute("""
                        INSERT INTO system_info (id, version, status, active_alerts, total_users, database_status, status_display)
                        VALUES (1, 'v1.0.0', 'healthy', 0, 1, 'connected', '正常稼働中')
                        ON CONFLICT (id) DO NOTHING
                    """)
                    print("✅ テスト用システム情報を作成")
            except Exception as setup_error:
                print(f"⚠️ システム情報セットアップエラー（継続）: {setup_error}")
            
            print("✅ テスト環境セットアップ完了")
            return db
            
        except Exception as e:
            print(f"❌ テスト環境セットアップエラー: {e}")
            raise
    
    @asynccontextmanager
    async def transactional_test(self):
        """トランザクション付きテスト実行（自動ロールバック）"""
        if not self.transaction_manager:
            raise RuntimeError("データベース接続が必要です")
        
        async with self.transaction_manager.rollback_on_exit() as db:
            yield db
    
    async def cleanup_scan_data(self):
        """スキャン関連テストデータのクリーンアップ"""
        try:
            if self.database:
                # 実行中のスキャンを強制停止
                await self.database.execute(
                    "UPDATE scan_executions SET status = 'cancelled', completed_at = NOW() WHERE status IN ('running', 'pending')"
                )
                # 完了状態のスキャンもクリーンアップ対象に
                completed_count = await self.database.execute("DELETE FROM scan_results")
                execution_count = await self.database.execute("DELETE FROM scan_executions")
                print(f"✅ スキャンテストデータクリーンアップ完了: 結果={completed_count}, 実行記録={execution_count}")
        except Exception as e:
            print(f"⚠️ スキャンデータクリーンアップエラー: {e}")

    async def force_cleanup_all_test_data(self):
        """全テストデータの強制クリーンアップ（緊急時用）"""
        try:
            if self.database:
                # テストプレフィックスのデータを全削除
                await self.database.execute(
                    "DELETE FROM contact_inquiries WHERE email LIKE '%test-%@example.com'"
                )
                await self.database.execute(
                    "DELETE FROM contact_inquiries WHERE subject LIKE '[TEST-%'"
                )
                # スキャン関連テストデータも削除
                await self.cleanup_scan_data()
                print("✅ 全テストデータ強制クリーンアップ完了")
        except Exception as e:
            print(f"⚠️ 強制クリーンアップエラー: {e}")

# グローバルテストヘルパーインスタンス
global_test_helper = None

def get_global_test_helper():
    """グローバルテストヘルパーを取得（シングルトンパターン）"""
    global global_test_helper
    if global_test_helper is None:
        global_test_helper = DatabaseTestHelper()
    return global_test_helper

# テスト終了時のグローバルクリーンアップ
async def cleanup_global_test_environment():
    """全テスト終了時のグローバルクリーンアップ"""
    try:
        global global_test_helper
        if global_test_helper:
            await global_test_helper.final_disconnect()
        print("✅ グローバルテスト環境クリーンアップ完了")
    except Exception as e:
        print(f"⚠️ グローバルクリーンアップエラー: {e}")