# 依存関係グラフ解析レポート

**生成日時**: 2026-01-21
**対象**: Stock Harvest AI プロジェクト全体
**解析ファイル数**: 134ファイル
**総import関係数**: 260

---

## 📊 1. import依存関係の統計

### 最も多くimportされているファイル (Top 20)

**1位: backend/src/lib/logger.py (43回)**
- プロジェクト全体で使用される共通ロガー
- ✅ 適切な設計（低レイヤーの共通ユーティリティ）

**2位: backend/src/database/config.py (21回)**
- データベース接続設定
- ✅ 適切な設計（インフラ層）

**3位: frontend/src/types (18回)**
- TypeScript型定義集約ファイル
- ✅ 適切な設計（型定義は最下層）

**4位: backend/src/database/tables.py (14回)**
- データベーステーブル定義
- ✅ 適切な設計（データ層）

**5位: frontend/src/layouts/MainLayout.tsx (5回)**
- メインレイアウトコンポーネント
- ✅ 適切（Pagesから参照される）

**6-20位:**
- backend/src/services/technical_analysis_service.py (5回)
- frontend/src/lib/logger.ts (4回)
- backend/src/services/logic_detection_service.py (4回)
- frontend/src/contexts/AuthContextTypes.ts (3回)
- frontend/src/contexts/AuthContextDefinition.ts (3回)
- backend/src/services/test_data_provider.py (3回)
- backend/src/models/discord_models.py (3回)
- backend/src/models/charts_models.py (3回)
- backend/src/services/stock_data_service.py (3回)
- backend/src/services/listing_data_service.py (3回)
- backend/src/services/price_limit_service.py (3回)
- backend/src/services/irbank_integration_service.py (3回)
- backend/src/services/kabutan_integration_service.py (3回)
- frontend/src/stories/Button.tsx (2回)
- frontend/src/stories/Header.tsx (2回)

### 最もimportしているファイル (Top 20)

**1位: backend/src/main.py (15個)**
- FastAPIアプリケーションエントリーポイント
- ✅ 適切（最上位層がルーターをまとめる）

**2位: backend/src/services/__init__.py (9個)**
- サービス層の集約ファイル
- ✅ 適切（パッケージ初期化）

**3位: frontend/src/pages/DashboardPage.tsx (8個)**
- ダッシュボードページ
- ✅ 適切（Pageは多くのコンポーネントを組み合わせる）

**4-20位:**
- backend/src/controllers/data_source_controller.py (7個)
- backend/src/services/data_source_scheduler_service.py (7個)
- backend/src/controllers/scan_controller.py (6個)
- backend/src/services/enhanced_earnings_service.py (6個)
- backend/src/services/scan_service.py (6個)
- frontend/src/App.tsx (5個)
- frontend/src/contexts/AuthContext.tsx (5個)
- backend/src/services/notification_config_service.py (5個)
- backend/src/services/trading_service.py (5個)
- backend/src/services/charts_service.py (5個)
- frontend/src/pages/ContactSupportPage.tsx (4個)
- backend/src/controllers/system_controller.py (4個)
- backend/src/controllers/notification_controller.py (4個)
- backend/src/controllers/trading_controller.py (4個)
- backend/src/controllers/charts_controller.py (4個)
- backend/src/services/logic_a_strict_service.py (4個)
- backend/src/services/discord_service.py (4個)

---

## 🔍 2. 孤立ファイルの分析

### 2-1. 完全に孤立（何もimportせず、何もimportされない）

**0件** - ✅ すべてのファイルが何らかの形で接続されている

### 2-2. importされるのみ（自分は何もimportしない） - 35件

これらは **リーフノード** として機能する設計（良好）

**主要な例:**
- `backend/src/lib/logger.py` (43回) - ✅ ユーティリティ
- `frontend/src/types` (18回) - ✅ 型定義
- `backend/src/models/*.py` - ✅ データモデル
- `backend/src/validators/*.py` - ✅ バリデーション定義

### 2-3. importするのみ（誰からもimportされない） - 20件

これらは **ルートノード** として機能（良好）

