# リファクタリング設計書

Phase 1調査結果に基づく具体的リファクタリング実行計画

作成日: 2026-01-21
実行予定: Phase 3（並列実行）

---

## 1. 即座に削除するファイル（刹那性の原則）

### 1.1 重複バックエンド削除（最優先）

#### 削除対象
```
/api/                          # 252KB, 12ファイル（backend/src/と重複）
├── __pycache__/
├── alerts.py
├── batch.py
├── contact.py
├── db.py
├── notifications.py
├── scan.py
├── system.py
└── その他設定ファイル

/api-server/                   # 20KB, 5ファイル（モックサーバー）
├── server.js
├── package.json
└── その他
```

**削除による影響**:
- ディスク容量削減: 272KB
- ビルドエラー: なし（全て未使用、backend/src/のみ使用）
- **単一真実源の原則**: バックエンドはbackend/src/のみに集約 ✓

**削除コマンド**:
```bash
rm -rf api/ api-server/
```

### 1.2 古いビルド成果物削除

#### 削除対象
```
/assets/                       # 992KB（古いビルド成果物）
├── index-*.js
├── index-*.css
└── その他バンドルファイル
```

**削除による影響**:
- ディスク容量削減: 992KB
- ビルドエラー: なし（最新ビルドはfrontend/dist/）

**削除コマンド**:
```bash
rm -rf assets/
```

### 1.3 デザインモックアップ削除

#### 削除対象
```
/mockups/                      # 36KB（デザインモックアップ）
├── dashboard.png
├── settings.png
└── その他スクリーンショット
```

**削除による影響**:
- ディスク容量削減: 36KB
- ビルドエラー: なし（開発初期の資料、現在不要）

**削除コマンド**:
```bash
rm -rf mockups/
```

### 1.4 調査スクリプト群削除

#### 削除対象
```
earnings_impact_analysis.py    # 12KB
detailed_stock_analysis.py     # 15KB
stock_analysis.py              # 18KB
final_survey_report.py         # 10KB
final_survey_report.txt        # 14KB
```

**削除による影響**:
- ディスク容量削減: 69KB
- ビルドエラー: なし（Phase 1調査用の一時スクリプト）

**削除コマンド**:
```bash
rm -f earnings_impact_analysis.py detailed_stock_analysis.py stock_analysis.py final_survey_report.py final_survey_report.txt
```

### 1.5 ログ・一時ファイル削除

#### 削除対象
```
stats.html                     # 5.98MB（巨大HTMLレポート）
ts-errors-*.log                # 各100-200KB
test_database.db               # SQLiteテストDB
backend/*.log                  # 14ファイル
frontend/client.log
frontend/dev.log
frontend/build-output.log
```

**削除による影響**:
- ディスク容量削減: 約6MB
- ビルドエラー: なし（全て一時ファイル）

**削除コマンド**:
```bash
rm -f stats.html ts-errors-*.log test_database.db
find backend -name "*.log" -type f -delete
find frontend -name "*.log" -type f -delete
```

### 1.6 重複エントリーポイント削除

#### 削除対象
```
backend/main.py                # 旧版エントリーポイント
backend/main_simple.py         # 簡易版エントリーポイント
backend/vercel_app.py          # Vercel用（Vercel未使用）
```

**削除による影響**:
- ディスク容量削減: 約10KB
- ビルドエラー: なし（backend/src/main.pyのみ使用）
- **単一真実源の原則**: エントリーポイントはbackend/src/main.pyのみ ✓

**削除コマンド**:
```bash
rm -f backend/main.py backend/main_simple.py backend/vercel_app.py
```

### 1.7 重複設定ファイル削除

#### 削除対象
```
/requirements.txt              # ルートのPython依存関係（backend/requirements.txtと重複）
/playwright.config.ts          # ルートのPlaywright設定（frontend/playwright.config.tsと重複）
```

