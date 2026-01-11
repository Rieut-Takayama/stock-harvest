# プロジェクト設定

## 基本設定
```yaml
プロジェクト名: Stock Harvest AI - ストップ高張り付き検知システム
開始日: 2026-01-11
技術スタック:
  frontend: 
    - React 19.1
    - TypeScript 5.9
    - MUI v7
    - Recharts 3.3
    - Zustand 5.0
    - React Router v7
    - React Query (Tanstack) 5.90
    - Vite 7.1
    - Playwright (E2Eテスト)
  backend:
    - Python 3.11+
    - FastAPI 0.104.1
    - Uvicorn 0.24.0
    - pandas 2.1.4
    - numpy 1.24.4
    - pandas-ta 0.3.14b
    - yfinance 0.2.28
    - APScheduler 3.10.4
    - AsyncPG 0.29.0 (PostgreSQL接続)
    - Pydantic 2.5.0 (データバリデーション)
  database:
    - PostgreSQL (Neon推奨)
```

## 開発環境
```yaml
ポート設定:
  # 複数プロジェクト並行開発のため、一般的でないポートを使用
  frontend: 3247
  backend: 8432
  database: 5433

環境変数:
  設定ファイル: .env.local(ルートディレクトリ)
  必須項目:
    - DATABASE_URL
    - LINE_NOTIFY_TOKEN
    - OPENAI_API_KEY (オプション)
```

## テスト認証情報
```yaml
開発用アカウント:
  # 個人利用のため認証なし
  email: 不要
  password: 不要

外部サービス:
  Yahoo Finance: APIキー不要（yfinanceライブラリ使用）
  LINE Notify: 個人トークン設定必要
  Neon Database: 無料アカウントで開始
```

## コーディング規約

### 命名規則
```yaml
ファイル名:
  - コンポーネント: PascalCase.tsx (例: StockDashboard.tsx)
  - ユーティリティ: camelCase.ts (例: calculatePrice.ts)
  - 定数: UPPER_SNAKE_CASE.ts (例: TECHNICAL_INDICATORS.ts)

変数・関数:
  - 変数: camelCase
  - 関数: camelCase
  - 定数: UPPER_SNAKE_CASE
  - 型/インターフェース: PascalCase
```

### コード品質
```yaml
必須ルール:
  - TypeScript: strictモード有効
  - 未使用の変数/import禁止
  - console.log本番環境禁止
  - エラーハンドリング必須

フォーマット:
  - インデント: スペース2つ
  - セミコロン: あり
  - クォート: シングル
```

### コミットメッセージ
```yaml
形式: [type]: [description]

type:
  - feat: 新機能
  - fix: バグ修正
  - docs: ドキュメント
  - style: フォーマット
  - refactor: リファクタリング
  - test: テスト
  - chore: その他

例: "feat: 全銘柄AIスキャン機能を追加"
```

## プロジェクト固有ルール

### ストップ高張り付き検知ロジック
```yaml
5つの判定条件:
  1. ストップ高価格に到達（終値 = ストップ高価格）
  2. 始値 = 終値（張り付き状態）
  3. 安値 < 終値 × 0.01（1%未満条件）
  4. 上場5年未満の銘柄
  5. 四半期決算発表の翌営業日

バッチ処理:
  - 実行タイミング: 毎日15時30分以降
  - 処理対象: 全市場約3000銘柄
  - 期待抽出数: 月間0-3銘柄（超希少パターン）
```

### APIエンドポイント
```yaml
命名規則:
  - RESTful形式を厳守
  - 複数形を使用 (/batch-results, /extractions)
  - ケバブケース使用 (/stock-data)
  
主要エンドポイント:
  - GET /api/batch/results - 最新抽出結果取得
  - GET /api/extractions/history - 過去抽出履歴
  - GET /api/system/status - システム状態確認
  - GET /api/health - ヘルスチェック
```

### 型定義
```yaml
配置:
  frontend: src/types/index.ts
  backend: src/types/index.ts

同期ルール:
  - 両ファイルは常に同一内容を保つ
  - 片方を更新したら即座にもう片方も更新

抽出銘柄データ型例:
  interface ExtractedStock {
    code: string;          // 銘柄コード
    name: string;          // 銘柄名
    market: string;        // 市場区分
    extractDate: string;   // 抽出日
    stockPrice: {
      open: number;        // 始値
      close: number;       // 終値
      high: number;        // 高値
      low: number;         // 安値
      stopHigh: number;    // ストップ高価格
    };
    conditions: {
      lowToCloseRatio: number;    // 安値/終値比率
      listingDate: string;        // 上場日
      yearsListed: number;        // 上場年数
      earningsDate: string;       // 決算発表日
    };
  }
```

