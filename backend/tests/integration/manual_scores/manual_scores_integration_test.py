"""
手動スコア評価機能統合テスト
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

from backend.tests.utils.MilestoneTracker import MilestoneTracker
from backend.src.database.config import get_database_connection, connect_db
from backend.src.services.manual_scores_service import ManualScoresService, ManualScoresServiceError


class ManualScoresIntegrationTest:
    """手動スコア評価機能統合テスト"""
    
    def __init__(self):
        """テスト初期化"""
        self.service = ManualScoresService()
        self.test_evaluations = []  # テスト中に作成したスコア評価IDを記録
        self.tracker = MilestoneTracker()
        print("=== 手動スコア評価機能統合テスト開始 ===")
    
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
    
    async def test_create_score_evaluation(self) -> Dict[str, Any]:
        """テスト1: スコア評価作成"""
        self.tracker.setOperation("スコア評価作成テスト")
        
        try:
            # テストデータ準備
            test_data = {
                'stock_code': '9984',
                'stock_name': 'ソフトバンクグループ',
                'score': 'A+',
                'logic_type': 'logic_b',
                'scan_result_id': f'scan-result-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'evaluation_reason': '黒字転換後の強いモメンタムと技術革新への注力。AIビジネスの拡大が期待される。',
                'confidence_level': 'high',
                'price_at_evaluation': 5840.0,
                'ai_score_before': 'B',
                'follow_up_required': True,
                'follow_up_date': datetime.now() + timedelta(days=30),
                'tags': ['AI銘柄', '黒字転換', 'モメンタム'],
                'is_learning_case': True
            }
            
            self.tracker.mark("テストデータ準備完了")
            
            # スコア評価作成実行
            result = await self.service.create_score_evaluation(test_data)
            
            # 結果検証
            assert result['success'] == True, "作成に失敗"
            assert 'score_id' in result, "score_idが返されていない"
            assert result['evaluation']['stock_code'] == test_data['stock_code'], "銘柄コードが一致しない"
            assert result['evaluation']['score'] == test_data['score'], "スコアが一致しない"
            assert result['evaluation']['logic_type'] == test_data['logic_type'], "ロジックタイプが一致しない"
            
            # テスト用に記録
            self.test_evaluations.append(result['score_id'])
            
            self.tracker.mark("作成結果検証完了")
            print("✅ テスト1: スコア評価作成 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト1: スコア評価作成 - 失敗: {e}")
            raise
    
    async def test_get_score_evaluation(self, stock_code: str) -> Dict[str, Any]:
        """テスト2: スコア評価取得"""
        self.tracker.setOperation("スコア評価取得テスト")
        
        try:
            # スコア評価取得実行
            result = await self.service.get_score_evaluation(stock_code, 'logic_b')
            
            # 結果検証
            assert result['success'] == True, "取得に失敗"
            assert result['evaluation'] is not None, "評価データが取得されていない"
            
            evaluation = result['evaluation']
            assert evaluation['stock_code'] == stock_code, "銘柄コードが一致しない"
            assert evaluation['logic_type'] == 'logic_b', "ロジックタイプが一致しない"
            assert 'score_change_history' in evaluation, "スコア変更履歴が含まれていない"
            assert 'tags' in evaluation, "タグが含まれていない"
            
            self.tracker.mark("取得結果検証完了")
            print("✅ テスト2: スコア評価取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト2: スコア評価取得 - 失敗: {e}")
            raise
    
    async def test_update_score_evaluation(self, score_id: str):
        """テスト3: スコア評価更新"""
        self.tracker.setOperation("スコア評価更新テスト")
        
        try:
            # 更新データ
            update_data = {
                'score': 'S',
                'evaluation_reason': '期待を上回る業績発表により格上げ。革新的なAI技術の商用化が進展。',
                'confidence_level': 'high',
                'ai_score_after': 'A+',
                'performance_validation': {
                    'actual_performance_1w': 15.2,
                    'expected_performance_1w': 8.5,
                    'validation_date': datetime.now().isoformat(),
                    'validation_notes': '予想を大幅に上回るパフォーマンス'
                },
                'tags': ['AI銘柄', '黒字転換', 'モメンタム', '格上げ'],
                'is_learning_case': True,
                'change_reason': '業績発表によるポジティブサプライズのため格上げ'
            }
            
            # 更新実行
            result = await self.service.update_score_evaluation(score_id, update_data)
            
            # 結果検証
            assert result['success'] == True, "更新に失敗"
            assert result['score_id'] == score_id, "score_idが一致しない"
            assert 'updated_fields' in result, "updated_fieldsが返されていない"
            
            # 更新内容の検証
            updated_evaluation = result['evaluation']
            assert updated_evaluation['score'] == 'S', "スコアが更新されていない"
            assert updated_evaluation['ai_score_after'] == 'A+', "AI後スコアが更新されていない"
            
            # 変更履歴の確認
            change_history = updated_evaluation['score_change_history']
            assert len(change_history) >= 1, "変更履歴が記録されていない"
            
            self.tracker.mark("更新結果検証完了")
            print("✅ テスト3: スコア評価更新 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト3: スコア評価更新 - 失敗: {e}")
            raise
    
    async def test_search_score_evaluations(self):
        """テスト4: スコア評価検索"""
        self.tracker.setOperation("スコア評価検索テスト")
        
        try:
            # 検索パラメータ
            search_params = {
                'logic_type': 'logic_b',
                'confidence_level': 'high',
                'is_learning_case': True,
                'page': 1,
                'limit': 10
            }
            
            # 検索実行
            result = await self.service.search_score_evaluations(search_params)
            
            # 結果検証
            assert result['success'] == True, "検索に失敗"
            assert 'evaluations' in result, "evaluationsが返されていない"
            assert 'pagination' in result, "paginationが返されていない"
            assert result['pagination']['total'] >= 1, "作成したスコア評価が検索されない"
            
            # 詳細検証
            found_evaluation = None
            for evaluation in result['evaluations']:
                if evaluation['stock_code'] == '9984':
                    found_evaluation = evaluation
                    break
            
            assert found_evaluation is not None, "作成したスコア評価が見つからない"
            assert found_evaluation['logic_type'] == 'logic_b', "ロジックタイプが一致しない"
            assert found_evaluation['is_learning_case'] == True, "学習事例フラグが一致しない"
            
            self.tracker.mark("検索結果検証完了")
            print("✅ テスト4: スコア評価検索 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト4: スコア評価検索 - 失敗: {e}")
            raise
    
    async def test_get_score_history(self, stock_code: str):
        """テスト5: スコア評価履歴取得"""
        self.tracker.setOperation("スコア評価履歴取得テスト")
        
        try:
            # 履歴取得実行（コンパクト形式）
            result = await self.service.get_score_history(stock_code, compact=True)
            
            # 結果検証
            assert result['success'] == True, "履歴取得に失敗"
            assert 'history' in result, "historyが返されていない"
            assert 'summary' in result, "summaryが返されていない"
            assert len(result['history']) >= 1, "履歴が記録されていない"
            
            # サマリー検証
            summary = result['summary']
            assert 'latest_score' in summary, "最新スコアが含まれていない"
            assert 'evaluation_count' in summary, "評価回数が含まれていない"
            assert 'scores_distribution' in summary, "スコア分布が含まれていない"
            
            self.tracker.mark("履歴検証完了")
            print("✅ テスト5: スコア評価履歴取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト5: スコア評価履歴取得 - 失敗: {e}")
            raise
    
    async def test_get_ai_calculation_status(self, stock_code: str):
        """テスト6: AI スコア計算状態取得"""
        self.tracker.setOperation("AI スコア計算状態取得テスト")
        
        try:
            # AI計算状態取得実行
            result = await self.service.get_ai_calculation_status(stock_code)
            
            # 結果検証
            assert result['success'] == True, "AI計算状態取得に失敗"
            assert 'status' in result, "statusが返されていない"
            
            status = result['status']
            assert 'is_calculating' in status, "is_calculatingが含まれていない"
            assert 'stock_code' in status, "stock_codeが含まれていない"
            assert status['stock_code'] == stock_code, "銘柄コードが一致しない"
            
            self.tracker.mark("AI計算状態検証完了")
            print("✅ テスト6: AI スコア計算状態取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト6: AI スコア計算状態取得 - 失敗: {e}")
            raise
    
    async def test_get_evaluation_statistics(self):
        """テスト7: スコア評価統計取得"""
        self.tracker.setOperation("スコア評価統計取得テスト")
        
        try:
            # 統計取得実行
            result = await self.service.get_evaluation_statistics()
            
            # 結果検証
            assert result['success'] == True, "統計取得に失敗"
            assert 'statistics' in result, "statisticsが返されていない"
            
            stats = result['statistics']
            assert 'total_evaluations' in stats, "総評価件数が含まれていない"
            assert 'score_distribution' in stats, "スコア分布が含まれていない"
            assert 'confidence_distribution' in stats, "確信度分布が含まれていない"
            assert 'logic_type_distribution' in stats, "ロジック別分布が含まれていない"
            assert 'quality_metrics' in stats, "品質指標が含まれていない"
            
            assert stats['total_evaluations'] >= 1, "作成したスコア評価がカウントされていない"
            
            # 品質指標の確認
            quality_metrics = stats['quality_metrics']
            assert 'high_confidence_ratio' in quality_metrics, "高確信度率が含まれていない"
            assert 'learning_cases_ratio' in quality_metrics, "学習事例率が含まれていない"
            
            self.tracker.mark("統計検証完了")
            print("✅ テスト7: スコア評価統計取得 - 成功")
            return result
            
        except Exception as e:
            print(f"❌ テスト7: スコア評価統計取得 - 失敗: {e}")
            raise
    
    async def test_multiple_evaluations_and_superseding(self):
        """テスト8: 複数評価と置換テスト"""
        self.tracker.setOperation("複数評価と置換テスト")
        
        try:
            # 同一銘柄・同一ロジックで2つ目の評価を作成
            second_evaluation_data = {
                'stock_code': '9984',
                'stock_name': 'ソフトバンクグループ',
                'score': 'B',
                'logic_type': 'logic_b',
                'evaluation_reason': '新しい評価による置換テスト',
                'confidence_level': 'medium',
                'price_at_evaluation': 5920.0,
                'change_reason': '評価基準の見直しによる再評価'
            }
            
            # 2つ目の評価作成
            result = await self.service.create_score_evaluation(second_evaluation_data)
            
            # 結果検証
            assert result['success'] == True, "2つ目の評価作成に失敗"
            second_score_id = result['score_id']
            self.test_evaluations.append(second_score_id)
            
            # 最新の評価を取得して、新しい評価がアクティブであることを確認
            latest_result = await self.service.get_score_evaluation('9984', 'logic_b')
            assert latest_result['evaluation']['id'] == second_score_id, "新しい評価がアクティブになっていない"
            assert latest_result['evaluation']['score'] == 'B', "新しいスコアが反映されていない"
            
            self.tracker.mark("置換動作検証完了")
            print("✅ テスト8: 複数評価と置換テスト - 成功")
            
        except Exception as e:
            print(f"❌ テスト8: 複数評価と置換テスト - 失敗: {e}")
            raise
    
    async def test_validation_errors(self):
        """テスト9: バリデーションエラーテスト"""
        self.tracker.setOperation("バリデーションエラーテスト")
        
        try:
            # 不正なデータでスコア評価作成を試行
            invalid_data = {
                'stock_code': '999',  # 不正な銘柄コード
                'stock_name': '',     # 空の銘柄名
                'score': 'Z',         # 不正なスコア
                'logic_type': 'invalid_logic',  # 不正なロジックタイプ
                'evaluation_reason': '',  # 空の評価理由
                'confidence_level': 'invalid',  # 不正な確信度
                'price_at_evaluation': -100.0   # 負の価格
            }
            
            # エラーが発生することを確認
            try:
                await self.service.create_score_evaluation(invalid_data)
                assert False, "バリデーションエラーが発生しなかった"
            except ManualScoresServiceError as e:
                assert e.code == "VALIDATION_ERROR", f"期待されるエラーコードと異なる: {e.code}"
            
            # 更新時のバリデーションエラーもテスト
            try:
                await self.service.update_score_evaluation("invalid-id", {
                    'score': 'Z',  # 不正なスコア
                    # change_reason が必須だが含まれていない
                })
                assert False, "更新時のバリデーションエラーが発生しなかった"
            except ManualScoresServiceError as e:
                assert e.code in ["VALIDATION_ERROR", "INVALID_ID"], f"期待されるエラーコードと異なる: {e.code}"
            
            self.tracker.mark("バリデーションエラー検証完了")
            print("✅ テスト9: バリデーションエラーテスト - 成功")
            
        except Exception as e:
            print(f"❌ テスト9: バリデーションエラーテスト - 失敗: {e}")
            raise
    
    async def cleanup_test_data(self):
        """テストデータクリーンアップ"""
        self.tracker.setOperation("テストデータクリーンアップ")
        
        try:
            # 作成したスコア評価をアーカイブ状態に変更
            for score_id in self.test_evaluations:
                try:
                    await self.service.update_score_evaluation(score_id, {
                        'status': 'archived',
                        'change_reason': 'テスト終了によるアーカイブ'
                    })
                    print(f"スコア評価 {score_id} をアーカイブしました")
                except Exception as e:
                    print(f"スコア評価 {score_id} のクリーンアップでエラー: {e}")
            
            self.tracker.mark("クリーンアップ完了")
            print("✅ テストデータクリーンアップ完了")
            
        except Exception as e:
            print(f"⚠️ テストデータクリーンアップでエラー: {e}")
    
    async def run_all_tests(self):
        """全テスト実行"""
        try:
            # テスト環境セットアップ
            await self.setup_test_environment()
            
            # テスト1: スコア評価作成
            create_result = await self.test_create_score_evaluation()
            score_id = create_result['score_id']
            
            # テスト2: スコア評価取得
            await self.test_get_score_evaluation('9984')
            
            # テスト3: スコア評価更新
            await self.test_update_score_evaluation(score_id)
            
            # テスト4: スコア評価検索
            await self.test_search_score_evaluations()
            
            # テスト5: スコア評価履歴取得
            await self.test_get_score_history('9984')
            
            # テスト6: AI スコア計算状態取得
            await self.test_get_ai_calculation_status('9984')
            
            # テスト7: スコア評価統計取得
            await self.test_get_evaluation_statistics()
            
            # テスト8: 複数評価と置換テスト
            await self.test_multiple_evaluations_and_superseding()
            
            # テスト9: バリデーションエラーテスト
            await self.test_validation_errors()
            
            # クリーンアップ
            await self.cleanup_test_data()
            
            # 全体結果
            self.tracker.summary()
            print("\n🎉 手動スコア評価機能統合テスト - 全て成功!")
            return True
            
        except Exception as e:
            print(f"\n💥 手動スコア評価機能統合テスト - 失敗: {e}")
            self.tracker.summary()
            return False


async def main():
    """メイン実行関数"""
    # 環境変数設定
    os.environ['DATABASE_URL'] = 'sqlite:///./test_database.db'
    
    # テスト実行
    test = ManualScoresIntegrationTest()
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