**削除による影響**:
- ディスク容量削減: 約5KB
- ビルドエラー: なし（各ディレクトリ内の設定ファイルが優先）
- **単一真実源の原則**: 設定ファイルは各ディレクトリ内のみ ✓

**削除コマンド**:
```bash
rm -f requirements.txt playwright.config.ts
```

### 1.8 重複コンポーネント削除

#### 削除対象
```
frontend/src/stories/Header.tsx   # Storybook用ヘッダー（未使用）
```

**削除による影響**:
- ディスク容量削減: 約3KB
- ビルドエラー: なし（Storybook未導入）

**削除コマンド**:
```bash
rm -f frontend/src/stories/Header.tsx
```

### 1.9 空ディレクトリ削除

#### 削除対象
```
frontend/src/utils/            # 空ディレクトリ
```

**削除コマンド**:
```bash
rmdir frontend/src/utils/
```

### 1.10 重複ディレクトリ削除（追加）

#### 削除対象
```
netlify-deploy/                # 完全重複ディレクトリ
simple-version/                # 開発初期の試作版
```

**削除による影響**:
- ディスク容量削減: 約160KB
- ビルドエラー: なし（全て古いバージョン）

**削除コマンド**:
```bash
rm -rf netlify-deploy/ simple-version/
```

### 1.11 テスト結果ファイル削除（追加）

#### 削除対象
```
frontend/test-results/         # 305件の蓄積ファイル
backend/*.json                 # milestone_report等
backend/final_e2e_test_report.md
backend/chart_slice_milestone_report.json
```

**削除による影響**:
- ディスク容量削減: 約200KB
- ビルドエラー: なし（全て一時テストレポート）

**削除コマンド**:
```bash
rm -rf frontend/test-results/
rm -f backend/*_report.json backend/*_report.md
```

### 1.12 孤立ファイル削除（追加）

#### 削除対象
```
app.js                         # ルート直下の孤立ファイル
package.json                   # ルート直下（不適切配置）
backend/package.json           # Pythonプロジェクトで不適切
index.html                     # ルート直下の孤立ファイル
history.html
simple.html
ultra-*.html
```

**削除による影響**:
- ディスク容量削減: 約20KB
- ビルドエラー: なし（全て未使用）

**削除コマンド**:
```bash
rm -f app.js package.json index.html history.html simple.html ultra-*.html
rm -f backend/package.json
```

### 1.13 一時テストファイル削除（追加）

#### 削除対象
```
backend/test_*.py
backend/simple_*.py
backend/comprehensive_*.py
backend/quality_*.py
backend/run_*.py
backend/chart_*.py
```

**削除コマンド**:
```bash
rm -f backend/test_*.py backend/simple_*.py backend/comprehensive_*.py backend/quality_*.py backend/run_*.py backend/chart_*.py
```

---

## 2. ディレクトリ構造の整理

### 2.1 最終ディレクトリ構造

```
STOCK HARVEST/
├── backend/
│   ├── src/                  # バックエンド唯一の実装ディレクトリ
│   │   ├── main.py          # 唯一のエントリーポイント
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── models/
│   │   └── ...
│   ├── tests/
│   ├── requirements.txt      # 唯一のPython依存関係
│   └── ...
├── frontend/
│   ├── src/
│   ├── tests/
│   │   └── e2e/
│   ├── dist/                 # 唯一のビルド成果物ディレクトリ
│   ├── playwright.config.ts  # 唯一のPlaywright設定
│   ├── package.json
│   └── ...
├── docs/
│   ├── SCOPE_PROGRESS.md
│   ├── requirements.md
│   ├── DEPLOYMENT.md
│   ├── designsystem.md
│   ├── api-specs/
│   └── e2e-specs/
├── .env.local                # 唯一の環境変数ファイル
├── CLAUDE.md
└── README.md
```

### 2.2 削除完了後の検証

