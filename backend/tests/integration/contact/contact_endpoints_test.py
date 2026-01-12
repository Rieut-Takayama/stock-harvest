"""
お問い合わせエンドポイントの統合テスト
スライス1: お問い合わせ機能の完全なテスト

実行コマンド:
cd backend && python3 -m pytest tests/integration/contact/contact_endpoints_test.py -v
"""

import pytest
import asyncio
import sys
import os

# プロジェクトルートを動的に取得してパスを追加
def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # tests/integration/contact/ -> tests/ -> backend/
    return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

sys.path.append(get_project_root())

from tests.utils.MilestoneTracker import MilestoneTracker
from tests.utils.db_test_helper import DatabaseTestHelper
from tests.utils.api_test_helper import APITestHelper

class TestContactEndpoints:
    
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
    async def test_faq_endpoint_success(self):
        """
        GET /api/contact/faq - FAQ一覧取得の正常ケース
        """
        self.tracker.set_operation("FAQ取得テスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # FAQ取得
        self.tracker.set_operation("FAQ API呼び出し")
        response = await self.api_helper.get("/api/contact/faq")
        self.tracker.mark("APIレスポンス受信")
        
        # レスポンス検証
        self.tracker.set_operation("レスポンス検証")
        
        # ステータスコード確認
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        # JSON構造確認
        assert response["json"] is not None, "レスポンスにJSONが含まれていません"
        assert isinstance(response["json"], list), "FAQレスポンスは配列である必要があります"
        
        faq_list = response["json"]
        
        if len(faq_list) > 0:
            # 最初のFAQ項目を検証
            first_faq = faq_list[0]
            required_fields = ["id", "category", "question", "answer", "tags"]
            
            for field in required_fields:
                assert field in first_faq, f"FAQ項目に必須フィールド '{field}' がありません"
            
            # データ型確認
            assert isinstance(first_faq["id"], str), "FAQ ID は文字列である必要があります"
            assert len(first_faq["id"]) > 0, "FAQ ID は空文字列ではいけません"
            assert isinstance(first_faq["category"], str), "FAQ category は文字列である必要があります"
            assert len(first_faq["category"]) > 0, "FAQ category は空文字列ではいけません"
            assert isinstance(first_faq["question"], str), "FAQ question は文字列である必要があります"
            assert len(first_faq["question"]) > 0, "FAQ question は空文字列ではいけません"
            assert isinstance(first_faq["answer"], str), "FAQ answer は文字列である必要があります"
            assert len(first_faq["answer"]) > 0, "FAQ answer は空文字列ではいけません"
            assert isinstance(first_faq["tags"], list), "FAQ tags は配列である必要があります"
        
        self.tracker.mark("レスポンス検証完了")
        
        # データベース確認
        self.tracker.set_operation("データベース確認")
        db_count = await self.db.fetch_one("SELECT COUNT(*) as count FROM faq WHERE is_active = true")
        assert db_count["count"] == len(faq_list), "データベースのFAQ件数とAPIレスポンス件数が一致しません"
        self.tracker.mark("データベース確認完了")
        
        print(f"✅ FAQ取得成功: {len(faq_list)}件")
    
    @pytest.mark.asyncio
    async def test_contact_submit_success(self):
        """
        POST /api/contact/submit - お問い合わせ送信の正常ケース
        """
        self.tracker.set_operation("お問い合わせ送信テスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # ユニークなテストデータ準備
        self.tracker.set_operation("テストデータ準備")
        base_data = {
            "type": "technical",
            "subject": "テストお問い合わせ",
            "content": "これはテスト用のお問い合わせ内容です。",
            "email": "test@example.com",
            "priority": "medium"
        }
        test_data = self.db_helper.generate_unique_test_data(base_data)
        self.tracker.mark("テストデータ準備完了")
        
        # お問い合わせ送信
        self.tracker.set_operation("お問い合わせAPI呼び出し")
        response = await self.api_helper.post("/api/contact/submit", test_data)
        self.tracker.mark("APIレスポンス受信")
        
        # レスポンス検証
        self.tracker.set_operation("レスポンス検証")
        
        # ステータスコード確認
        assert response["status_code"] == 200, f"Expected 200, got {response['status_code']}"
        
        # JSON構造確認
        assert response["json"] is not None, "レスポンスにJSONが含まれていません"
        
        json_data = response["json"]
        required_fields = ["success", "message", "inquiryId", "submittedAt"]
        
        for field in required_fields:
            assert field in json_data, f"必須フィールド '{field}' がレスポンスにありません"
        
        # データ型・値確認
        assert json_data["success"] is True, "success は True である必要があります"
        assert isinstance(json_data["message"], str), "message は文字列である必要があります"
        assert isinstance(json_data["inquiryId"], str), "inquiryId は文字列である必要があります"
        assert isinstance(json_data["submittedAt"], str), "submittedAt は文字列である必要があります"
        
        inquiry_id = json_data["inquiryId"]
        self.tracker.mark("レスポンス検証完了")
        
        # データベース確認
        self.tracker.set_operation("データベース確認")
        db_record = await self.db.fetch_one(
            "SELECT * FROM contact_inquiries WHERE id = :id",
            {"id": inquiry_id}
        )
        assert db_record is not None, "お問い合わせがデータベースに保存されていません"
        assert db_record["type"] == test_data["type"], "保存されたタイプが一致しません"
        assert db_record["email"] == test_data["email"], "保存されたメールアドレスが一致しません"
        self.tracker.mark("データベース確認完了")
        
        print(f"✅ お問い合わせ送信成功: {inquiry_id}")
    
    @pytest.mark.asyncio  
    async def test_contact_submit_validation_errors(self):
        """
        POST /api/contact/submit - バリデーションエラーケース
        """
        self.tracker.set_operation("バリデーションエラーテスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # 空の件名でテスト
        self.tracker.set_operation("空件名テスト")
        invalid_data = {
            "type": "technical",
            "subject": "",  # 空の件名
            "content": "テスト内容",
            "email": "test@example.com",
            "priority": "medium"
        }
        
        response = await self.api_helper.post("/api/contact/submit", invalid_data)
        # FastAPIのPydanticバリデーションは422を返す
        assert response["status_code"] in [400, 422], f"Empty subject should return 400 or 422, got {response['status_code']}"
        self.tracker.mark("空件名テスト完了")

        # 空の内容でテスト
        self.tracker.set_operation("空内容テスト")
        invalid_data["subject"] = "テスト件名"
        invalid_data["content"] = ""  # 空の内容

        response = await self.api_helper.post("/api/contact/submit", invalid_data)
        # FastAPIのPydanticバリデーションは422を返す
        assert response["status_code"] in [400, 422], f"Empty content should return 400 or 422, got {response['status_code']}"
        self.tracker.mark("空内容テスト完了")
        
        print("✅ バリデーションエラーテスト完了")
    
    @pytest.mark.asyncio
    async def test_contact_integration_flow(self):
        """
        お問い合わせ機能の統合フローテスト
        FAQ取得 → お問い合わせ送信の流れ
        """
        self.tracker.set_operation("統合フローテスト開始")
        self.tracker.mark("テスト開始")
        
        # データベース準備
        self.tracker.set_operation("データベース準備")
        self.db = await self.db_helper.setup_test_environment()
        self.tracker.mark("データベース準備完了")
        
        # 1. FAQ取得
        self.tracker.set_operation("FAQ取得ステップ")
        faq_response = await self.api_helper.get("/api/contact/faq")
        assert faq_response["status_code"] == 200, "FAQ取得が失敗しました"
        self.tracker.mark("FAQ取得完了")
        
        # 2. お問い合わせ送信
        self.tracker.set_operation("お問い合わせ送信ステップ")
        test_data = self.db_helper.generate_unique_test_data({
            "type": "technical",
            "subject": "統合テストからのお問い合わせ",
            "content": "FAQ を確認した後でのお問い合わせです。",
            "email": "integration-test@example.com",
            "priority": "low"
        })
        
        submit_response = await self.api_helper.post("/api/contact/submit", test_data)
        assert submit_response["status_code"] == 200, "お問い合わせ送信が失敗しました"
        self.tracker.mark("お問い合わせ送信完了")
        
        # 3. 結果検証
        self.tracker.set_operation("結果検証ステップ")
        inquiry_id = submit_response["json"]["inquiryId"]
        
        # データベースで確認
        db_record = await self.db.fetch_one(
            "SELECT * FROM contact_inquiries WHERE id = :id",
            {"id": inquiry_id}
        )
        assert db_record is not None, "お問い合わせがデータベースに保存されていません"
        assert db_record["status"] == "open", "お問い合わせステータスが正しくありません"
        self.tracker.mark("結果検証完了")
        
        print(f"✅ 統合フローテスト完了: FAQ {len(faq_response['json'])}件 → お問い合わせ {inquiry_id}")

# テスト実行スクリプト
if __name__ == "__main__":
    import subprocess
    
    print("🧪 お問い合わせ機能統合テスト実行")
    print("=" * 50)
    
    # テスト実行
    # 現在のファイルのディレクトリからプロジェクトルートを取得
    backend_dir = get_project_root()
    
    result = subprocess.run([
        "python3", "-m", "pytest", 
        "tests/integration/contact/contact_endpoints_test.py", 
        "-v", "--tb=short"
    ], cwd=backend_dir)
    
    if result.returncode == 0:
        print("\n✅ すべてのテストが成功しました")
    else:
        print(f"\n❌ テストが失敗しました (終了コード: {result.returncode})")
    
    exit(result.returncode)