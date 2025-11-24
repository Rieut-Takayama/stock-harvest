# ロジックB強化版実装仕様書

## 概要

**ロジックB強化版（黒字転換銘柄精密検出）**は、直近1年間で初めて経常利益が黒字転換した銘柄を精密に検出し、5日移動平均線上抜けタイミングでエントリーシグナルを生成する高度なトレーディングアルゴリズムです。

## 主要機能

### 1. 黒字転換条件検出
- **対象期間**: 直近1年間（4四半期）
- **転換条件**: 最新四半期で初回黒字転換
- **最低赤字期間**: 連続2四半期以上の赤字期間からの回復
- **改善率評価**: 過去平均損失からの改善度を数値化

### 2. エントリータイミング検出
- **5日移動平均線上抜け**: 2%以上の上抜けでシグナル発生
- **価格上昇範囲**: 1-8%の穏やかな上昇を期待
- **出来高条件**: 1500万株以上の十分な流動性
- **RSI適正範囲**: 40-75の健全な範囲

### 3. 売買管理システム
- **利確目標**: +25%（業績改善銘柄の特性を考慮）
- **損切りライン**: -10%（リスク管理）
- **最大保有期間**: 45日（1.5ヶ月）
- **リスク評価**: 5段階リスクレベル判定

## 技術実装

### コア実装ファイル
```
backend/src/services/logic_detection_service.py
├── detect_logic_b_enhanced() - メイン検出ロジック
├── _check_profitability_turnaround() - 黒字転換判定
├── _detect_ma5_crossover() - MA5上抜け検出
├── _validate_entry_conditions_b() - エントリー条件検証
├── _check_exclusion_rules_b() - 除外ルール判定
├── _generate_trading_signal_b() - 売買シグナル生成
└── _assess_trading_risk_b() - リスク評価
```

### 統合ポイント
```
backend/src/services/scan_service.py
└── _execute_scan() - 全銘柄スキャンでロジックB強化版を実行
```

### 設定パラメータ
```python
logic_b_enhanced_config = {
    'ma5_crossover_threshold': 0.02,      # MA5上抜け閾値（2%）
    'profit_target_rate': 25.0,           # 利確目標（+25%）
    'stop_loss_rate': -10.0,              # 損切りライン（-10%）
    'max_holding_days': 45,               # 最大保有期間（1.5ヶ月）
    'min_volume': 15000000,               # 最低出来高（1500万株）
    'consecutive_profit_quarters': 2,     # 連続黒字四半期数
    'exclude_loss_carryforward': True,    # 繰越損失除外フラグ
}
```

## データソース活用

### 無料版実装
- **Yahoo Finance API**: 四半期財務データ、株価データ
- **EDINET公開データ**: 決算短信情報（将来実装予定）
- **企業IR情報**: 公開決算情報の活用

### データキャッシュシステム
```python
self.earnings_data_cache = {}      # 決算データキャッシュ（1週間有効）
self.moving_average_cache = {}     # 移動平均データキャッシュ（1時間有効）
```

## 検出アルゴリズム詳細

### Step 1: 黒字転換判定
```python
async def _check_profitability_turnaround(self, stock_code: str) -> Dict:
    # 1. 四半期決算データを取得（Yahoo Finance）
    # 2. 最新四半期の黒字確認
    # 3. 過去四半期の連続赤字期間をカウント
    # 4. 改善率を計算（(最新利益 - 過去平均損失) / 過去平均損失）
    # 5. 信頼度スコアを算出（0.6 + 連続赤字期間*0.1 + 改善率*0.25）
```

### Step 2: MA5上抜け検出
```python
async def _detect_ma5_crossover(self, stock_data: Dict) -> Dict:
    # 1. 過去1ヶ月の株価データを取得
    # 2. 5日移動平均線を計算
    # 3. 現在価格 > MA5 かつ MA5上昇トレンド
    # 4. 上抜け率が閾値（2%）以上
    # 5. 信頼度スコアを算出
```

### Step 3: エントリー条件検証
```python
async def _validate_entry_conditions_b(self, stock_data: Dict) -> Dict:
    # 1. 出来高 >= 1500万株
    # 2. 価格変化率 1-8%の範囲
    # 3. RSI 40-75の適正範囲
    # 4. 出来高比率 1.2-3.0の適度な増加
```

### Step 4: 除外ルール
```python
async def _check_exclusion_rules_b(self, stock_data: Dict, stock_code: str) -> Dict:
    # 1. 繰越損失チェック（大幅累積損失の除外）
    # 2. 極端な価格変動除外（15%以上）
    # 3. 低流動性銘柄除外（500万株未満）
    # 4. 重複検出除外（6ヶ月以内の検出履歴）
```

## シグナル生成システム