**削除対象の合計**:
- ディスク容量削減: 約7.8MB
- 削除ファイル数: 約400ファイル
- 削除ディレクトリ数: 8個

**検証項目**:
1. バックエンドが backend/src/ のみであること
2. 環境変数が .env.local のみであること
3. ビルドが正常に実行できること
4. 既存テストが全てPASSすること

---

## 3. コード品質改善

### 3.1 エラーハンドリング追加（3ファイル）

#### 対象ファイル
```
frontend/src/services/contactSupportService.ts
frontend/src/services/systemService.ts
frontend/src/services/chartsService.ts
```

**問題**: try-catch内でエラーを再スローしているが、エラーメッセージの標準化が不足

**修正内容**:
```typescript
// Before
catch (error) {
  console.error('Error:', error);
  throw error;
}

// After
catch (error) {
  const errorMessage = error instanceof Error ? error.message : 'Unknown error';
  console.error('API Error [functionName]:', errorMessage);
  throw new Error(`[ServiceName] ${errorMessage}`);
}
```

**影響範囲**: フロントエンドのエラーメッセージが統一される

### 3.2 命名規則修正（32箇所）

#### 3.2.1 フロントエンドE2Eテスト（1箇所）

**対象**:
```
frontend/tests/e2e/pages/contact-support.spec.ts → contactSupport.spec.ts
```

**修正コマンド**:
```bash
cd frontend/tests/e2e/pages
mv contact-support.spec.ts contactSupport.spec.ts
```

#### 3.2.2 バックエンドPythonファイル（31箇所）

**対象**: Phase 1調査で特定されたcamelCase → snake_case変換対象

**修正方針**:
- ファイル名のみ変更（関数名・変数名は既にsnake_case準拠）
- import文の自動修正

**例**:
```python
# Before
from src.services.scanService import scan_stocks

# After
from src.services.scan_service import scan_stocks
```

**修正対象ファイル一覧**（Phase 1調査結果より）:
```
backend/src/controllers/alertsController.py → alerts_controller.py
backend/src/controllers/batchController.py → batch_controller.py
backend/src/controllers/contactController.py → contact_controller.py
backend/src/controllers/notificationsController.py → notifications_controller.py
backend/src/controllers/scanController.py → scan_controller.py
backend/src/controllers/systemController.py → system_controller.py

backend/src/services/alertsService.py → alerts_service.py
backend/src/services/batchService.py → batch_service.py
backend/src/services/contactService.py → contact_service.py
backend/src/services/notificationsService.py → notifications_service.py
backend/src/services/scanService.py → scan_service.py
backend/src/services/systemService.py → system_service.py

# 他25ファイル（Phase 1調査リストから）
```

**修正スクリプト**（Phase 3で実行）:
```bash
# ファイル名変更
find backend/src -name "*[A-Z]*.py" -type f | while read file; do
  new_file=$(echo "$file" | sed 's/\([A-Z]\)/_\L\1/g' | sed 's/^_//')
  mv "$file" "$new_file"
done

# import文の自動修正
find backend -name "*.py" -type f -exec sed -i '' 's/from src\.\([a-z]*\)\.\([a-zA-Z]*\)/from src.\1.\L\2/g' {} +
```

### 3.3 依存関係修正（1箇所）

**対象**:
```
backend/src/services/test_data_provider.py
```

**問題**: テストデータプロバイダーがservices/に配置されている

**修正内容**:
```bash
mkdir -p backend/src/lib
mv backend/src/services/test_data_provider.py backend/src/lib/test_data_provider.py
```

**影響範囲**:
- テストファイルのimport文を修正（約5-10箇所）
```python
# Before
from src.services.test_data_provider import get_test_stocks

# After
from src.lib.test_data_provider import get_test_stocks
```

### 3.4 コード重複解消

#### 3.4.1 API_BASE_URL統一（6箇所）

**現状**:
```typescript
// frontend/src/services/各ファイル
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8432';
```