**主要な例:**
- `backend/src/main.py` (15個import) - ✅ エントリーポイント
- `frontend/src/main.tsx` (2個import) - ✅ エントリーポイント
- `frontend/src/pages/*.tsx` - ✅ ページコンポーネント
- `backend/src/database/migrate.py` - ✅ マイグレーションスクリプト
- `backend/src/database/seed_faq_data.py` - ✅ データシードスクリプト
- `*.stories.ts` - ✅ Storybookストーリー

---

## 🔄 3. 循環依存の検出

**結果: 循環依存なし** ✅

プロジェクトのアーキテクチャは非循環有向グラフ (DAG) を形成しており、健全です。

---

## ⚠️ 4. 不適切な依存関係（レイヤー違反）

### 検出された違反: **1件**

#### 違反1: repositories → services

**詳細:**
```
backend/src/repositories/charts_repository.py (repositories層)
  ↓ import
backend/src/services/test_data_provider.py (services層)
```

**問題点:**
- リポジトリ層（データアクセス層）がサービス層（ビジネスロジック層）をimportしている
- 正しい依存方向は `services → repositories` であるべき
- アーキテクチャの依存性逆転原則 (DIP) に違反

**該当コード（18行目）:**
```python
from ..services.test_data_provider import test_data_provider
```

**影響範囲:**
- テストモード時のデータ提供に使用
- 本番コードにはテスト用の依存が混入している状態

**推奨修正方法:**

**方法1: テストデータプロバイダーをlib層に移動**
```
backend/src/services/test_data_provider.py
  ↓ 移動
backend/src/lib/test_data_provider.py
```
- `test_data_provider`はユーティリティとして位置づけ直す
- repositories層からも安全に参照可能

**方法2: 依存性注入 (DI)**
```python
# ChartsRepository.__init__に注入
def __init__(self, data_provider=None):
    self.data_provider = data_provider or ProductionDataProvider()
```

**方法3: インターフェース抽象化**
```python
# backend/src/interfaces/data_provider.py
class DataProviderInterface:
    def get_fixed_stock_data(self, code: str): pass
    def create_mock_api_response(self, symbol: str, period: str): pass
```

---

## 📈 5. コンポーネント間依存関係分析

### 5-1. フロントエンド - コンポーネント間依存

**結果: 依存関係なし** ✅

各コンポーネントが独立しており、良好な設計です。

### 5-2. フロントエンド - フック間依存

**結果: 依存関係なし** ✅

各フックが独立しており、良好な設計です。

### 5-3. バックエンド - サービス間依存

**検出された依存関係:**

```
services/__init__.py
├── alerts_service.py
├── charts_service.py
├── contact_service.py
├── logic_detection_service.py
├── scan_service.py
├── signals_service.py
├── stock_data_service.py
├── system_service.py
└── technical_analysis_service.py

alerts_service.py
└── notification_service.py

charts_service.py
└── test_data_provider.py

data_source_scheduler_service.py
├── irbank_integration_service.py
├── kabutan_integration_service.py
├── listing_data_service.py
└── price_limit_service.py

enhanced_earnings_service.py
├── earnings_analysis_service.py
├── irbank_integration_service.py
└── kabutan_integration_service.py

logic_a_strict_service.py
├── listing_data_service.py
└── price_limit_service.py

notification_config_service.py
└── notification_service.py

scan_service.py
├── logic_a_strict_service.py
├── logic_detection_service.py
├── stock_data_service_enhanced.py
└── technical_analysis_service.py

stock_data_service_enhanced.py
└── test_data_provider.py

trading_service.py
├── real_stock_data_service.py
└── technical_analysis_service.py

trading_signals_service.py
├── logic_detection_service.py
├── stock_data_service.py
└── technical_analysis_service.py
```

**評価: おおむね良好** ✅

サービス層内での依存は許容範囲内です。ただし、以下の点に注意:
- `test_data_provider`の扱い（前述のレイヤー違反の原因）
- サービスの粒度が適切かどうかの継続的なレビューが必要

---

## 📊 6. 依存関係グラフの全体像（テキスト表現）

### フロントエンドアーキテクチャ

