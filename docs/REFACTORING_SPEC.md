# リファクタリング設計書 - Stock Harvest AI

## 概要

本設計書は5つの包括的調査レポートに基づき、Stock Harvest AIプロジェクトの品質向上とコード最適化を目的とした戦略的リファクタリング計画を定義します。

### 評価サマリー
- **フロントエンド**: A+ (極めて良好)
- **バックエンド**: 85/100 (優秀な3層アーキテクチャ)
- **技術的負債**: 7.0/10 (良好だが改善の余地あり)

## 1. 即座に削除するファイル(刹那性の原則)

### 削除対象リスト

#### 1.1 重複コンテンツ(約160KB)
- `netlify-deploy/` - 完全重複ディレクトリ
- `simple-version/` - 開発初期の試作版
- `mockups/` - 完成版では不要なモックアップ

#### 1.2 ログファイル(約500KB)
- `backend-type-check.log`
- `build-output.log`
- `ts-errors-frontend.log`
- `backend/server*.log` (14ファイル)
- `frontend/client.log`
- `frontend/dev.log`
- `frontend/build-output.log`

#### 1.3 テスト結果ファイル(約200KB)
- `frontend/test-results/` 全体(305件の蓄積ファイル)
- `backend/*.json` (milestone_report等)
- `backend/final_e2e_test_report.md`

#### 1.4 一時ファイル・不要設定
- `app.js` (ルート直下の孤立ファイル)
- `package.json` (ルート直下、不適切配置)
- `backend/package.json` (Python プロジェクトで不適切)
- `history.html`, `simple.html`, `ultra-*.html`
- `index.html` (ルート直下の孤立ファイル)

### 削除コマンド

```bash
# Phase 1: 重複ディレクトリの削除
rm -rf netlify-deploy/
rm -rf simple-version/
rm -rf mockups/

# Phase 2: ログファイルの一括削除
find . -name "*.log" -type f -delete
find . -name "server*.log" -type f -delete

# Phase 3: テスト結果の削除
rm -rf frontend/test-results/
rm -f backend/*_report.json
rm -f backend/*_report.md

# Phase 4: 孤立ファイルの削除
rm -f app.js package.json index.html history.html simple.html ultra-*.html
rm -f backend/package.json
rm -f ts-errors-frontend.log

# Phase 5: 一時テストファイルの削除
rm -f backend/test_*.py
rm -f backend/simple_*.py
rm -f backend/comprehensive_*.py
rm -f backend/quality_*.py
rm -f backend/run_*.py
rm -f backend/chart_*.py
```

## 2. 設定ファイルの修正

### 2.1 CLAUDE.md の技術スタック更新

#### 現在の記載vs実際の差異修正
```yaml
# 修正前
frontend: 
  - React 18        # → React 19に更新
  - MUI v6          # → MUI v7に更新
  - Vite 5          # → 最新版確認

# 追加項目
  - Playwright (E2Eテスト)
  - Zustand (状態管理実装済み)
  - React Query (データフェッチング)
```

#### ポート設定の確認
```yaml
# 実際の設定と一致性確認
frontend: 3247    # vite.config.ts確認
backend: 8432     # main.py確認
```

### 2.2 不適切な設定ファイル対応
- `backend/railway.json`: Railway特化設定、汎用性確認
- `backend/render.yaml`: Render特化設定、汎用性確認
- `vercel.json`: Vercel特化設定、汎用性確認

## 3. 大型ファイル分割計画

### 3.1 DashboardPage.tsx の分割(476行)

#### 分割戦略
```
DashboardPage.tsx (476行) → 分割後:
├── DashboardPage.tsx (100-120行) - メインコンポーネント
├── components/dashboard/
│   ├── StockScanSection.tsx (80-100行)
│   ├── MetricsSection.tsx (60-80行)
│   ├── ChartsSection.tsx (100-120行)
│   └── AlertsSection.tsx (80-100行)
└── hooks/dashboard/
    ├── useDashboardLayout.ts
    └── useScanControls.ts
```

#### 責任分離
- **DashboardPage**: レイアウト・状態管理・ページ全体のオーケストレーション
- **StockScanSection**: スキャン機能・実行状態管理
- **MetricsSection**: 統計データ表示・KPI可視化  
- **ChartsSection**: チャート表示・ズーム・フィルタリング
- **AlertsSection**: アラート一覧・管理機能

### 3.2 scan_service.py の分割(469行)

#### 分割戦略
```
scan_service.py (469行) → 分割後:
├── scan_service.py (100-120行) - 公開API・オーケストレーション
├── services/scan/
│   ├── stock_data_fetcher.py (100-120行)
│   ├── technical_analyzer.py (120-140行)
│   ├── signal_generator.py (100-120行)
│   └── scan_executor.py (80-100行)
└── utils/scan/
    ├── data_validator.py
    └── performance_tracker.py
```

