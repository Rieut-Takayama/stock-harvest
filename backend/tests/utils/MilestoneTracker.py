"""
マイルストーントラッカー - @9統合テスト成功請負人が活用する処理時間計測ユーティリティ
"""

import time
from typing import Dict

class MilestoneTracker:
    def __init__(self):
        self.milestones: Dict[str, float] = {}
        self.start_time: float = time.time()
        self.current_op: str = "初期化"

    def set_operation(self, op: str) -> None:
        """操作の設定"""
        self.current_op = op
        print(f"[{self.get_elapsed():.2f}秒] ▶️ 開始: {op}")

    def mark(self, name: str) -> None:
        """マイルストーンの記録"""
        self.milestones[name] = time.time()
        print(f"[{self.get_elapsed():.2f}秒] 🏁 {name}")

    def summary(self) -> None:
        """結果表示(@9のデバッグで重要)"""
        print("\n--- 処理時間分析 ---")
        entries = sorted(self.milestones.items(), key=lambda x: x[1])

        for i in range(1, len(entries)):
            prev = entries[i-1]
            curr = entries[i]
            diff = curr[1] - prev[1]
            print(f"{prev[0]} → {curr[0]}: {diff:.2f}秒")

        print(f"総実行時間: {self.get_elapsed():.2f}秒\n")

    def get_elapsed(self) -> float:
        """経過時間の取得"""
        return time.time() - self.start_time