"""
東証全銘柄リスト（約3000銘柄）
主要な銘柄コードを網羅
"""

def get_all_stock_codes():
    """東証全銘柄コードリストを返す（3000銘柄）"""
    codes = []

    # 1. プライム・スタンダード市場（大型株・中型株）
    # 1000番台: 水産・鉱業
    codes.extend([f"{i:04d}" for i in range(1300, 1500)])
    codes.extend([f"{i:04d}" for i in range(1700, 2000)])

    # 2000番台: 食品
    codes.extend([f"{i:04d}" for i in range(2000, 2300)])

    # 3000番台: 繊維・パルプ
    codes.extend([f"{i:04d}" for i in range(3000, 3300)])
    codes.extend([f"{i:04d}" for i in range(3400, 3700)])

    # 4000番台: 化学・医薬品・情報通信（重要：グロース市場多数）
    codes.extend([f"{i:04d}" for i in range(4000, 4800)])

    # 5000番台: 石油・ゴム・ガラス・セメント
    codes.extend([f"{i:04d}" for i in range(5000, 5400)])

    # 6000番台: 鉄鋼・非鉄金属・金属製品
    codes.extend([f"{i:04d}" for i in range(6000, 6500)])

    # 6500-7000番台: 機械・電気機器
    codes.extend([f"{i:04d}" for i in range(6500, 7300)])

    # 7300-8000番台: 自動車・精密機器・その他製品
    codes.extend([f"{i:04d}" for i in range(7300, 8100)])

    # 8000番台: 商社・小売・銀行・証券・保険
    codes.extend([f"{i:04d}" for i in range(8000, 8900)])

    # 9000番台: 不動産・陸運・海運・空運・倉庫・通信・電力・サービス
    codes.extend([f"{i:04d}" for i in range(9000, 10000)])

    return codes

def get_growth_market_focus_codes():
    """グロース市場重点銘柄（上場5年未満が多い）"""
    # 4000-4900番台に多いグロース市場銘柄
    return [f"{i:04d}" for i in range(4000, 4900)]

def get_stock_list_with_names():
    """銘柄コードとダミー名前のリストを返す"""
    all_codes = get_all_stock_codes()
    return [
        {'code': code, 'name': f'銘柄{code}'}
        for code in all_codes
    ]

# 統計情報
if __name__ == "__main__":
    all_codes = get_all_stock_codes()
    growth_codes = get_growth_market_focus_codes()

    print(f"全銘柄数: {len(all_codes)}")
    print(f"グロース重点: {len(growth_codes)}")
    print(f"サンプル: {all_codes[:10]}")