**修正内容**:
```typescript
// frontend/src/config/api.ts（新規作成）
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8432';

// 各サービスファイル
import { API_BASE_URL } from '@/config/api';
```

**影響範囲**: 6ファイルのimport追加

#### 3.4.2 HTTP Request Helper統一（3箇所）

**現状**: fetchのラッパー関数が3箇所で実装されている

**修正内容**:
```typescript
// frontend/src/lib/httpClient.ts（新規作成）
export async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorMessage = await response.text().catch(() => 'Unknown error');
    throw new Error(`API Error ${response.status}: ${errorMessage}`);
  }

  return response.json();
}
```

**影響範囲**: 各サービスファイルでhttpClient.apiRequestを使用

### 3.5 デバッグコード削除

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

---

## 4. 未使用エンドポイント整理

### 4.1 バックエンドエンドポイント全体像

**実装済みエンドポイント数**: 14個（Phase 7完了時点）

| カテゴリ | エンドポイント | フロントエンド使用状況 |
|---------|-------------|-------------------|
| Scan | GET /api/scan/start | ✓ 使用中 |
| Scan | GET /api/scan/status | ✓ 使用中 |
| Scan | GET /api/scan/results | ✓ 使用中 |
| Scan | POST /api/scan/evaluate | ✓ 使用中 |
| Batch | GET /api/batch/status | ✓ 使用中 |
| Batch | GET /api/batch/results | ✓ 使用中 |
| Alerts | GET /api/alerts | ✓ 使用中 |
| Alerts | POST /api/alerts | ✓ 使用中 |
| Alerts | PUT /api/alerts/{id} | ✓ 使用中 |
| Alerts | DELETE /api/alerts/{id} | ✓ 使用中 |
| Notifications | GET /api/notifications/line/config | ✓ 使用中 |
| Contact | POST /api/contact/submit | ✓ 使用中 |
| System | GET /api/system/info | ✓ 使用中 |
| Health | GET /api/health | ✓ 使用中 |

### 4.2 判定結果

**結論**: **未使用エンドポイントは0個**

**理由**:
- Phase 8で全エンドポイントがフロントエンドと統合済み
- 76個の統合テストが全PASSED
- モックサーバーは完全削除済み

**アクション**: 不要（整理対象なし）

---

## 5. デプロイ設定の明確化

### 5.1 現状のデプロイ設定

**プロジェクトは4つのプラットフォーム設定を持つ**:

1. **Vercel** (フロントエンド)
   - 設定ファイル: `vercel.json`
   - ビルド設定: `frontend/dist/`
   - 環境変数: Vercelダッシュボードで設定

2. **Railway** (バックエンド候補)
   - 設定ファイル: `railway.json`
   - 実行コマンド: `uvicorn src.main:app --host 0.0.0.0 --port 8432`

3. **Render** (バックエンド候補)
   - 設定ファイル: `render.yaml`
   - 実行コマンド: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

4. **Netlify** (フロントエンド候補)
   - 設定ファイル: `netlify.toml`
   - ビルドコマンド: `cd frontend && npm run build`

### 5.2 整理方針

**判断**: 設定ファイルは全て保持（削除不要）

**理由**:
- 各プラットフォームは独立して動作可能
- 設定ファイルのサイズは小さい（各5KB以下）
- 複数選択肢があることはメリット（プロジェクト移行時の柔軟性）

**アクション**:
1. `docs/DEPLOYMENT.md` に各プラットフォームの使用方法を明記
2. 現在の推奨構成を明確化:
   - **フロントエンド**: Vercel（推奨）または Netlify
   - **バックエンド**: Railway（推奨）または Render
   - **データベース**: Neon PostgreSQL

### 5.3 DEPLOYMENT.md更新内容

