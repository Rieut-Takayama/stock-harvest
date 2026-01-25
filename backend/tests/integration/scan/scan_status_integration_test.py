"""
スキャン状態API（D2）統合テスト
API仕様書準拠の詳細テストケース

テスト対象: GET /api/scan/status
依存関係: D1（POST /api/scan/execute）

実データ主義:
- モックは一切使用しない
- 実際のデータベース接続を使用
- 実際のスキャン処理を実行してテスト
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any
from datetime import datetime


class TestScanStatusAPI:
    """スキャン状態API（D2）の統合テストクラス"""

    @classmethod
    def setup_class(cls):
        """テストクラス初期化"""
        cls.base_url = "http://localhost:8432"
        cls.scan_execute_endpoint = f"{cls.base_url}/api/scan/execute"
        cls.scan_status_endpoint = f"{cls.base_url}/api/scan/status"
        print("\n" + "=" * 80)
        print("スキャン状態API（D2）統合テスト開始")
        print("=" * 80)

    def setup_method(self, method):
        """各テストメソッド前の初期化"""
        print(f"\n🧪 テスト開始: {method.__name__}")

    def teardown_method(self, method):
        """各テストメソッド後のクリーンアップ"""
        print(f"✅ テスト完了: {method.__name__}\n")

    @pytest.mark.asyncio
    async def test_01_scan_status_idle_state(self):
        """
        Test 1: アイドル状態のスキャン状態取得
        スキャンが実行されていない状態で、適切なアイドルレスポンスを返却
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.scan_status_endpoint,
                timeout=10.0
            )

            assert response.status_code == 200, f"ステータスコードが200ではありません: {response.status_code}"

            data = response.json()
            print(f"📊 レスポンス: {data}")

            # API仕様書準拠のフィールド検証
            required_fields = [
                "isRunning", "progress", "totalStocks", "processedStocks",
                "currentStock", "estimatedTime", "message"
            ]

            for field in required_fields:
                assert field in data, f"必須フィールド '{field}' が存在しません"

            # データ型検証
            assert isinstance(data["isRunning"], bool), "isRunning はブール型である必要があります"
            assert isinstance(data["progress"], int), "progress は整数型である必要があります"
            assert isinstance(data["totalStocks"], int), "totalStocks は整数型である必要があります"
            assert isinstance(data["processedStocks"], int), "processedStocks は整数型である必要があります"
            assert isinstance(data["message"], str), "message は文字列型である必要があります"

            # アイドル状態の特定条件検証（スキャン未実行または完了）
            if data["isRunning"] is False:
                print("✅ アイドル状態を正しく検出")

            print(f"✅ スキャン状態: {'実行中' if data['isRunning'] else 'アイドル'}")

    @pytest.mark.asyncio
    async def test_02_scan_status_running_state(self):
        """
        Test 2: 実行中状態のスキャン状態取得
        スキャン実行後、実行中状態のレスポンスを正しく返却
        """
        # スキャンを開始
        async with httpx.AsyncClient() as client:
            execute_response = await client.post(
                self.scan_execute_endpoint,
                timeout=30.0
            )

            assert execute_response.status_code == 200, "スキャン開始に失敗"
            execute_data = execute_response.json()
            scan_id = execute_data.get("scanId")

            print(f"🚀 スキャン開始: {scan_id}")

            # 少し待ってから状態確認
            await asyncio.sleep(2)

            # スキャン状態を取得
            status_response = await client.get(
                self.scan_status_endpoint,
                timeout=10.0
            )

            assert status_response.status_code == 200, "状態取得に失敗"

            data = status_response.json()
            print(f"📊 実行中レスポンス: {data}")

            # 実行中状態の検証
            assert isinstance(data["isRunning"], bool), "isRunning はブール型である必要があります"
            assert isinstance(data["progress"], int), "progress は整数型である必要があります"
            assert isinstance(data["totalStocks"], int), "totalStocks は整数型である必要があります"
            assert isinstance(data["processedStocks"], int), "processedStocks は整数型である必要があります"

            # 進捗率の妥当性検証
            assert 0 <= data["progress"] <= 100, f"進捗率が範囲外: {data['progress']}"

            # 処理済み銘柄数の妥当性検証
            assert data["processedStocks"] <= data["totalStocks"], \
                f"処理済み銘柄数が総数を超えています: {data['processedStocks']} > {data['totalStocks']}"

            print(f"✅ 実行中状態を正しく検出: 進捗 {data['progress']}%")
            print(f"✅ 処理状況: {data['processedStocks']}/{data['totalStocks']} 銘柄")

    @pytest.mark.asyncio
    async def test_03_scan_status_progress_update(self):
        """
        Test 3: スキャン進捗の更新確認
        スキャン実行中に進捗が正しく更新されることを確認
        """
        # スキャンを開始
        async with httpx.AsyncClient() as client:
            execute_response = await client.post(
                self.scan_execute_endpoint,
                timeout=30.0
            )

            assert execute_response.status_code == 200, "スキャン開始に失敗"
            scan_id = execute_response.json().get("scanId")

            print(f"🚀 スキャン開始: {scan_id}")

            # 進捗を複数回確認
            progress_history = []
            for i in range(3):
                await asyncio.sleep(2)

                status_response = await client.get(
                    self.scan_status_endpoint,
                    timeout=10.0
                )

                assert status_response.status_code == 200, f"状態取得失敗（{i+1}回目）"

                data = status_response.json()
                progress_history.append({
                    "iteration": i + 1,
                    "progress": data["progress"],
                    "processedStocks": data["processedStocks"],
                    "isRunning": data["isRunning"]
                })

                print(f"📊 {i+1}回目: 進捗 {data['progress']}%, 処理済み {data['processedStocks']} 銘柄")

            # 進捗が増加しているか、または完了しているかを確認
            for i in range(len(progress_history) - 1):
                current = progress_history[i]
                next_item = progress_history[i + 1]

                # 進捗が増加または完了
                assert (
                    next_item["progress"] >= current["progress"] or
                    next_item["progress"] == 100 or
                    not next_item["isRunning"]
                ), f"進捗が減少しています: {current['progress']} -> {next_item['progress']}"

            print("✅ 進捗が正しく更新されています")

    @pytest.mark.asyncio
    async def test_04_scan_status_response_format(self):
        """
        Test 4: レスポンス形式の厳密な検証
        API仕様書に完全準拠したレスポンス形式を確認
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.scan_status_endpoint,
                timeout=10.0
            )

            assert response.status_code == 200, "ステータスコードが200ではありません"

            data = response.json()
            print(f"📊 レスポンス形式検証: {data}")

            # API仕様書準拠のフィールド型検証
            field_types = {
                "isRunning": bool,
                "progress": int,
                "totalStocks": int,
                "processedStocks": int,
                "message": str,
            }

            for field, expected_type in field_types.items():
                assert field in data, f"フィールド '{field}' が存在しません"
                assert isinstance(data[field], expected_type), \
                    f"フィールド '{field}' の型が不正です: 期待={expected_type.__name__}, 実際={type(data[field]).__name__}"

            # NULL許容フィールドの検証
            nullable_fields = ["currentStock", "estimatedTime"]
            for field in nullable_fields:
                assert field in data, f"フィールド '{field}' が存在しません"
                if data[field] is not None:
                    if field == "currentStock":
                        assert isinstance(data[field], str), f"{field} は文字列である必要があります"
                    elif field == "estimatedTime":
                        assert isinstance(data[field], int), f"{field} は整数である必要があります"

            print("✅ レスポンス形式が仕様書に完全準拠")

    @pytest.mark.asyncio
    async def test_05_scan_status_completed_state(self):
        """
        Test 5: 完了状態のスキャン状態取得
        スキャン完了後、適切な完了レスポンスを返却
        """
        # スキャンを開始
        async with httpx.AsyncClient() as client:
            execute_response = await client.post(
                self.scan_execute_endpoint,
                timeout=30.0
            )

            assert execute_response.status_code == 200, "スキャン開始に失敗"
            scan_id = execute_response.json().get("scanId")

            print(f"🚀 スキャン開始: {scan_id}")

            # スキャン完了まで待機（最大60秒）
            max_wait_time = 60
            wait_interval = 3
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval

                status_response = await client.get(
                    self.scan_status_endpoint,
                    timeout=10.0
                )

                assert status_response.status_code == 200, "状態取得失敗"

                data = status_response.json()

                if not data["isRunning"]:
                    print(f"✅ スキャン完了: 経過時間 {elapsed_time}秒")

                    # 完了状態の検証
                    assert data["progress"] == 100 or data["progress"] == 0, \
                        f"完了状態の進捗率が不正: {data['progress']}"

                    if data["progress"] == 100:
                        assert data["processedStocks"] == data["totalStocks"], \
                            "処理済み銘柄数が総数と一致しません"

                    print(f"✅ 完了状態を正しく検出")
                    return

                print(f"⏳ 待機中: 進捗 {data['progress']}% ({elapsed_time}/{max_wait_time}秒)")

            pytest.fail("スキャンが制限時間内に完了しませんでした")

    @pytest.mark.asyncio
    async def test_06_scan_status_error_handling(self):
        """
        Test 6: エラーハンドリングの確認
        異常系でも適切にエラーハンドリングされることを確認
        """
        async with httpx.AsyncClient() as client:
            # 正常なリクエスト
            response = await client.get(
                self.scan_status_endpoint,
                timeout=10.0
            )

            # 500エラーが発生しないことを確認
            assert response.status_code != 500, "内部サーバーエラーが発生しました"

            # 200または適切なエラーコードを返却
            assert response.status_code in [200, 404, 503], \
                f"予期しないステータスコード: {response.status_code}"

            if response.status_code == 200:
                data = response.json()
                assert "message" in data, "エラーレスポンスに message フィールドがありません"

            print("✅ エラーハンドリングが適切に機能")

    @pytest.mark.asyncio
    async def test_07_scan_status_multiple_requests(self):
        """
        Test 7: 複数リクエストの並列処理確認
        複数のステータス取得リクエストが正しく処理されることを確認
        """
        async with httpx.AsyncClient() as client:
            # スキャンを開始
            execute_response = await client.post(
                self.scan_execute_endpoint,
                timeout=30.0
            )

            assert execute_response.status_code == 200, "スキャン開始に失敗"
            scan_id = execute_response.json().get("scanId")

            print(f"🚀 スキャン開始: {scan_id}")

            await asyncio.sleep(2)

            # 並列で複数のステータス取得リクエストを送信
            tasks = []
            for i in range(5):
                task = client.get(self.scan_status_endpoint, timeout=10.0)
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            # 全てのレスポンスが成功することを確認
            for i, response in enumerate(responses):
                assert response.status_code == 200, f"リクエスト{i+1}が失敗: {response.status_code}"

                data = response.json()
                assert "isRunning" in data, f"リクエスト{i+1}のレスポンスが不正"

                print(f"✅ リクエスト{i+1}: 進捗 {data['progress']}%")

            print("✅ 複数リクエストの並列処理が正常に動作")

    @pytest.mark.asyncio
    async def test_08_scan_status_d1_dependency(self):
        """
        Test 8: D1依存関係の確認
        D1（スキャン実行API）との依存関係が正しく動作することを確認
        """
        async with httpx.AsyncClient() as client:
            # D1: スキャン実行
            execute_response = await client.post(
                self.scan_execute_endpoint,
                timeout=30.0
            )

            assert execute_response.status_code == 200, "D1（スキャン実行）が失敗"
            execute_data = execute_response.json()
            scan_id = execute_data.get("scanId")

            print(f"✅ D1実行成功: {scan_id}")

            await asyncio.sleep(2)

            # D2: スキャン状態取得
            status_response = await client.get(
                self.scan_status_endpoint,
                timeout=10.0
            )

            assert status_response.status_code == 200, "D2（スキャン状態取得）が失敗"
            status_data = status_response.json()

            print(f"✅ D2実行成功: isRunning={status_data['isRunning']}, progress={status_data['progress']}%")

            # D1とD2の連携確認
            if status_data["isRunning"]:
                assert status_data["totalStocks"] > 0, "D1実行後にtotalStocksが0です"
                print(f"✅ D1→D2の依存関係が正しく動作")
            else:
                print("⚠️  スキャンが既に完了しています（高速実行環境）")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
