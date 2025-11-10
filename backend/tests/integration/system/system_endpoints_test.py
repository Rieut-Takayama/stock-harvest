"""
システム基盤エンドポイントの統合テスト
スライス1: システム基盤の完全なテスト

実行コマンド:
cd backend && python3 -m pytest tests/integration/system/system_endpoints_test.py -v
"""

import pytest
import asyncio
import sys
import os

# プロジェクトルートを動的に取得してパスを追加
def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # tests/integration/system/ -> tests/ -> backend/
    return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

sys.path.append(get_project_root())

from tests.utils.MilestoneTracker import MilestoneTracker
from tests.utils.db_test_helper import DatabaseTestHelper
from tests.utils.api_test_helper import APITestHelper

class TestSystemEndpoints:
    
    def setup_method(self):
        """各テストメソッドの前処理"""
        self.tracker = MilestoneTracker()
        self.db_helper = DatabaseTestHelper()
        self.api_helper = APITestHelper()
        self.db = None
    
    def teardown_method(self):
        """各テストメソッドの後処理"""
        async def cleanup():
            if self.db:
                await self.db_helper.cleanup_test_data(self.db)
                await self.db_helper.disconnect_db()
            await self.api_helper.cleanup_client()
        
        asyncio.run(cleanup())
        self.tracker.summary()
    
    @pytest.mark.asyncio
    async def test_system_info_endpoint_success(self):
        """
        GET /api/system/info - システム情報取得の正常ケース
        """
        self.tracker.set_operation("システム情報取得テスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # APIサーバー起動確認
        self.tracker.set_operation("APIサーバー確認")
        try:
            # まずヘルスチェック
            health_response = await self.api_helper.get("/health")
            assert health_response["status_code"] == 200, "APIサーバーが起動していません"
            self.tracker.mark("APIサーバー起動確認")
        except Exception as e:
            pytest.fail(f"APIサーバーに接続できません。サーバーを起動してください: {e}")
        
        # システム情報取得
        self.tracker.set_operation("システム情報API呼び出し")
        response = await self.api_helper.get("/api/system/info")
        self.tracker.mark("APIレスポンス受信")
        
        # レスポンス検証
        self.tracker.set_operation("レスポンス検証")
        
        # ステータスコード確認
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        # JSON構造確認
        assert response["json"] is not None, "レスポンスにJSONが含まれていません"
        
        json_data = response["json"]
        required_fields = ["version", "status", "statusDisplay", "databaseStatus", "lastUpdated"]
        
        for field in required_fields:
            assert field in json_data, f"必須フィールド '{field}' がレスポンスにありません"
        
        # データ型確認
        assert isinstance(json_data["version"], str), "version は文字列である必要があります"
        assert len(json_data["version"]) > 0, "version は空文字列ではいけません"
        assert isinstance(json_data["status"], str), "status は文字列である必要があります"
        assert json_data["status"] in ["healthy", "degraded", "down"], f"無効なステータス: {json_data['status']}"
        
        # より詳細な検証
        assert "databaseStatus" in json_data, "databaseStatus フィールドが必要です"
        assert json_data["databaseStatus"] in ["connected", "disconnected", "error"], f"無効なdatabaseStatus: {json_data['databaseStatus']}"
        
        self.tracker.mark("レスポンス検証完了")
        
        # データベース確認
        self.tracker.set_operation("データベース確認")
        db_record = await self.db.fetch_one("SELECT * FROM system_info WHERE id = 1")
        assert db_record is not None, "システム情報がデータベースに存在しません"
        self.tracker.mark("データベース確認完了")
        
        print(f"✅ システム情報取得成功: {json_data['version']}")
    
    @pytest.mark.asyncio
    async def test_system_status_endpoint_success(self):
        """
        GET /api/system/status - ヘルスチェックの正常ケース
        """
        self.tracker.set_operation("ヘルスチェックテスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # ヘルスチェック実行
        self.tracker.set_operation("ヘルスチェックAPI呼び出し")
        response = await self.api_helper.get("/api/system/status")
        self.tracker.mark("APIレスポンス受信")
        
        # レスポンス検証
        self.tracker.set_operation("レスポンス検証")
        
        # 正常なシステムではステータスコード200を期待
        expected_status = 200  # healthy な状態
        assert response["status_code"] in [200, 503], f"Expected 200 or 503, got {response['status_code']}"
        
        # JSON構造確認
        assert response["json"] is not None, "レスポンスにJSONが含まれていません"
        
        json_data = response["json"]
        required_fields = ["healthy", "status", "message", "checks"]
        
        for field in required_fields:
            assert field in json_data, f"必須フィールド '{field}' がレスポンスにありません"
        
        # データ型確認
        assert isinstance(json_data["healthy"], bool), "healthy はブール値である必要があります"
        assert isinstance(json_data["status"], str), "status は文字列である必要があります"
        assert json_data["status"] in ["healthy", "unhealthy"], f"無効なステータス: {json_data['status']}"
        assert isinstance(json_data["checks"], dict), "checks は辞書である必要があります"
        
        self.tracker.mark("レスポンス検証完了")
        
        # ヘルスチェック詳細確認
        self.tracker.set_operation("ヘルス詳細確認")
        checks = json_data["checks"]
        assert "database" in checks, "データベースチェックが含まれていません"
        
        db_check = checks["database"]
        assert "status" in db_check, "データベースチェックにステータスが含まれていません"
        assert db_check["status"] in ["pass", "fail"], f"無効なデータベースチェックステータス: {db_check['status']}"
        
        self.tracker.mark("ヘルス詳細確認完了")
        
        print(f"✅ ヘルスチェック成功: {json_data['status']}")
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """
        API エラーハンドリングテスト
        """
        self.tracker.set_operation("エラーハンドリングテスト開始")
        self.tracker.mark("テスト開始")
        
        # 存在しないエンドポイントテスト
        self.tracker.set_operation("存在しないエンドポイントテスト")
        response = await self.api_helper.get("/api/system/nonexistent")
        self.tracker.mark("存在しないエンドポイントレスポンス受信")
        
        # 404エラーを期待
        assert response["status_code"] == 404, f"Expected 404, got {response['status_code']}"
        
        self.tracker.mark("エラーハンドリング確認完了")
        
        print("✅ エラーハンドリングテスト完了")

# テスト実行スクリプト
if __name__ == "__main__":
    import subprocess
    
    print("🧪 システム基盤統合テスト実行")
    print("=" * 50)
    
    # テスト実行
    # 現在のファイルのディレクトリからプロジェクトルートを取得
    backend_dir = get_project_root()
    
    result = subprocess.run([
        "python3", "-m", "pytest", 
        "tests/integration/system/system_endpoints_test.py", 
        "-v", "--tb=short"
    ], cwd=backend_dir)
    
    if result.returncode == 0:
        print("\n✅ すべてのテストが成功しました")
    else:
        print(f"\n❌ テストが失敗しました (終了コード: {result.returncode})")
    
    exit(result.returncode)