## デザインシステム
```yaml
カラーパレット:
  primary: 
    main: '#1976d2' # 青（信頼性・安定性）
    light: '#42a5f5'
    dark: '#0d47a1'
  
  secondary:
    main: '#4caf50' # 緑（成長・利益）
    light: '#81c784'
    dark: '#388e3c'
  
  background:
    default: '#ffffff' # 白（クリーンさ）
    paper: '#f5f5f5'
  
  text:
    primary: '#212121'
    secondary: '#757575'
  
  positive: '#4caf50' # 上昇・利益
  negative: '#f44336' # 下落・損失
```

## 🆕 最新技術情報(知識カットオフ対応)
```yaml
# Web検索で解決した破壊的変更を記録
- yfinance: 2024年版では一部APIが変更、公式ドキュメント参照推奨
- ta-lib: Python 3.11+でのインストールに追加設定必要
- FastAPI: 最新版でWebSocket対応が強化

# MUI v7対応情報 (2025-11-07追加)
- TypeScript型インポート: 'import type' 必須 (verbatimModuleSyntax対応)
- Grid2統合: Grid2がGridに統合、xs/mdプロパティは size={{xs: 12, md: 6}} 形式に変更
- モジュール宣言: '@mui/material/styles'に統一、ネストしたインポートは削除
- テーマ関数引数: 未使用のthemeパラメータはTypeScriptエラーの原因
- TypographyOptions: '@mui/material/styles'から直接インポート不可

# JavaScript/TypeScript UTF-8対応 (2025-11-08追加)
- btoa()関数: 日本語等Unicode文字でInvalidCharacterError発生
- 解決策: encodeURIComponent+replace、またはTextEncoder使用
- JWTライブラリ: モック実装時はUnicode文字エンコーディング考慮必須
```

## ⚠️ プロジェクト固有の注意事項
```yaml
# ストップ高張り付き検知システム固有の制約
- 超希少パターン: 月間0-3銘柄程度の極めて稀な現象
- バッチ処理限定: リアルタイム検知は不要（15時30分以降実行）
- 投資助言回避: パターン検索ツールとして位置づけ
- 条件厳格性: 5つすべての条件を満たす必要があり、緩和不可
- データ遅延: Yahoo Finance APIの20分遅延は許容範囲内
```

## 🔄 マイグレーション手順

### 環境設定完了確認
1. **環境変数設定**: .env.localに全必須項目設定済み
2. **データベース接続**: DATABASE_URL設定済み（Neon PostgreSQL推奨）
3. **外部APIキー**: 基本的に不要（Yahoo Financeは無料API使用）

### アプリケーション起動手順
```bash
# フロントエンド起動（開発環境）
cd frontend && npm run dev  # ポート: 3247

# バックエンド起動（バッチ処理サーバー）
cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8432

# バッチ処理手動実行（テスト用）
cd backend && python -m src.batch.stock_extraction

# データベース初期化（初回のみ）
cd backend && python -m src.database.migrate
```

**注意**:
- ポート番号は必ず 3247(frontend) / 8432(backend) を使用
- バッチ処理は15時30分に自動実行（APScheduler使用）
- 環境変数は .env.local から自動読み込み

## 📝 作業ログ(最新5件)
```yaml
# ストップ高張り付き検知システム開発記録
- [2026-01-11] Phase 1完了: 要件定義書作成、5つの判定条件確定、技術スタック決定
- [2026-01-11] ロジック詳細設計: 馬場さんの投資ノウハウを完全再現する仕様策定
- [2026-01-11] データ設計: 抽出銘柄、決算情報、バッチ実行ログの3エンティティ設計
- [2026-01-11] バッチ処理仕様: 15時30分自動実行、月間0-3銘柄抽出の希少パターン検知
- [2026-01-11] インフラ選定: Vercel+Cloud Run+Neon PostgreSQLの無料構成確定
```

## 13. プロジェクト開発フロー

### Phase 1: 要件定義 ✅ 完了
- **目標**: ストップ高張り付き検知システムの仕様確定
- **成果物**: 要件定義書、技術スタック、データ設計

### Phase 2-8: 実装フェーズ
1. **Git/GitHub管理**: バージョン管理とブランチ戦略
2. **フロントエンド基盤**: React+TypeScript環境構築  
3. **ページ実装**: 検索結果・管理ページ作成
4. **バックエンド基盤**: FastAPI+PostgreSQL環境構築
5. **ロジック実装**: 5つの条件判定とバッチ処理
6. **統合テスト**: API連携とエンドツーエンドテスト
7. **デプロイ設定**: Vercel+Cloud Runへの本番配置

### 品質基準
- **関数行数**: 100行以下（96.7%カバー）
- **ファイル行数**: 700行以下（96.9%カバー）
- **複雑度**: McCabe 10以下
- **行長**: 120文字以下