### エントリーシグナル
```python
if change_rate >= 1.5:  # 1.5%以上の上昇
    signal_type = 'BUY_ENTRY'
    signal_strength = min(90, 50 + (change_rate * 8))  # 50-90%の範囲
else:
    signal_type = 'WATCH'
    signal_strength = max(20, change_rate * 20)  # 監視モード
```

### 価格ターゲット
```python
entry_price = current_price
profit_target = entry_price * 1.25  # +25%利確
stop_loss = entry_price * 0.90      # -10%損切り
```

### リスク評価アルゴリズム
```python
risk_score = 70  # ベーススコア

# 価格変動リスク
if change_rate < 2.0:
    risk_score -= 10  # 動きが鈍い

# 流動性リスク  
if volume < 10000000:
    risk_score -= 15  # やや低流動性

# RSI過熱リスク
if rsi > 75 or rsi < 40:
    risk_score -= 10  # 過熱または低水準

# リスクレベル判定
if risk_score >= 85: risk_level = 'LOW'
elif risk_score >= 70: risk_level = 'MEDIUM'
elif risk_score >= 55: risk_level = 'MEDIUM_HIGH'
else: risk_level = 'HIGH'
```

## テスト結果

### スタンドアロンテスト
```bash
cd /Users/rieut/STOCK\ HARVEST/backend
python3 test_logic_b_standalone.py
```

**テスト結果例**:
```
📈 検出結果:
   検出成功: ✅
   シグナルタイプ: BUY_ENTRY
   シグナル強度: 75.6%
   エントリー価格: 1,250円
   利確目標: 1,562円 (+25.0%)
   損切り: 1,125円 (-10.0%)
   最大保有期間: 45日
   リスクレベル: MEDIUM
   
🔍 詳細分析結果:
   黒字転換: ✅ (95.0%信頼度)
   MA5上抜け: ✅ (100.0%信頼度)
   エントリー条件: ✅
```

## API統合

### スキャンサービス統合
スキャンサービス (`scan_service.py`) に完全統合され、全銘柄スキャン時に以下が実行されます：

```python
# ロジックB強化版検出（黒字転換銘柄精密検出）
logic_b_enhanced_result = await self.logic_detection_service.detect_logic_b_enhanced(stock_data)
if logic_b_enhanced_result['detected']:
    stock_data['enhanced_signals'] = logic_b_enhanced_result
    logic_b_enhanced_detected.append(stock_data)
    await self._save_scan_result(scan_id, stock_data, 'logic_b_enhanced')
```

### フロントエンド対応
APIレスポンスに `logicBEnhanced` セクションが追加され、フロントエンドで専用UI表示が可能：

```json
{
  "scanId": "scan_20251124_143022",
  "logicBEnhanced": {
    "detected": 5,
    "stocks": [
      {
        "code": "3456",
        "name": "パルコデジタル",
        "enhanced_signals": {
          "signal_type": "BUY_ENTRY",
          "signal_strength": 75.6,
          "profit_target": 1562,
          "stop_loss": 1125,
          "strategy_type": "profitability_turnaround"
        }
      }
    ]
  }
}
```

## パフォーマンス最適化

### キャッシュ戦略
- **決算データキャッシュ**: 1週間有効（決算データ変更頻度を考慮）
- **移動平均キャッシュ**: 1時間有効（株価変動への追従）
- **検出履歴キャッシュ**: メモリ内保存（重複検出防止）

### API制限対応
```python
# Yahoo Finance API制限考慮
await asyncio.sleep(1)  # 各銘柄処理間に1秒待機
```

## 将来拡張予定

### 有料データソース連携
- **IRバンク**: 詳細決算データ取得
- **カブタン**: 企業分析データ連携
- **QUICK**: リアルタイム決算情報

### アルゴリズム改善
- **機械学習統合**: 黒字転換成功確率の予測モデル
- **セクター分析**: 業界別黒字転換パターンの分析
- **マクロ経済連携**: 経済指標との相関分析

## 運用推奨事項

### リスク管理
1. **ポジションサイズ**: 総資産の2-5%以内
2. **分散投資**: 同時期に5銘柄以内
3. **損切り厳守**: -10%で機械的に実行
4. **業績フォロー**: 四半期決算の継続監視

### 市場環境考慮
- **強気相場**: より積極的なエントリー
- **弱気相場**: エントリー見送りまたは縮小
- **決算シーズン**: 特に注意深い監視

## 実装完了日
**2024年11月24日** - Stock Harvest AI ロジックB強化版（黒字転換銘柄精密検出）実装完了

---

このドキュメントは、ロジックB強化版の技術実装と運用ガイドラインを包括的に説明しています。実際の投資にご利用の際は、必ずリスク管理を行い、投資は自己責任でお願いします。