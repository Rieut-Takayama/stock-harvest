#!/usr/bin/env python3
"""
ロジックB強化版（黒字転換銘柄精密検出）の動作テスト
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.services.logic_detection_service import LogicDetectionService


async def test_logic_b_enhanced():
    """ロジックB強化版の動作テスト"""
    print("🔍 ロジックB強化版（黒字転換銘柄精密検出）テスト開始\n")
    
    # ロジック検出サービスを初期化
    logic_service = LogicDetectionService()
    
    # テスト用の株価データ
    test_stock_data = {
        'code': '3456',
        'name': 'パルコデジタル',
        'price': 1250.0,
        'changeRate': 3.2,
        'volume': 18500000,
        'signals': {
            'rsi': 65.3,
            'macd': 0.05,
            'bollingerPosition': -0.2,
            'trendDirection': 'up',
            'volumeRatio': 2.1,
            'ma5': 1215.0,
            'ma25': 1180.0
        }
    }
    
    print("📊 テスト対象銘柄:")
    print(f"   銘柄コード: {test_stock_data['code']}")
    print(f"   銘柄名: {test_stock_data['name']}")
    print(f"   現在価格: {test_stock_data['price']:,.0f}円")
    print(f"   変化率: {test_stock_data['changeRate']:+.1f}%")
    print(f"   出来高: {test_stock_data['volume']:,}株")
    print(f"   RSI: {test_stock_data['signals']['rsi']:.1f}")
    print()
    
    # ロジックB強化版テスト
    print("🎯 ロジックB強化版検出テスト...")
    result = await logic_service.detect_logic_b_enhanced(test_stock_data)
    
    print("📈 検出結果:")
    print(f"   検出成功: {'✅' if result['detected'] else '❌'}")
    
    if result['detected']:
        print(f"   シグナルタイプ: {result['signal_type']}")
        print(f"   シグナル強度: {result['signal_strength']}%")
        print(f"   エントリー価格: {result['entry_price']:,.0f}円")
        print(f"   利確目標: {result['profit_target']:,.0f}円 (+{result['expected_return']}%)")
        print(f"   損切り: {result['stop_loss']:,.0f}円 ({result['max_loss']}%)")
        print(f"   最大保有期間: {result['max_holding_days']}日")
        print(f"   リスクレベル: {result['risk_assessment']['risk_level']}")
        print(f"   推奨事項: {result['risk_assessment']['recommendation']}")
        
        print("\n🔍 詳細分析結果:")
        if 'detection_details' in result:
            details = result['detection_details']
            
            # 黒字転換分析
            if 'profitability_turnaround' in details:
                prof_data = details['profitability_turnaround']
                print(f"   黒字転換: {'✅' if prof_data.get('is_turnaround', False) else '❌'} ({prof_data.get('confidence', 0):.1%}信頼度)")
                if prof_data.get('is_turnaround'):
                    print(f"     - {prof_data.get('reason', 'N/A')}")
                    print(f"     - 連続赤字四半期: {prof_data.get('consecutive_loss_quarters', 0)}期")
                    print(f"     - 改善率: {prof_data.get('improvement_rate', 0):.1%}")
            
            # MA5上抜け分析
            if 'ma5_crossover' in details:
                ma_data = details['ma5_crossover']
                print(f"   MA5上抜け: {'✅' if ma_data.get('is_crossover', False) else '❌'} ({ma_data.get('confidence', 0):.1%}信頼度)")
                if ma_data.get('is_crossover'):
                    print(f"     - 現在価格: {ma_data.get('current_price', 0):,.0f}円")
                    print(f"     - MA5価格: {ma_data.get('ma5_value', 0):,.0f}円")
                    print(f"     - 上抜け率: {ma_data.get('crossover_ratio', 0):+.1%}")
            
            # エントリー条件
            if 'entry_conditions' in details:
                entry_data = details['entry_conditions']
                print(f"   エントリー条件: {'✅' if entry_data.get('valid', False) else '❌'}")
                if not entry_data.get('valid'):
                    print(f"     - 未満理由: {entry_data.get('reason', 'N/A')}")
    else:
        print(f"   未検出理由: {result.get('reason', 'N/A')}")
    
    print()
    
    # 設定情報の表示
    print("⚙️ ロジックB強化版設定:")
    config = logic_service.logic_b_enhanced_config
    print(f"   MA5上抜け閾値: {config['ma5_crossover_threshold']:.1%}")
    print(f"   利確目標: +{config['profit_target_rate']}%")
    print(f"   損切りライン: {config['stop_loss_rate']}%")
    print(f"   最大保有期間: {config['max_holding_days']}日")
    print(f"   最低出来高: {config['min_volume']:,}株")
    print(f"   連続黒字期間: {config['consecutive_profit_quarters']}四半期")
    
    print("\n📝 説明:")
    print(f"   {logic_service.get_logic_b_enhanced_description()}")
    
    print("\n✅ ロジックB強化版テスト完了")


async def test_comparison_with_original():
    """従来版ロジックBとの比較テスト"""
    print("\n🔄 従来版ロジックBとの比較テスト\n")
    
    logic_service = LogicDetectionService()
    
    test_stock_data = {
        'code': '7890',
        'name': 'テストグロース',
        'price': 890.0,
        'changeRate': 2.8,
        'volume': 12000000,
        'signals': {
            'rsi': 62.0,
            'macd': 0.02,
            'bollingerPosition': -0.1,
            'trendDirection': 'up',
            'volumeRatio': 1.8
        }
    }
    
    # 従来版ロジックBテスト
    print("📊 従来版ロジックB:")
    original_result = await logic_service.detect_logic_b(test_stock_data)
    print(f"   検出結果: {'✅ 検出' if original_result else '❌ 未検出'}")
    
    # 強化版ロジックBテスト
    print("\n🎯 強化版ロジックB:")
    enhanced_result = await logic_service.detect_logic_b_enhanced(test_stock_data)
    print(f"   検出結果: {'✅ 検出' if enhanced_result['detected'] else '❌ 未検出'}")
    
    if enhanced_result['detected']:
        print(f"   シグナル強度: {enhanced_result['signal_strength']}%")
        print(f"   戦略タイプ: {enhanced_result.get('strategy_type', 'N/A')}")
    
    print("\n💡 比較結果:")
    if original_result and enhanced_result['detected']:
        print("   両方で検出 - 強化版がより詳細な分析を提供")
    elif original_result and not enhanced_result['detected']:
        print("   従来版のみ検出 - 強化版はより厳格な条件")
    elif not original_result and enhanced_result['detected']:
        print("   強化版のみ検出 - 黒字転換パターンを精密に検出")
    else:
        print("   両方とも未検出 - 条件に満たない銘柄")


async def main():
    """メイン実行関数"""
    try:
        await test_logic_b_enhanced()
        await test_comparison_with_original()
        
        print("\n🎉 すべてのテストが完了しました！")
        
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("  ロジックB強化版（黒字転換銘柄精密検出）テスト")
    print("=" * 60)
    
    asyncio.run(main())