# Contact Support API仕様書

生成日: 2025-11-07
収集元: frontend/src/services/mock/contactSupportService.ts
@MOCK_TO_APIマーク数: 3

## エンドポイント一覧

### 1. FAQ取得
- **エンドポイント**: `GET /api/contact/faq`
- **APIパス定数**: `API_PATHS.CONTACT.FAQ`
- **Request**: なし
- **Response**: `FAQ[]`
- **説明**: よくある質問の一覧を取得

#### レスポンス例
```json
[
  {
    "id": "1",
    "question": "ロジックスキャンはどのくらいの頻度で実行されますか？",
    "answer": "ロジックスキャンは平日の取引時間中、15分間隔で全銘柄を対象に実行されます。"
  }
]
```

### 2. 問合せフォーム送信
- **エンドポイント**: `POST /api/contact/submit`
- **APIパス定数**: `API_PATHS.CONTACT.SUBMIT`
- **Request**: `ContactForm`
- **Response**: `{ success: boolean, message: string }`
- **説明**: 問合せフォームの内容を送信

#### リクエスト例
```json
{
  "type": "technical",
  "subject": "ログインできない",
  "content": "ログインページでエラーが発生します",
  "email": "user@example.com"
}
```

### 3. システム情報取得
- **エンドポイント**: `GET /api/system/info`
- **APIパス定数**: `API_PATHS.SYSTEM.INFO`
- **Request**: なし
- **Response**: `SystemInfo`
- **説明**: システムのバージョンと稼働状況を取得

#### レスポンス例
```json
{
  "version": "v1.0.0",
  "lastUpdated": "2025-11-07T10:00:00Z",
  "status": "operational",
  "statusDisplay": "正常稼働中"
}
```

## モックサービス参照
```typescript
// 実装時はこのモックサービスの挙動を参考にする
frontend/src/services/mock/contactSupportService.ts
```