#### 責任分離
- **scan_service**: 公開API・エラーハンドリング・結果統合
- **stock_data_fetcher**: Yahoo Finance APIアクセス・データ取得
- **technical_analyzer**: テクニカル指標計算・トレンド分析
- **signal_generator**: 売買シグナル生成・アラート判定
- **scan_executor**: バッチ処理・並列実行制御

### 3.3 重要な制約

**⚠️ types/index.ts は分割しない（単一真実源の原則）**
- フロントエンド: `src/types/index.ts`
- バックエンド: `src/types/index.ts`  
- 両ファイルは完全同期を維持
- API契約の一貫性保証のため、分割は絶対に禁止

## 4. 命名規則の統一

### 4.1 Pythonファイル名修正リスト

#### ファイル名命名規則統一
```python
# 現在 → 修正後
alerts_controller.py → alerts_controller.py ✓ (適合済み)
charts_controller.py → charts_controller.py ✓ (適合済み)
scan_controller.py → scan_controller.py ✓ (適合済み)

# サービス層
alerts_service.py → alerts_service.py ✓ (適合済み)
charts_service.py → charts_service.py ✓ (適合済み)
scan_service.py → scan_service.py ✓ (適合済み)

# リポジトリ層
alerts_repository.py → alerts_repository.py ✓ (適合済み)
scan_repository.py → scan_repository.py ✓ (適合済み)
```

#### クラス名・関数名統一
```python
# snake_case → camelCase (必要に応じて)
class ScanService:     # ✓ PascalCase適合済み
    def execute_scan() # ✓ snake_case適合済み
    
# 定数名統一
SCAN_TIMEOUT = 300     # ✓ UPPER_SNAKE_CASE適合済み
MAX_STOCKS = 1000      # ✓ UPPER_SNAKE_CASE適合済み
```

### 4.2 TypeScript命名規則確認

#### インターフェース・型定義
```typescript
// 既存命名の品質確認
interface StockData { } ✓ PascalCase適合
interface TechnicalSignals { } ✓ PascalCase適合
type AlertType = string; ✓ PascalCase適合

// 関数・変数名確認
const fetchStockData = () => { }; ✓ camelCase適合
const SCAN_INTERVALS = { }; ✓ UPPER_SNAKE_CASE適合
```

## 5. 品質向上計画

### 5.1 デバッグコード削除

#### console.log削除対象
```bash
# フロントエンドのデバッグコード検索・削除
rg "console\.(log|debug|warn)" frontend/src/ --type ts --type tsx

# バックエンドのprint文削除
rg "print\(" backend/src/ --type py

# 削除優先度
# 1. console.log() - 本番環境への影響大
# 2. print() - ログ肥大化の原因
# 3. debugger; - 実行停止リスク
```

#### TODO/FIXMEコメント整理
```bash
# 技術的負債コメントの分類
rg "TODO|FIXME|XXX|HACK" . --type ts --type tsx --type py

# 対応方針
# TODO: Issue化 → GitHub Issues登録
# FIXME: 即座対応 → 当リファクタリングで解決
# XXX/HACK: リファクタリング → 適切な実装に置換
```

### 5.2 エラーハンドリング改善

#### フロントエンドのエラー処理強化
```typescript
// API呼び出しエラー処理
try {
  const result = await apiCall();
} catch (error) {
  // 統一エラーハンドリング実装
  handleApiError(error);
  showUserFriendlyMessage(error);
}

// グローバルエラーバウンダリ実装
<ErrorBoundary fallback={ErrorFallback}>
  <App />
</ErrorBoundary>
```

#### バックエンドのエラー処理強化
```python
# HTTP例外の統一処理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return standardized_error_response(exc)

# バリデーションエラーの詳細化
@app.exception_handler(ValidationError)  
async def validation_exception_handler(request, exc):
    return detailed_validation_error(exc)
```

### 5.3 TypeScript型安全性強化

#### strictモード設定確認
```json
// tsconfig.json 厳密設定
{
  "compilerOptions": {
    "strict": true,              ✓ 有効済み
    "noUnusedLocals": true,      ✓ 有効済み
    "noUnusedParameters": true,  ✓ 有効済み
    "exactOptionalPropertyTypes": true // 追加推奨
  }
}
```

## 6. 並列実行計画

### 6.1 Phase 3での最適エージェント配置

#### 作業量分析に基づく配置
```
総作業見積り: 160タスク
最適並列度: 4エージェント (40タスク/エージェント)
推定完了時間: 3-4時間
```

#### エージェント分担

**🧹 クリーンアップエージェント (1名)**
- 対象: 削除作業全般 (40タスク)
- スコープ:
  - 重複ディレクトリ削除 (10タスク)
  - ログファイル削除 (15タスク) 
  - テスト結果削除 (10タスク)
  - 孤立ファイル削除 (5タスク)

**🔧 ファイル分割エージェント (2名)**
- 対象: 大型ファイル分割 (80タスク = 40タスク×2)
- **エージェント A**: DashboardPage.tsx分割
  - コンポーネント分離 (20タスク)
  - hooks分離 (10タスク)
  - テスト移行 (10タスク)