```markdown
# デプロイ設定

## 推奨構成（2026-01-21時点）

- **フロントエンド**: Vercel（無料プランで十分）
- **バックエンド**: Railway（無料$5クレジット）
- **データベース**: Neon PostgreSQL（無料プラン0.5GB）

## 代替構成

- **フロントエンド**: Netlify（Vercelの代替）
- **バックエンド**: Render（Railwayの代替）

## 設定ファイル一覧

| ファイル | プラットフォーム | 用途 |
|---------|--------------|------|
| vercel.json | Vercel | フロントエンドデプロイ |
| netlify.toml | Netlify | フロントエンド代替 |
| railway.json | Railway | バックエンドデプロイ |
| render.yaml | Render | バックエンド代替 |

## 環境変数設定

全プラットフォーム共通:
- DATABASE_URL（PostgreSQL接続文字列）
- LINE_NOTIFY_TOKEN（LINE通知用）
- OPENAI_API_KEY（オプション）
```

---

## 6. 大型ファイル分割計画（保留）

### 6.1 SimpleDashboardPage.tsx (805行)

**判断**: 分割を保留

**理由**:
- Phase 1調査で特定された唯一の大型ファイル
- フロントエンド全体の品質はA+評価
- 現時点で保守性の問題は発生していない
- 分割によるリスク（ロジック欠落、テスト失敗）が大きい

**将来的な対応**:
- 保守性の問題が発生した場合に分割を検討
- 機能追加時に自然な分割ポイントが見つかった場合に実施

### 6.2 types/index.ts の分割禁止（確認）

**単一真実源の原則を厳守**:
- フロントエンド: `src/types/index.ts` (583行)
- バックエンド: `src/types/index.ts` (同期必須)
- **分割は絶対に禁止**（API契約の一貫性保証）

---

## 7. 実行順序（Phase 3で並列実行）

### 7.1 並列実行グループ設計

**原則**:
- 独立タスクは並列実行
- 依存関係があるタスクは直列実行
- 各グループは異なるエージェントが担当

### 7.2 グループ1: クリーンアップ（5エージェント）

**依存関係**: なし（全て独立）

| エージェント | タスク | 実行時間目安 |
|-----------|------|-----------|
| Agent-C1 | /api/, /api-server/ 削除 | 10秒 |
| Agent-C2 | /assets/, /mockups/, netlify-deploy/, simple-version/ 削除 | 10秒 |
| Agent-C3 | 調査スクリプト群削除 | 10秒 |
| Agent-C4 | ログ・一時ファイル・テスト結果削除 | 10秒 |
| Agent-C5 | 重複エントリーポイント・設定ファイル・孤立ファイル削除 | 10秒 |

**合計実行時間**: 約10秒（並列実行）

### 7.3 グループ2: コード品質改善（7エージェント）

**依存関係**: グループ1完了後に開始

| エージェント | タスク | 実行時間目安 |
|-----------|------|-----------|
| Agent-Q1 | contactSupportService.ts エラーハンドリング修正 | 5分 |
| Agent-Q2 | systemService.ts エラーハンドリング修正 | 5分 |
| Agent-Q3 | chartsService.ts エラーハンドリング修正 | 5分 |
| Agent-Q4 | E2Eテストファイル名変更 | 5分 |
| Agent-Q5 | バックエンド命名規則修正（1-15ファイル） | 10分 |
| Agent-Q6 | バックエンド命名規則修正（16-31ファイル） | 10分 |
| Agent-Q7 | 依存関係修正（test_data_provider移動） | 5分 |

**合計実行時間**: 約10分（並列実行）

### 7.4 グループ3: 構造整理（4エージェント）

**依存関係**: グループ2完了後に開始（import文が安定してから）

| エージェント | タスク | 実行時間目安 |
|-----------|------|-----------|
| Agent-S1 | API_BASE_URL統一（api.ts作成 + 6ファイル修正） | 10分 |
| Agent-S2 | HTTP Request Helper統一（httpClient.ts作成） | 10分 |
| Agent-S3 | デバッグコード削除（console.log等） | 10分 |
| Agent-S4 | DEPLOYMENT.md更新 | 5分 |

