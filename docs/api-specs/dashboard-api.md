# ロジックスキャナーダッシュボードAPI仕様書

生成日: 2025-11-07
収集元: frontend/src/services/mock/dashboardService.ts
@MOCK_TO_APIマーク数: 5

## エンドポイント一覧

### 1. 全銘柄スキャン実行
- **エンドポイント**: `POST /api/scan/execute`
- **APIパス定数**: `API_PATHS.SCAN.EXECUTE`
- **Request**: なし
- **Response**: `{ scanId: string, message: string }`
- **説明**: 全銘柄に対するロジックスキャンを開始

#### レスポンス例
```json
{
  "scanId": "scan_20251107_093000",
  "message": "全銘柄スキャンを開始しました"
}
```

### 2. スキャン状態取得
- **エンドポイント**: `GET /api/scan/status`
- **APIパス定数**: `API_PATHS.SCAN.STATUS`
- **Request**: なし
- **Response**: `ScanStatus`
- **説明**: 現在実行中のスキャンの進捗状況を取得

#### レスポンス例
```json
{
  "isRunning": true,
  "progress": 65,
  "totalStocks": 3800,
  "processedStocks": 2470,
  "currentStock": "7203",
  "estimatedTime": 45,
  "message": "スキャン実行中..."
}
```

### 3. スキャン結果取得
- **エンドポイント**: `GET /api/scan/results`
- **APIパス定数**: `API_PATHS.SCAN.RESULTS`
- **Request**: なし
- **Response**: `ScanResult`
- **説明**: 最新のスキャン結果を取得

#### レスポンス例
```json
{
  "scanId": "scan_20251107_093000",
  "completedAt": "2025-11-07T09:33:00Z",
  "totalProcessed": 3800,
  "logicA": {
    "detected": 3,
    "stocks": [
      {
        "code": "7203",
        "name": "トヨタ自動車",
        "price": 2890,
        "change": 145,
        "changeRate": 5.3,
        "volume": 15420000
      }
    ]
  },
  "logicB": {
    "detected": 2,
    "stocks": [
      {
        "code": "4689", 
        "name": "Zホールディングス",
        "price": 425,
        "change": 12,
        "changeRate": 2.9,
        "volume": 8950000
      }
    ]
  }
}
```

### 4. 手動決済シグナル実行
- **エンドポイント**: `POST /api/signals/manual-execute`
- **APIパス定数**: `API_PATHS.SIGNALS.MANUAL_EXECUTE`
- **Request**: `ManualSignalRequest`
- **Response**: `SignalExecutionResult`
- **説明**: 手動での決済シグナル（損切り・利確）を実行

#### リクエスト例（損切り）
```json
{
  "type": "stop_loss",
  "reason": "急激な下落のため損切りを実行"
}
```

#### リクエスト例（利確）
```json
{
  "type": "take_profit", 
  "reason": "目標利益に到達したため利確を実行"
}
```

#### レスポンス例
```json
{
  "success": true,
  "signalId": "signal_20251107_093500",
  "executedAt": "2025-11-07T09:35:00Z",
  "message": "損切りシグナルを正常に送信しました"
}
```

### 5. チャートデータ取得
- **エンドポイント**: `GET /api/charts/data/:stockCode`
- **APIパス定数**: `API_PATHS.CHARTS.DATA(stockCode)`
- **Request**: ChartDisplayConfig (URLパラメータ)
- **Response**: チャートデータ（モックでは銘柄コード表示）
- **説明**: 指定した銘柄のチャートデータを取得

#### リクエスト例
```
GET /api/charts/data/7203?timeframe=1d&period=30d
```

## ロジック検出仕様

### ロジックA: ストップ高張り付き銘柄
- 対象: 全上場銘柄
- 条件: 
  - 当日高値がストップ高
  - 一定時間（15分以上）張り付き状態
- 検出時アクション: アラート・チャート表示

### ロジックB: 赤字→黒字転換銘柄
- 対象: 財務データ利用可能銘柄
- 条件:
  - 前期が赤字（営業利益 < 0）
  - 当期予想が黒字（営業利益 > 0）
- 検出時アクション: アラート・チャート表示

## 手動決済シグナル

### シグナルタイプ
- `stop_loss`: 損切りシグナル
- `take_profit`: 利確シグナル

### 実行フロー
1. フロントエンドで確認ダイアログ表示
2. ユーザー確認後、API実行
3. バックエンドで外部取引システムに通知
4. 結果をフロントエンドに返却

## モックサービス参照
```typescript
// 実装時はこのモックサービスの挙動を参考にする
frontend/src/services/mock/dashboardService.ts
```