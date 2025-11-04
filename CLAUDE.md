# プロジェクト設定

## 基本設定
```yaml
プロジェクト名: Stock Harvest AI
開始日: 2025-11-04
技術スタック:
  frontend: 
    - React 18
    - TypeScript 5
    - MUI v6
    - Recharts
    - Zustand
    - React Router v6
    - React Query
    - Vite 5
  backend:
    - Python 3.11+
    - FastAPI
    - pandas
    - numpy
    - ta-lib
    - yfinance
    - APScheduler
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

### APIエンドポイント
```yaml
命名規則:
  - RESTful形式を厳守
  - 複数形を使用 (/stocks, /alerts)
  - ケバブケース使用 (/scan-results)
  
主要エンドポイント:
  - POST /api/scan/execute - 全銘柄スキャン実行
  - GET /api/stocks/:code - 銘柄詳細取得
  - GET /api/portfolio - ポートフォリオ一覧
  - POST /api/alerts - アラート設定
```

### 型定義
```yaml
配置:
  frontend: src/types/index.ts
  backend: src/types/index.ts

同期ルール:
  - 両ファイルは常に同一内容を保つ
  - 片方を更新したら即座にもう片方も更新

株価データ型例:
  interface StockData {
    code: string;
    name: string;
    price: number;
    change: number;
    changeRate: number;
    volume: number;
    signals: TechnicalSignals;
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
```

## ⚠️ プロジェクト固有の注意事項
```yaml
# 実現可能性調査で発見した制約事項
- リアルタイムデータ: 無料APIでは20分遅延
- API制限: Yahoo Financeは過度なアクセスでIP制限の可能性
- 投資助言: 商用利用時は投資助言業登録が必要
- 株価予測: AIの予測精度は約55-60%が現実的上限
```

## 📝 作業ログ(最新5件)
```yaml
# 主要な作業を記録
- [2025-11-04] 要件定義書作成完了
- [2025-11-04] 技術スタック決定（React + Python/FastAPI）
- [2025-11-04] 5ページ構成で設計完了
- [2025-11-04] 青・緑・白のデザインコンセプト決定
- [2025-11-04] 個人利用前提で認証なし設計を採用
```