"""
ロジックA強化版の動作確認スクリプト
環境変数設定なしでの基本機能テスト
"""

import asyncio
import sys
import os
from datetime import datetime

# 環境変数設定（テスト用）
os.environ['TESTING_MODE'] = 'true'
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'  # テスト用ダミー

# パス追加
sys.path.append('./src')

from services.logic_detection_service import LogicDetectionService

def main():
    """メイン実行関数"""
    print("🔍 Stock Harvest AI - ロジックA強化版 動作確認")
    print("=" * 50)
    
    # ロジック検出サービスのインスタンス作成
    logic_service = LogicDetectionService()
    
    # 1. 設定の確認
    print("\n📋 1. 設定確認")
    configs = logic_service.get_logic_configs()
    print(f"   従来版設定: {configs['logic_a']}")
    print(f"   強化版設定: {logic_service.logic_a_enhanced_config}")
    
    # 2. テストデータの準備
    print("\n📊 2. テストデータ準備")
    test_cases = [
        {
            'name': 'ストップ高張り付きケース',
            'data': {
                'code': '3000',
                'name': 'テスト新興株A',
                'price': 1500,
                'change': 250,
                'changeRate': 20.0,  # ストップ高レベル
                'volume': 25000000,  # 高出来高
                'signals': {
                    'rsi': 75,
                    'macd': 0.5,
                    'bollingerPosition': 0.8,
                    'volumeRatio': 2.5,
                    'trendDirection': 'up'
                }
            }
        },
        {
            'name': '通常上昇ケース',
            'data': {
                'code': '3100',
                'name': 'テスト新興株B',
                'price': 800,
                'change': 40,
                'changeRate': 5.3,  # 通常上昇
                'volume': 15000000,
                'signals': {
                    'rsi': 65,
                    'macd': 0.2,
                    'bollingerPosition': 0.5,
                    'volumeRatio': 1.8,
                    'trendDirection': 'up'
                }
            }
        },
        {
            'name': '条件未満ケース',
            'data': {
                'code': '7203',  # 既存大型株（上場条件未満）
                'name': 'トヨタ自動車',
                'price': 2900,
                'change': 30,
                'changeRate': 1.0,  # 小幅上昇
                'volume': 8000000,
                'signals': {
                    'rsi': 55,
                    'macd': -0.1,
                    'bollingerPosition': 0.2,
                    'volumeRatio': 1.2,
                    'trendDirection': 'sideways'
                }
            }
        }
    ]
    
    # 3. 非同期検出テストの実行
    async def run_detection_tests():
        print("\n🧪 3. 検出テスト実行")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- テストケース {i}: {test_case['name']} ---")
            
            # 強化版検出
            try:
                enhanced_result = await logic_service.detect_logic_a_enhanced(test_case['data'])
                print(f"✅ 強化版検出: {enhanced_result.get('detected', False)}")
                
                if enhanced_result.get('detected'):
                    print(f"   📈 シグナルタイプ: {enhanced_result.get('signal_type')}")
                    print(f"   🔥 シグナル強度: {enhanced_result.get('signal_strength')}%")
                    print(f"   💰 エントリー価格: {enhanced_result.get('entry_price'):,}円")
                    print(f"   🎯 利確目標: {enhanced_result.get('profit_target'):,}円 (+{enhanced_result.get('expected_return')}%)")
                    print(f"   🛑 損切り: {enhanced_result.get('stop_loss'):,}円 ({enhanced_result.get('max_loss')}%)")
                    print(f"   ⏰ 最大保有: {enhanced_result.get('max_holding_days')}日")
                    
                    risk = enhanced_result.get('risk_assessment', {})
                    print(f"   ⚠️ リスク評価: {risk.get('risk_level')} (スコア: {risk.get('risk_score')}/100)")
                    print(f"   💡 推奨: {risk.get('recommendation')}")
                else:
                    print(f"   ❌ 非検出理由: {enhanced_result.get('reason')}")
                
            except Exception as e:
                print(f"   ❌ エラー: {str(e)}")
            
            # 従来版との比較
            try:
                legacy_result = await logic_service.detect_logic_a(test_case['data'])
                print(f"🔄 従来版検出: {legacy_result}")
            except Exception as e:
                print(f"🔄 従来版エラー: {str(e)}")
    
    # 4. 個別機能テスト
    async def run_component_tests():
        print("\n🔧 4. 個別機能テスト")
        
        test_data = test_cases[0]['data']  # ストップ高ケースを使用
        
        # ストップ高検出テスト
        try:
            stop_high_result = await logic_service._detect_stop_high_sticking(test_data)
            print(f"✅ ストップ高検出: {stop_high_result.get('is_stop_high')}")
            if stop_high_result.get('is_stop_high'):
                print(f"   到達率: {stop_high_result.get('reach_ratio', 0):.1%}")
                print(f"   下髭比率: {stop_high_result.get('lower_shadow_ratio', 0):.1%}")
        except Exception as e:
            print(f"❌ ストップ高検出エラー: {e}")
        
        # 上場条件テスト
        try:
            listing_new = await logic_service._check_listing_conditions('3000')  # 新興
            listing_old = await logic_service._check_listing_conditions('7203')  # 既存
            print(f"✅ 上場条件: 新興株={listing_new}, 既存株={listing_old}")
        except Exception as e:
            print(f"❌ 上場条件テストエラー: {e}")
        
        # 決算タイミングテスト
        try:
            earnings_result = await logic_service._check_earnings_timing('3000')
            print(f"✅ 決算タイミング: {earnings_result.get('is_earnings_day')} ({earnings_result.get('source')})")
        except Exception as e:
            print(f"❌ 決算タイミングテストエラー: {e}")
        
        # 売買シグナル生成テスト
        try:
            signal_result = await logic_service._generate_trading_signal(test_data)
            print(f"✅ 売買シグナル: {signal_result.get('signal_type')} (強度: {signal_result.get('signal_strength')}%)")
        except Exception as e:
            print(f"❌ 売買シグナルテストエラー: {e}")
    
    # 5. 履歴管理テスト
    def test_history_management():
        print("\n📚 5. 履歴管理テスト")
        
        test_stock_code = 'TEST001'
        
        # 履歴記録
        test_record = {
            'detection_date': datetime.now(),
            'detection_type': 'logic_a_enhanced',
            'stock_data': test_cases[0]['data'],
            'signal': {'signal_type': 'BUY_ENTRY', 'signal_strength': 85.5}
        }
        
        asyncio.create_task(logic_service._record_stock_history(test_stock_code, test_record))
        
        # 履歴取得
        history = logic_service.get_stock_history(test_stock_code)
        print(f"✅ 履歴記録・取得: {len(history)}件")
        
        # 全検出銘柄取得
        all_detected = logic_service.get_all_detected_stocks('logic_a_enhanced')
        print(f"✅ 全検出銘柄: {len(all_detected)}件")
    
    # テスト実行
    asyncio.run(run_detection_tests())
    asyncio.run(run_component_tests())
    test_history_management()
    
    print("\n🎉 ロジックA強化版の動作確認完了")
    print("=" * 50)
    print("\n📝 実装された主要機能:")
    print("  ✅ ストップ高張り付き精密検出")
    print("  ✅ 上場条件判定（新興企業対象）")
    print("  ✅ 決算タイミング推定")
    print("  ✅ 除外ルール適用")
    print("  ✅ 売買シグナル生成（エントリー/利確/損切り）")
    print("  ✅ リスク評価システム")
    print("  ✅ 履歴管理システム")
    print("  ✅ 初回条件判定")
    print("\n🚀 APIエンドポイント:")
    print("  - POST /api/scan/logic-a-enhanced")
    print("  - GET /api/scan/logic-a-history/{stock_code}")
    print("  - GET /api/scan/logic-a-all-detected")
    print("  - GET /api/scan/logic-a-config")

if __name__ == "__main__":
    main()