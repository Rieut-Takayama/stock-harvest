"""
システム情報エンドポイントの統合テスト
スライス1: システム情報API (C3: GET /api/system/info)

実行コマンド:
cd backend && python3 -m pytest tests/integration/system/system_info_test.py -v
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

class TestSystemInfoEndpoint:

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
                await self.db_helper.disconnect_db()
            await self.api_helper.cleanup_client()

        asyncio.run(cleanup())
        self.tracker.summary()

    @pytest.mark.asyncio
    async def test_system_info_endpoint_success(self):
        """
        GET /api/system/info - システム情報取得の正常ケース
        API仕様書準拠: version, lastUpdated, status, statusDisplay の4フィールドを検証
        """
        self.tracker.set_operation("システム情報取得テスト開始")
        self.tracker.mark("テスト開始")

        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")

        # システム情報API呼び出し
        self.tracker.set_operation("システム情報API呼び出し")
        response = await self.api_helper.get("/api/system/info")
        self.tracker.mark("APIレスポンス受信")

        # レスポンス検証
        self.tracker.set_operation("レスポンス検証")

        # ステータスコード確認
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"

        # JSON構造確認
        assert response["json"] is not None, "レスポンスにJSONが含まれていません"

        system_info = response["json"]

        # API仕様書準拠: 必須フィールド確認（4フィールドのみ）
        required_fields = ["version", "lastUpdated", "status", "statusDisplay"]

        for field in required_fields:
            assert field in system_info, f"必須フィールド '{field}' がレスポンスにありません"

        # データ型確認
        assert isinstance(system_info["version"], str), "version は文字列である必要があります"
        assert system_info["version"].startswith("v"), "version は 'v' で始まる必要があります"
        assert len(system_info["version"]) > 0, "version は空文字列ではいけません"

        assert isinstance(system_info["lastUpdated"], str), "lastUpdated は文字列である必要があります"
        assert len(system_info["lastUpdated"]) > 0, "lastUpdated は空文字列ではいけません"

        assert isinstance(system_info["status"], str), "status は文字列である必要があります"
        valid_statuses = ["operational", "degraded", "down"]
        assert system_info["status"] in valid_statuses, f"status は {valid_statuses} のいずれかである必要があります"

        assert isinstance(system_info["statusDisplay"], str), "statusDisplay は文字列である必要があります"
        assert len(system_info["statusDisplay"]) > 0, "statusDisplay は空文字列ではいけません"

        self.tracker.mark("レスポンス検証完了")

        # データベース確認
        self.tracker.set_operation("データベース確認")
        db_record = await self.db.fetch_one("SELECT version, status, last_updated, status_display FROM system_info WHERE id = 1")
        assert db_record is not None, "システム情報がデータベースに存在しません"
        assert db_record["version"] == system_info["version"], "データベースのバージョンとAPIレスポンスが一致しません"
        assert db_record["status"] == system_info["status"], "データベースのステータスとAPIレスポンスが一致しません"
        self.tracker.mark("データベース確認完了")

        print(f"✅ システム情報取得成功: version={system_info['version']}, status={system_info['status']}")

    @pytest.mark.asyncio
    async def test_system_info_response_format_validation(self):
        """
        GET /api/system/info - レスポンスフォーマットの厳密な検証
        """
        self.tracker.set_operation("レスポンスフォーマット検証テスト開始")
        self.tracker.mark("テスト開始")

        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")

        # システム情報取得
        self.tracker.set_operation("システム情報取得")
        response = await self.api_helper.get("/api/system/info")
        assert response["status_code"] == 200, "システム情報取得が失敗しました"
        self.tracker.mark("システム情報取得完了")

        # レスポンス検証
        self.tracker.set_operation("フォーマット検証")
        system_info = response["json"]

        # バージョン形式の検証（例: v1.0.0）
        version = system_info["version"]
        assert version[0] == "v", "バージョンは 'v' で始まる必要があります"
        version_parts = version[1:].split(".")
        assert len(version_parts) >= 2, "バージョンは少なくとも 'v1.0' 形式である必要があります"

        # lastUpdatedのISO 8601形式検証
        last_updated = system_info["lastUpdated"]
        from datetime import datetime
        try:
            datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"lastUpdated が ISO 8601 形式ではありません: {last_updated}")

        # statusの値検証
        status = system_info["status"]
        assert status in ["operational", "degraded", "down"], f"無効なステータス値: {status}"

        # statusDisplayの日本語表示検証
        status_display = system_info["statusDisplay"]
        assert len(status_display) > 0, "statusDisplay が空です"
        assert len(status_display) <= 100, "statusDisplay が長すぎます（100文字以下）"

        self.tracker.mark("フォーマット検証完了")

        print(f"✅ レスポンスフォーマット検証成功")

    @pytest.mark.asyncio
    async def test_system_info_consistency_across_requests(self):
        """
        GET /api/system/info - 複数リクエスト間の一貫性テスト
        """
        self.tracker.set_operation("一貫性テスト開始")
        self.tracker.mark("テスト開始")

        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")

        # 1回目のリクエスト
        self.tracker.set_operation("1回目のリクエスト")
        response1 = await self.api_helper.get("/api/system/info")
        assert response1["status_code"] == 200, "1回目のリクエストが失敗しました"
        info1 = response1["json"]
        self.tracker.mark("1回目のレスポンス受信")

        # 2回目のリクエスト
        self.tracker.set_operation("2回目のリクエスト")
        response2 = await self.api_helper.get("/api/system/info")
        assert response2["status_code"] == 200, "2回目のリクエストが失敗しました"
        info2 = response2["json"]
        self.tracker.mark("2回目のレスポンス受信")

        # 一貫性検証
        self.tracker.set_operation("一貫性検証")
        assert info1["version"] == info2["version"], "バージョンが異なります"
        assert info1["status"] == info2["status"], "ステータスが異なります"
        assert info1["statusDisplay"] == info2["statusDisplay"], "ステータス表示が異なります"
        # lastUpdatedは同じ秒内なら同じはず（DBの精度による）
        self.tracker.mark("一貫性検証完了")

        print(f"✅ 一貫性テスト成功: version={info1['version']}")

# テスト実行スクリプト
if __name__ == "__main__":
    import subprocess

    print("🧪 システム情報API統合テスト実行")
    print("=" * 50)

    # テスト実行
    backend_dir = get_project_root()

    result = subprocess.run([
        "python3", "-m", "pytest",
        "tests/integration/system/system_info_test.py",
        "-v", "--tb=short"
    ], cwd=backend_dir)

    if result.returncode == 0:
        print("\n✅ すべてのテストが成功しました")
    else:
        print(f"\n❌ テストが失敗しました (終了コード: {result.returncode})")

    exit(result.returncode)
