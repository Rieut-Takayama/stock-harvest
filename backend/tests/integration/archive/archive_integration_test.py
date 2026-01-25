"""
銘柄アーカイブ機能統合テスト
Stock Harvest AI - 実データ環境での統合テスト
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# プロジェクトルートをPythonパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

from tests.utils.MilestoneTracker import MilestoneTracker
from src.database.config import get_database_connection, connect_db
from src.services.archive_service import ArchiveService, ArchiveServiceError


class ArchiveIntegrationTest:
    """銘柄アーカイブ機能統合テスト"""
    
    def __init__(self):
        """テスト初期化"""
        self.service = ArchiveService()
        self.test_archives = []  # テスト中に作成したアーカイブIDを記録
        self.tracker = MilestoneTracker()
        print("=== 銘柄アーカイブ機能統合テスト開始 ===")
    
    async def setup_test_environment(self):
        """テスト環境セットアップ"""
        self.tracker.setOperation("テスト環境セットアップ")
        
        try:
            # データベース接続確認
            connected = await connect_db()
            if not connected:
                raise Exception("データベース接続失敗")
            
            self.tracker.mark("データベース接続完了")
            print("✅ テスト環境セットアップ完了")
            
        except Exception as e:
            print(f"❌ テスト環境セットアップ失敗: {e}")
            raise
    
    async def test_create_archive_entry(self) -> Dict[str, Any]:
        """テスト1: アーカイブエントリ作成"""
        self.tracker.setOperation("アーカイブエントリ作成テスト")
        
        try:
            # テストデータ準備
            test_data = {
                'stock_code': '7203',
                'stock_name': 'トヨタ自動車',
                'logic_type': 'logic_a',
                'scan_id': f'scan-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'price_at_detection': 2450.0,
                'volume_at_detection': 1500000,
                'market_cap_at_detection': 35000000000.0,
                'technical_signals_snapshot': {
                    'rsi': 65.5,
                    'macd': 12.3,
                    'volume_ratio': 1.8
                },
                'logic_specific_data': {
                    'listing_years': 2.5,
                    'earnings_quarter': 'Q3',
                    'stop_high_price': 2500.0
                },
                'manual_score': 'A',
                'manual_score_reason': '強い上昇トレンドと良好なファンダメンタルズ',
                'lessons_learned': 'ストップ高後の継続性に注目'
            }
            
            self.tracker.mark("テストデータ準備完了")
            
            # アーカイブエントリ作成実行
            result = await self.service.create_archive_entry(test_data)
            
            # 結果検証
            assert result['success'] == True, "作成に失敗"
            assert 'archive_id' in result, "archive_idが返されていない"
            assert result['archive']['stock_code'] == test_data['stock_code'], "銘柄コードが一致しない"
            assert result['archive']['logic_type'] == test_data['logic_type'], "ロジックタイプが一致しない"
            
            # テスト用に記録
            self.test_archives.append(result['archive_id'])
            
            self.tracker.mark("作成結果検証完了")
            print("✅ テスト1: アーカイブエントリ作成 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト1: アーカイブエントリ作成 - 失敗: {e}")
            raise
    
    async def test_search_archives(self) -> Dict[str, Any]:
        """テスト2: アーカイブ検索"""
        self.tracker.setOperation("アーカイブ検索テスト")
        
        try:
            # 検索パラメータ
            search_params = {
                'stock_code': '7203',
                'logic_type': 'logic_a',
                'page': 1,
                'limit': 10
            }
            
            # 検索実行
            result = await self.service.search_archives(search_params)
            
            # 結果検証
            assert result['success'] == True, "検索に失敗"
            assert 'archives' in result, "archivesが返されていない"
            assert 'pagination' in result, "paginationが返されていない"
            assert result['pagination']['total'] >= 1, "作成したアーカイブが検索されない"
            
            # 詳細検証
            found_archive = None
            for archive in result['archives']:
                if archive['stock_code'] == '7203':
                    found_archive = archive
                    break
            
            assert found_archive is not None, "作成したアーカイブが見つからない"
            assert found_archive['logic_type'] == 'logic_a', "ロジックタイプが一致しない"
            
            self.tracker.mark("検索結果検証完了")
            print("✅ テスト2: アーカイブ検索 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト2: アーカイブ検索 - 失敗: {e}")
            raise
    
    async def test_update_archive_performance(self, archive_id: str):
        """テスト3: アーカイブパフォーマンス更新"""
        self.tracker.setOperation("アーカイブパフォーマンス更新テスト")
        
        try:
            # 更新データ
            update_data = {
                'performance_after_1d': 5.2,
                'performance_after_1w': 12.8,
                'performance_after_1m': 25.4,
                'max_gain': 28.6,
                'max_loss': -3.1,
                'outcome_classification': 'success',
                'trade_execution': {
                    'entry_date': datetime.now().isoformat(),
                    'entry_price': 2460.0,
                    'exit_date': (datetime.now() + timedelta(days=30)).isoformat(),
                    'exit_price': 3085.0,
                    'profit_rate': 25.4,
                    'holding_days': 30
                },
                'lessons_learned': '予想を上回るパフォーマンス。ロジックAの有効性確認。',
                'follow_up_notes': '次回同様条件の銘柄での検証を実施予定。'
            }
            
            # 更新実行
            result = await self.service.update_archive_performance(archive_id, update_data)
            
            # 結果検証
            assert result['success'] == True, "更新に失敗"
            assert result['archive_id'] == archive_id, "archive_idが一致しない"
            assert 'updated_fields' in result, "updated_fieldsが返されていない"
            assert len(result['updated_fields']) > 0, "更新されたフィールドが記録されていない"
            
            # 更新内容の検証
            updated_archive = result['archive']
            assert updated_archive['performance_after_1m'] == 25.4, "1ヶ月後パフォーマンスが更新されていない"
            assert updated_archive['outcome_classification'] == 'success', "結果分類が更新されていない"
            
            self.tracker.mark("更新結果検証完了")
            print("✅ テスト3: アーカイブパフォーマンス更新 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト3: アーカイブパフォーマンス更新 - 失敗: {e}")
            raise
    
    async def test_get_archive_details(self, archive_id: str):
        """テスト4: アーカイブ詳細取得"""
        self.tracker.setOperation("アーカイブ詳細取得テスト")
        
        try:
            # 詳細取得実行
            result = await self.service.get_archive_details(archive_id)
            
            # 結果検証
            assert result['success'] == True, "取得に失敗"
            assert 'archive' in result, "archiveが返されていない"
            
            archive = result['archive']
            assert archive['id'] == archive_id, "IDが一致しない"
            assert archive['stock_code'] == '7203', "銘柄コードが一致しない"
            assert 'technical_signals_snapshot' in archive, "テクニカル指標スナップショットが含まれていない"
            assert 'logic_specific_data' in archive, "ロジック固有データが含まれていない"
            
            self.tracker.mark("詳細取得検証完了")
            print("✅ テスト4: アーカイブ詳細取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト4: アーカイブ詳細取得 - 失敗: {e}")
            raise
    
    async def test_get_performance_statistics(self):
        """テスト5: パフォーマンス統計取得"""
        self.tracker.setOperation("パフォーマンス統計取得テスト")
        
        try:
            # 統計取得実行
            result = await self.service.get_performance_statistics()
            
            # 結果検証
            assert result['success'] == True, "統計取得に失敗"
            assert 'statistics' in result, "statisticsが返されていない"
            
            stats = result['statistics']
            assert 'total_archived' in stats, "総アーカイブ件数が含まれていない"
            assert 'logic_a_count' in stats, "ロジックA件数が含まれていない"
            assert 'logic_b_count' in stats, "ロジックB件数が含まれていない"
            assert 'success_rate' in stats, "成功率が含まれていない"
            assert 'manual_score_distribution' in stats, "手動スコア分布が含まれていない"
            
            assert stats['total_archived'] >= 1, "作成したアーカイブがカウントされていない"
            
            self.tracker.mark("統計検証完了")
            print("✅ テスト5: パフォーマンス統計取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト5: パフォーマンス統計取得 - 失敗: {e}")
            raise
    
    async def test_export_to_csv(self):
        """テスト6: CSV エクスポート"""
        self.tracker.setOperation("CSV エクスポートテスト")
        
        try:
            # エクスポート条件
            search_params = {
                'logic_type': 'logic_a',
                'page': 1,
                'limit': 100
            }
            
            export_options = {
                'date_format': '%Y-%m-%d %H:%M:%S',
                'decimal_places': 2,
                'include_fields': [
                    'stock_code', 'stock_name', 'logic_type', 'detection_date',
                    'price_at_detection', 'performance_after_1m', 'outcome_classification'
                ]
            }
            
            # CSV エクスポート実行
            csv_content = await self.service.export_to_csv(search_params, export_options)
            
            # 結果検証
            assert csv_content != "", "CSVコンテンツが空"
            assert '銘柄コード' in csv_content, "ヘッダーが含まれていない"
            assert '7203' in csv_content, "作成したデータが含まれていない"
            
            # CSV の行数チェック
            lines = csv_content.strip().split('\n')
            assert len(lines) >= 2, "ヘッダー + データ行が含まれていない"  # ヘッダー + 最低1行のデータ
            
            self.tracker.mark("CSV内容検証完了")
            print("✅ テスト6: CSV エクスポート - 成功")
            return csv_content
            
        except Exception as e:
            print(f"❌ テスト6: CSV エクスポート - 失敗: {e}")
            raise
    
    async def test_delete_archive(self, archive_id: str):
        """テスト7: アーカイブ削除（論理削除）"""
        self.tracker.setOperation("アーカイブ削除テスト")
        
        try:
            # 削除実行
            result = await self.service.delete_archive(archive_id)
            
            # 結果検証
            assert result['success'] == True, "削除に失敗"
            assert result['archive_id'] == archive_id, "archive_idが一致しない"
            
            # 削除後の状態確認
            try:
                deleted_result = await self.service.get_archive_details(archive_id)
                # 削除済みアーカイブへのアクセス時はサービスエラーが発生するはず
                assert False, "削除されたアーカイブが取得できてしまう"
            except ArchiveServiceError as e:
                assert e.code == "DELETED", "削除エラーコードが期待と異なる"
            
            self.tracker.mark("削除状態検証完了")
            print("✅ テスト7: アーカイブ削除 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト7: アーカイブ削除 - 失敗: {e}")
            raise
    
    async def test_validation_errors(self):
        """テスト8: バリデーションエラーテスト"""
        self.tracker.setOperation("バリデーションエラーテスト")
        
        try:
            # 不正なデータでアーカイブ作成を試行
            invalid_data = {
                'stock_code': '999',  # 不正な銘柄コード
                'stock_name': '',     # 空の銘柄名
                'logic_type': 'invalid_logic',  # 不正なロジックタイプ
                'scan_id': '',        # 空のスキャンID
                'price_at_detection': -100.0,  # 負の価格
                'volume_at_detection': -1000   # 負の出来高
            }
            
            # エラーが発生することを確認
            try:
                await self.service.create_archive_entry(invalid_data)
                assert False, "バリデーションエラーが発生しなかった"
            except ArchiveServiceError as e:
                assert e.code == "VALIDATION_ERROR", f"期待されるエラーコードと異なる: {e.code}"
            
            self.tracker.mark("バリデーションエラー検証完了")
            print("✅ テスト8: バリデーションエラーテスト - 成功")
            
        except Exception as e:
            print(f"❌ テスト8: バリデーションエラーテスト - 失敗: {e}")
            raise
    
    async def cleanup_test_data(self):
        """テストデータクリーンアップ"""
        self.tracker.setOperation("テストデータクリーンアップ")
        
        try:
            # 作成したアーカイブをクリーンアップ（論理削除済みなので実際は不要）
            for archive_id in self.test_archives:
                try:
                    # 強制的に物理削除は今回は実装しないため、ログのみ
                    print(f"テストアーカイブ {archive_id} は論理削除済み")
                except Exception as e:
                    print(f"アーカイブ {archive_id} のクリーンアップでエラー: {e}")
            
            self.tracker.mark("クリーンアップ完了")
            print("✅ テストデータクリーンアップ完了")
            
        except Exception as e:
            print(f"⚠️ テストデータクリーンアップでエラー: {e}")
    
    async def run_all_tests(self):
        """全テスト実行"""
        try:
            # テスト環境セットアップ
            await self.setup_test_environment()
            
            # テスト1: アーカイブエントリ作成
            create_result = await self.test_create_archive_entry()
            archive_id = create_result['archive_id']
            
            # テスト2: アーカイブ検索
            await self.test_search_archives()
            
            # テスト3: アーカイブパフォーマンス更新
            await self.test_update_archive_performance(archive_id)
            
            # テスト4: アーカイブ詳細取得
            await self.test_get_archive_details(archive_id)
            
            # テスト5: パフォーマンス統計取得
            await self.test_get_performance_statistics()
            
            # テスト6: CSV エクスポート
            await self.test_export_to_csv()
            
            # テスト7: アーカイブ削除
            await self.test_delete_archive(archive_id)
            
            # テスト8: バリデーションエラーテスト
            await self.test_validation_errors()
            
            # クリーンアップ
            await self.cleanup_test_data()
            
            # 全体結果
            self.tracker.summary()
            print("\n🎉 銘柄アーカイブ機能統合テスト - 全て成功!")
            return True
            
        except Exception as e:
            print(f"\n💥 銘柄アーカイブ機能統合テスト - 失敗: {e}")
            self.tracker.summary()
            return False


async def main():
    """メイン実行関数"""
    # 環境変数設定
    os.environ['DATABASE_URL'] = 'sqlite:///./test_database.db'
    
    # テスト実行
    test = ArchiveIntegrationTest()
    success = await test.run_all_tests()
    
    if success:
        print("\n✅ 全てのテストが正常に完了しました")
        return 0
    else:
        print("\n❌ テストが失敗しました")
        return 1


if __name__ == '__main__':
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)