```
main.tsx (エントリーポイント)
  ↓
App.tsx
  ├─→ layouts/MainLayout.tsx
  │     └─→ components/Header.tsx
  │     └─→ components/Sidebar.tsx
  ├─→ pages/SimpleDashboardPage.tsx
  │     ├─→ components/dashboard/ScanStatusCard.tsx
  │     ├─→ components/dashboard/LogicResults.tsx
  │     ├─→ components/dashboard/SystemStatus.tsx
  │     ├─→ components/dashboard/TopStocks.tsx
  │     ├─→ components/dashboard/ScoreEvaluationSection.tsx
  │     ├─→ hooks/useDashboardData.ts
  │     └─→ hooks/useScoreEvaluation.ts
  ├─→ pages/AlertsPage.tsx
  │     └─→ hooks/useAlertsData.ts
  ├─→ pages/ContactSupportPage.tsx
  │     └─→ hooks/useContactSupport.ts
  ├─→ pages/AdminPage.tsx
  └─→ contexts/AuthContext.tsx
        ├─→ contexts/AuthContextDefinition.ts
        ├─→ contexts/AuthContextTypes.ts
        ├─→ services/authService.ts
        └─→ services/tokenService.ts

hooks層
├─→ services/api/*.ts
└─→ types (型定義)

services層
└─→ lib/logger.ts
```

### バックエンドアーキテクチャ

```
main.py (エントリーポイント)
  ├─→ routes/*.py
  │     └─→ controllers/*_controller.py
  │           ├─→ validators/*_validators.py
  │           │     └─→ models/*.py
  │           └─→ services/*_service.py
  │                 ├─→ repositories/*_repository.py
  │                 │     └─→ database/tables.py
  │                 │           └─→ database/config.py
  │                 ├─→ models/*.py
  │                 └─→ lib/logger.py
  └─→ database/config.py

レイヤー構成:
[6] main.py
[5] routes
[4] controllers
[3] services
[2] repositories
[1] database
[0] models, validators, lib
```

---

## ✅ 7. 総合評価

### 良好な点

1. **循環依存なし** ✅
   - DAG構造を維持
   - テストしやすく、保守しやすい

2. **レイヤー違反がほぼない** ✅
   - 検出された違反は1件のみ
   - 全体的に適切な依存方向

3. **コンポーネント/フックの独立性** ✅
   - フロントエンドの各モジュールが独立
   - 再利用性が高い

4. **共通ユーティリティの適切な配置** ✅
   - logger.pyが最も参照される（適切）
   - 型定義が適切に集約されている

5. **エントリーポイントが明確** ✅
   - main.py/main.tsxが依存のルート
   - アプリケーション構造が理解しやすい

### 改善推奨事項

1. **🔧 レイヤー違反の修正（優先度: 高）**
   - `test_data_provider.py`をlib層に移動
   - または依存性注入パターンを適用

2. **📝 ドキュメント化（優先度: 中）**
   - 各レイヤーの責務を明文化
   - importルールをREADMEに記載

3. **🔍 継続的な監視（優先度: 中）**
   - CI/CDに依存関係チェックを組み込む
   - 定期的に依存グラフを検証

---

## 🎯 8. 推奨アクション

### 即座に対応すべき項目

**1. test_data_provider.pyの移動**

```bash
# 移動
mv backend/src/services/test_data_provider.py backend/src/lib/test_data_provider.py

# import文を更新
# backend/src/repositories/charts_repository.py
- from ..services.test_data_provider import test_data_provider
+ from ..lib.test_data_provider import test_data_provider

# backend/src/services/charts_service.py
- from .test_data_provider import test_data_provider
+ from ..lib.test_data_provider import test_data_provider
```

**2. アーキテクチャ図の作成**

- このレポートをベースにアーキテクチャ図を作成
- `docs/ARCHITECTURE.md`として保存

**3. CI/CDへの統合**

```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python3 dependency_graph.py
      - run: |
          if grep -q "⚠️" dependency_report.md; then
            echo "Dependency violations detected!"
            exit 1
          fi
```

---

## 📌 結論

**Stock Harvest AIプロジェクトの依存関係アーキテクチャは、全体的に非常に健全な状態です。**

- ✅ 循環依存なし
- ✅ レイヤー違反は1件のみ（修正容易）
- ✅ 適切な責任分離
- ✅ 高い保守性

**この依存関係の整理状態を維持することで、プロジェクトの長期的な品質を保証できます。**

---

**生成スクリプト**: `dependency_graph.py`, `detailed_analysis.py`
**確認日**: 2026-01-21