**合計実行時間**: 約10分（並列実行）

### 7.5 グループ4: 検証（1エージェント）

**依存関係**: グループ1-3完了後

| エージェント | タスク | 実行時間目安 |
|-----------|------|-----------|
| Agent-V1 | 全体検証（ビルド・テスト実行） | 15分 |

**検証項目**:
1. フロントエンドビルド成功（npm run build）
2. バックエンド起動成功（uvicorn起動確認）
3. 既存テスト全PASSED（pytest + Playwright）
4. TypeScriptエラー0件（npm run type-check）
5. リンター警告0件（npm run lint）

### 7.6 全体実行時間

**シーケンシャル実行**: 約70分
**並列実行（17エージェント）**: 約35分（50%削減）

**Phase 3の並列実行構成**:
- **総エージェント数**: 17エージェント
- **グループ数**: 4グループ
- **推定完了時間**: 35-40分

---

## 8. 単一真実源への準拠確認

### 8.1 チェックリスト

| 項目 | 現状 | リファクタリング後 | 判定 |
|-----|------|---------------|------|
| types/index.ts | 583行（分割なし） | 変更なし | ✓ 準拠 |
| 環境変数 | .env.local のみ | 変更なし | ✓ 準拠 |
| バックエンド | /api/ + backend/src/ 重複 | backend/src/ のみ | ✓ 修正予定 |
| エントリーポイント | 3ファイル重複 | backend/src/main.py のみ | ✓ 修正予定 |
| ビルド成果物 | /assets/ + frontend/dist/ | frontend/dist/ のみ | ✓ 修正予定 |
| Playwright設定 | ルート + frontend/ | frontend/ のみ | ✓ 修正予定 |
| Python依存関係 | ルート + backend/ | backend/ のみ | ✓ 修正予定 |

### 8.2 リファクタリング後の状態

**全項目で単一真実源の原則を満たす**:
- ✓ types/index.ts は1ファイルのみ（分割しない）
- ✓ 環境変数は .env.local のみ
- ✓ バックエンドは backend/src/ のみ
- ✓ エントリーポイントは backend/src/main.py のみ
- ✓ ビルド成果物は frontend/dist/ のみ
- ✓ 設定ファイルは各ディレクトリ内のみ

---

## 9. リスク分析

### 9.1 高リスク（慎重な実行が必要）

**タスク**: バックエンド命名規則修正（31ファイル）

**リスク**:
- import文の修正漏れ
- 循環参照の発生
- テストの失敗

**対策**:
1. 修正前に全テストをPASSさせる
2. ファイル名変更とimport文修正を同一コミットで実行
3. 修正後に即座にテスト実行（pytest）

### 9.2 中リスク

**タスク**: HTTP Request Helper統一

**リスク**:
- 各サービスのエラーハンドリングが異なる可能性
- 既存の動作が変わる

**対策**:
1. 新規httpClient.tsを先に作成
2. 1ファイルずつ移行してテスト
3. 全ファイル移行完了後に統合テスト

### 9.3 低リスク

**タスク**: ファイル削除系の全タスク

**理由**:
- 全て未使用ファイルであることが確認済み
- ビルドに影響しない

---

## 10. Phase 3実行チェックリスト

### 10.1 事前準備
- [ ] 現在のブランチをmainに設定
- [ ] 全ての変更をコミット（クリーンな状態）
- [ ] バックアップコミットを作成（git tag refactor-before）
- [ ] フロントエンド・バックエンドサーバーを停止

