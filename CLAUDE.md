# プロジェクト設定

## 基本設定
```yaml
プロジェクト名: Stock Harvest AI
開始日: 2025-11-04
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
# 実現可能性調査で発見した制約事項
- リアルタイムデータ: 無料APIでは20分遅延
- API制限: Yahoo Financeは過度なアクセスでIP制限の可能性
- 投資助言: 商用利用時は投資助言業登録が必要
- 株価予測: AIの予測精度は約55-60%が現実的上限
```

## 📝 作業ログ(最新5件)
```yaml
# 主要な作業を記録
- [2025-11-08] ログイン機能修正: Unicode文字エンコーディングエラー解消、E2Eテスト全件パス
- [2025-11-08] ビルドエラー完全解消: verbatimModuleSyntax、MUI Grid API、未使用変数修正
- [2025-11-07] ナチュラルライトテーマのMUIテーマファイル群作成完了
- [2025-11-07] MUI v7対応で型システムとGrid2の互換性修正
- [2025-11-07] ナチュラルライト選択(緑ベース #38a169)で開発環境整備完了
```

## 13. E2Eテスト自律実行の絶対原則

**【重要】セッション開始時・compact後の自動判定**

このセクションはE2Eテストオーケストレーターによって自動生成されました。

---

**最初に必ず専門知識を注入してください**

E2Eテスト実行中の場合、以下を実行してから開始してください:

```
inject_knowledge ツールで keyword: "@E2Eテストオーケストレーター"
を実行してから開始してください。(初回必須・compact後も必須)
```

重要:キーワードは "@E2Eテストオーケストレーター"
をそのまま使用してください。変換や推測は不要です。

準備完了です。まず知識注入を実行してから、タスクを開始してください。

---

**E2Eテストオーケストレーター実行中の判定**:
- SCOPE_PROGRESS.mdに「## 📊 E2Eテスト全体進捗」が存在する場合
- または、セッション再開時に前回のメッセージに「E2Eテスト」「オーケストレーター」キーワードがある場合

**セッション開始時・compact後の自動処理**:
1. 上記の判定基準でE2Eテスト実行中と判定
2. inject_knowledge('@E2Eテストオーケストレーター') を必ず実行
3. docs/e2e-best-practices.md の存在確認(なければ初期テンプレート作成)
4. SCOPE_PROGRESS.mdから [ ] テストの続きを自動で特定
5. [x] のテストは絶対にスキップ
6. ユーザー確認不要、完全自律モードで継続
7. ページ選定も自動(未完了ページを上から順に選択)
8. 停止条件:全テスト100%完了のみ

**5回エスカレーション後の処理**:
- チェックリストに [-] マークを付ける
- docs/e2e-test-history/skipped-tests.md に記録
- 次のテストへ自動で進む(停止しない)

**ベストプラクティス自動蓄積**:
- 各テストで成功した方法を docs/e2e-best-practices.md に自動保存
- 後続テストが前のテストの知見を自動活用
- 試行錯誤が減っていく(学習効果)

**重要**:
- この原則はCLAUDE.mdに記載されているため、compact後も自動で適用される
- セッション開始時にこのセクションがない場合、オーケストレーターが自動で追加する