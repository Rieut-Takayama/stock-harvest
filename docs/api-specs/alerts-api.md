# アラート設定API仕様書

生成日: 2025-11-07
収集元: frontend/src/services/mock/alertsService.ts
@MOCK_TO_APIマーク数: 6

## エンドポイント一覧

### 1. アラート一覧取得
- **エンドポイント**: `GET /api/alerts`
- **APIパス定数**: `API_PATHS.ALERTS.LIST`
- **Request**: なし
- **Response**: `Alert[]`
- **説明**: 設定済みアラートの一覧を取得

### 2. アラート作成
- **エンドポイント**: `POST /api/alerts`
- **APIパス定数**: `API_PATHS.ALERTS.CREATE`
- **Request**: `AlertFormData`
- **Response**: `Alert`
- **説明**: 新しいアラートを作成

#### リクエスト例（価格到達アラート）
```json
{
  "type": "price",
  "stockCode": "7203",
  "targetPrice": 3000,
  "condition": {
    "type": "price",
    "operator": ">=",
    "value": 3000
  }
}
```

#### リクエスト例（ロジック発動アラート）
```json
{
  "type": "logic",
  "stockCode": "9984",
  "condition": {
    "type": "logic",
    "logicType": "stop_high_limit"
  }
}
```

### 3. アラート状態切替
- **エンドポイント**: `PUT /api/alerts/:id/toggle`
- **APIパス定数**: `API_PATHS.ALERTS.TOGGLE(id)`
- **Request**: なし
- **Response**: `Alert`
- **説明**: アラートのON/OFF状態を切り替え

### 4. アラート削除
- **エンドポイント**: `DELETE /api/alerts/:id`
- **APIパス定数**: `API_PATHS.ALERTS.DELETE(id)`
- **Request**: なし
- **Response**: `void`
- **説明**: 指定したアラートを削除

### 5. LINE通知設定取得
- **エンドポイント**: `GET /api/notifications/line`
- **APIパス定数**: `API_PATHS.NOTIFICATIONS.LINE_CONFIG`
- **Request**: なし
- **Response**: `LineNotificationConfig`
- **説明**: LINE通知の設定状態を取得

#### レスポンス例
```json
{
  "isConnected": true,
  "token": "***masked***",
  "status": "connected",
  "lastNotification": "2025-11-07T09:30:00Z"
}
```

### 6. LINE通知設定更新
- **エンドポイント**: `PUT /api/notifications/line`
- **APIパス定数**: `API_PATHS.NOTIFICATIONS.LINE_CONFIG`
- **Request**: `Partial<LineNotificationConfig>`
- **Response**: `LineNotificationConfig`
- **説明**: LINE通知設定を更新

## アラートタイプ

### 価格到達アラート
- 指定した株価に到達した際に通知
- 条件: 以上(>=)、以下(<=)、等しい(=)

### ロジック発動アラート
- 特定のロジック検出時に通知
- 対応ロジック:
  - `stop_high_limit`: ストップ高張り付き
  - `loss_to_profit`: 赤字→黒字転換

## モックサービス参照
```typescript
// 実装時はこのモックサービスの挙動を参考にする
frontend/src/services/mock/alertsService.ts
```