- **エージェント B**: scan_service.py分割  
  - サービス分離 (25タスク)
  - ユーティリティ分離 (10タスク)
  - テスト移行 (5タスク)

**⚡ 品質向上エージェント (1名)**  
- 対象: コード品質向上 (40タスク)
- スコープ:
  - デバッグコード削除 (15タスク)
  - エラーハンドリング改善 (15タスク)
  - 命名規則統一 (5タスク)
  - 設定ファイル修正 (5タスク)

### 6.2 実行順序と依存関係

#### Phase 3A: 並列実行可能（依存なし）
```
🧹 クリーンアップエージェント: 即座開始
⚡ 品質向上エージェント: 即座開始  
```

#### Phase 3B: ファイル分割（クリーンアップ完了後）
```
🔧 ファイル分割エージェント A & B: 
- 前提条件: クリーンアップ完了
- types/index.ts 同期: リアルタイム協調
```

### 6.3 品質保証計画

#### 分割後の自動テスト実行
```bash
# フロントエンド: 分割後の動作確認
npm run test
npm run build
npm run dev # 動作確認

# バックエンド: 分割後のAPI確認  
python -m pytest tests/
python main.py # サーバー起動確認
```

#### 型安全性の検証
```bash
# TypeScript型チェック
npx tsc --noEmit

# Python型ヒント検証
mypy backend/src/
```

## 7. 成果指標とKPI

### 7.1 定量的指標

#### コード品質向上
```
- ファイルサイズ削減: 約1MB → 0MB (不要ファイル)
- 大型ファイル解消: 2ファイル → 0ファイル (400行超)
- TypeScriptエラー: 現在値 → 0件
- 未使用コード: 検出・削除完了
```

#### 保守性向上
```
- 平均ファイル行数: 削減目標 50-150行
- 責任分離度: Single Responsibility Principle適合率 100%
- 命名規則適合率: 100%
- テストカバレッジ: 現状維持+分割後コンポーネント対応
```

### 7.2 定性的指標

#### 開発者体験向上
- ファイル検索性向上
- 機能追加時の影響範囲明確化
- デバッグ効率向上
- コードレビュー容易性向上

#### 運用品質向上  
- 本番環境でのデバッグコード除去
- エラー追跡精度向上
- ログ出力最適化
- セキュリティリスク軽減

## 8. リスク管理と回避策

### 8.1 高リスク作業

#### types/index.ts 同期リスク
```
リスク: フロントエンド・バックエンド間の型定義不整合
回避策: 
- 分割作業前後でのファイル比較検証
- TypeScriptコンパイル確認
- API呼び出しテスト実行
```

#### 大型ファイル分割時のロジック欠落リスク
```
リスク: 分割時の機能ロジック欠落・重複
回避策:
- 分割前の完全テスト実行・結果保存
- 分割後の同一テスト実行・結果比較
- 段階的分割・各段階での動作確認
```

### 8.2 ロールバック計画

#### Git ブランチ戦略
```bash
# 作業開始前
git checkout -b refactoring/phase3-comprehensive
git push -u origin refactoring/phase3-comprehensive

# マイルストーン毎のコミット
git commit -m "feat: クリーンアップ完了"
git commit -m "feat: DashboardPage分割完了"  
git commit -m "feat: scan_service分割完了"
git commit -m "feat: 品質向上完了"

# 問題発生時のロールバック
git checkout main
git branch -D refactoring/phase3-comprehensive
```

## 9. 実行タイムライン

### 9.1 Phase 3 実行スケジュール

#### Day 1: 準備・クリーンアップ
```
午前: 設定ファイル修正・環境確認
午後: クリーンアップエージェント実行
夕方: 削除結果検証・コミット
```

#### Day 2: ファイル分割実行
```  
午前: DashboardPage.tsx分割
午後: scan_service.py分割
夕方: 分割結果テスト・検証
```

#### Day 3: 品質向上・総合テスト
```
午前: デバッグコード削除・エラーハンドリング改善
午後: 命名規則統一・最終検証
夕方: 総合テスト・リリース準備
```

### 9.2 完了判定基準

#### 必須条件(すべて満たすこと)
- [ ] TypeScriptコンパイルエラー 0件
- [ ] Pythonテスト実行成功
- [ ] フロントエンド開発サーバー起動成功  
- [ ] バックエンドサーバー起動成功
- [ ] 削除対象ファイル 0件
- [ ] 400行超ファイル 0件

#### 推奨条件(品質向上確認)
- [ ] console.log等デバッグコード 0件
- [ ] 命名規則違反 0件
- [ ] エラーハンドリング統一済み
- [ ] 技術的負債スコア 8.5+/10

---

## 結論

本リファクタリング設計書に基づく実行により、Stock Harvest AIプロジェクトの保守性・可読性・品質が大幅に向上し、継続的な機能開発に適した基盤が構築されます。特に刹那性の原則による不要ファイル即座削除と、型安全性を保った適切なファイル分割により、開発効率と運用品質の両面で顕著な改善が期待できます。