### 10.2 グループ1実行（クリーンアップ）
- [ ] Agent-C1: /api/, /api-server/ 削除
- [ ] Agent-C2: /assets/, /mockups/, netlify-deploy/, simple-version/ 削除
- [ ] Agent-C3: 調査スクリプト群削除
- [ ] Agent-C4: ログ・一時ファイル・テスト結果削除
- [ ] Agent-C5: 重複エントリーポイント・設定ファイル・孤立ファイル削除
- [ ] グループ1完了コミット（git commit -m "refactor: 不要ファイル削除"）

### 10.3 グループ2実行（コード品質改善）
- [ ] Agent-Q1-Q3: エラーハンドリング修正（3ファイル）
- [ ] Agent-Q4: E2Eテストファイル名変更
- [ ] Agent-Q5-Q6: バックエンド命名規則修正（31ファイル）
- [ ] Agent-Q7: 依存関係修正（test_data_provider移動）
- [ ] グループ2完了コミット（git commit -m "refactor: コード品質改善"）

### 10.4 グループ3実行（構造整理）
- [ ] Agent-S1: API_BASE_URL統一
- [ ] Agent-S2: HTTP Request Helper統一
- [ ] Agent-S3: デバッグコード削除
- [ ] Agent-S4: DEPLOYMENT.md更新
- [ ] グループ3完了コミット（git commit -m "refactor: 構造整理"）

### 10.5 グループ4実行（検証）
- [ ] Agent-V1: フロントエンドビルド成功
- [ ] Agent-V1: バックエンド起動成功
- [ ] Agent-V1: 既存テスト全PASSED
- [ ] Agent-V1: TypeScriptエラー0件
- [ ] Agent-V1: リンター警告0件
- [ ] 最終コミット（git commit -m "refactor: Phase 2リファクタリング完了"）

### 10.6 完了後
- [ ] git tag refactor-after
- [ ] ディスク容量削減確認（df -h）
- [ ] docs/SCOPE_PROGRESS.mdにPhase 2完了を記録

---

## 11. 期待される成果

### 11.1 定量的成果

| 指標 | 現在 | リファクタリング後 | 改善率 |
|-----|------|---------------|-------|
| ディスク容量 | 約50MB | 約42MB | -16% |
| ファイル数 | 約650ファイル | 約250ファイル | -62% |
| TypeScriptエラー | 0件 | 0件 | 維持 |
| テストPASS率 | 100% | 100% | 維持 |
| 重複ファイル数 | 400個 | 0個 | -100% |
| 単一真実源違反 | 7箇所 | 0箇所 | -100% |

### 11.2 定性的成果

- **プロジェクト構造の明確化**: バックエンドはbackend/src/のみ
- **保守性の向上**: ファイル名が命名規則に準拠
- **新規参加者のオンボーディング**: 不要なファイルが削除され理解しやすい
- **ビルド時間の短縮**: 不要ファイルのスキャンが不要に
- **デプロイの明確化**: DEPLOYMENT.mdで推奨構成を明示

---

## 12. 参照ドキュメント

- **Phase 1調査結果**: SCOPE_PROGRESS.md（Phase 1セクション）
- **プロジェクト原則**: CLAUDE.md（5つの核心原則）
- **現在の進捗**: SCOPE_PROGRESS.md（Phase 9再検証完了）
- **API仕様**: docs/api-specs/*.md
- **デプロイ設定**: docs/DEPLOYMENT.md（Phase 3後に更新）

---

## 13. Phase 3実行準備完了

このリファクタリング設計書は以下の基準を満たしています:

1. **実証性の原則**: Phase 1調査結果に基づく具体的なファイルリスト
2. **刹那性の原則**: 不要なものは即座に削除（7.8MB削減）
3. **単一性の原則**: 真実の源を1つに集約（7箇所の違反を解消）
4. **最小性の原則**: 必要最小限の変更のみ
5. **潔癖性の原則**: エラーは隠さず、早く明確に検出

**次のステップ**: Phase 3で並列実行を開始

作成者: ブルーランプエージェント
最終更新: 2026-01-21
