"""
簡易版スキャンロジック - デプロイ用
TA-Libを使わずにサンプルデータで動作する版
"""
import asyncio
import random
from datetime import datetime
from typing import List, Dict, Any

# サンプル銘柄データ
SAMPLE_STOCKS = [
    {"code": "9984", "name": "ソフトバンクグループ", "price": 22255.0},
    {"code": "4819", "name": "デジタルガレージ", "price": 3850.0},
    {"code": "2158", "name": "フロンテッジ", "price": 1245.0},
    {"code": "4477", "name": "BASE", "price": 2890.0},
    {"code": "6758", "name": "ソニー", "price": 18450.0},
    {"code": "7203", "name": "トヨタ自動車", "price": 2847.0},
    {"code": "9501", "name": "東京電力", "price": 892.0},
    {"code": "8306", "name": "三菱UFJ", "price": 1285.0},
    {"code": "4063", "name": "信越化学", "price": 4820.0},
    {"code": "6861", "name": "キーエンス", "price": 68500.0}
]

class SimpleScanLogic:
    def __init__(self):
        self.is_scanning = False
        self.progress = 100
        self.total_stocks = len(SAMPLE_STOCKS)
        self.processed_stocks = len(SAMPLE_STOCKS)
        self.scan_results = None
        
    async def execute_scan(self, logic_a: bool = True, logic_b: bool = True):
        """スキャンを実行（サンプルデータ使用）"""
        self.is_scanning = True
        self.progress = 0
        
        try:
            # 疑似的なスキャン処理
            for i in range(self.total_stocks):
                self.processed_stocks = i + 1
                self.progress = int((i + 1) / self.total_stocks * 100)
                await asyncio.sleep(0.1)  # 疑似処理時間
            
            # サンプル結果を生成
            logic_a_stocks = []
            logic_b_stocks = []
            
            if logic_a:
                # ロジックA: 価格上昇株をランダム選択
                selected = random.sample(SAMPLE_STOCKS[:5], 2)
                for stock in selected:
                    logic_a_stocks.append({
                        "code": stock["code"],
                        "name": stock["name"],
                        "price": stock["price"],
                        "change": round(random.uniform(50, 300), 1),
                        "changeRate": round(random.uniform(2.0, 8.0), 2),
                        "volume": random.randint(1000000, 50000000)
                    })
            
            if logic_b:
                # ロジックB: 黒字転換候補をランダム選択
                selected = random.sample(SAMPLE_STOCKS[5:], 1)
                for stock in selected:
                    logic_b_stocks.append({
                        "code": stock["code"],
                        "name": stock["name"],
                        "price": stock["price"],
                        "change": round(random.uniform(100, 500), 1),
                        "changeRate": round(random.uniform(3.0, 12.0), 2),
                        "volume": random.randint(5000000, 100000000)
                    })
            
            self.scan_results = {
                "scanId": f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "completedAt": datetime.now().isoformat(),
                "totalProcessed": self.total_stocks,
                "logicA": {
                    "detected": len(logic_a_stocks),
                    "stocks": logic_a_stocks
                },
                "logicB": {
                    "detected": len(logic_b_stocks),
                    "stocks": logic_b_stocks
                }
            }
            
            self.is_scanning = False
            return self.scan_results
            
        except Exception as e:
            self.is_scanning = False
            raise e
    
    def get_scan_status(self):
        """スキャン状況を取得"""
        return {
            "isRunning": self.is_scanning,
            "progress": self.progress,
            "totalStocks": self.total_stocks,
            "processedStocks": self.processed_stocks,
            "currentStock": None,
            "estimatedTime": 0,
            "message": "スキャン実行中..." if self.is_scanning else "スキャンが完了しました"
        }
    
    def get_scan_results(self):
        """最新のスキャン結果を取得"""
        if self.scan_results is None:
            # 初期状態でのダミー結果
            return {
                "scanId": "initial_scan",
                "completedAt": datetime.now().isoformat(),
                "totalProcessed": self.total_stocks,
                "logicA": {
                    "detected": 0,
                    "stocks": []
                },
                "logicB": {
                    "detected": 1,
                    "stocks": [{
                        "code": "9984",
                        "name": "ソフトバンクグループ",
                        "price": 22255.0,
                        "change": 555.0,
                        "changeRate": 2.56,
                        "volume": 15602400
                    }]
                }
            }
        return self.scan_results

# グローバルインスタンス
scan_engine = SimpleScanLogic()