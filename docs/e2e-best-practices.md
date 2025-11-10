# E2Eテストベストプラクティス - Stock Harvest AI

**プロジェクト名**: Stock Harvest AI  
**作成日時**: 2025-11-10 21:24  
**目的**: 成功したE2Eテスト手法とノウハウを蓄積し、後続テストの効率化を図る

---

## 📋 基本方針

### 実行環境
- **テストランナー**: Playwright
- **ブラウザ**: Chrome (headless mode)
- **ベースURL**: http://localhost:3247
- **タイムアウト**: 60秒
- **リトライ**: 本番環境2回、開発環境0回

### テスト実行ルール
1. **1個ずつ順次実行**: test.only() 使用で確実性重視
2. **依存関係遵守**: 前提テストが成功してから実行
3. **モック絶対禁止**: 実APIのみ使用
4. **失敗時即停止**: 根本原因解決まで次に進まない

---

## 🔧 サーバー起動・アクセス

### フロントエンドサーバー
```bash
cd /Users/rieut/STOCK\ HARVEST/frontend
npm run dev
# ポート3247で起動確認
```

### バックエンドサーバー
```bash
cd /Users/rieut/STOCK\ HARVEST/backend
python3 main.py
# ポート8432で起動確認
```

### サーバー起動確認
```typescript
// ページアクセス前に必ず確認
await page.goto('http://localhost:3247');
await expect(page).toHaveTitle('Stock Harvest AI');
```

---

## 📡 API接続確認

### システム基本確認
```typescript
// バックエンドAPI生存確認
const healthResponse = await page.request.get('http://localhost:8432/api/system/status');
expect(healthResponse.status()).toBe(200);

// システム情報取得確認  
const systemResponse = await page.request.get('http://localhost:8432/api/system/info');
expect(systemResponse.status()).toBe(200);
```

### データベース接続確認
```typescript
// PostgreSQL接続状態確認
const healthData = await healthResponse.json();
expect(healthData.checks.database.status).toBe('pass');
```

---

## 🎯 ページアクセスパターン

### ダッシュボードページ (/)
```typescript
await page.goto('http://localhost:3247/');
await page.waitForLoadState('networkidle');

// 基本要素確認
await expect(page.locator('h4')).toContainText('ロジックスキャナーダッシュボード');
await expect(page.locator('button:has-text("今すぐスキャン")')).toBeVisible();
```

### アラートページ (/alerts)
```typescript
await page.goto('http://localhost:3247/alerts');
await page.waitForLoadState('networkidle');

// 基本要素確認
await expect(page.locator('h4')).toContainText('アラート設定');
await expect(page.locator('form')).toBeVisible();
```

### サポートページ (/contact)
```typescript
await page.goto('http://localhost:3247/contact');
await page.waitForLoadState('networkidle');

// 基本要素確認
await expect(page.locator('h4')).toContainText('よくある質問');
await expect(page.locator('form')).toBeVisible();
```

---

## 💡 成功パターン集

### ローディング状態検証
```typescript
// MUIの LinearProgress を確認
const loadingIndicator = page.locator('div[role="progressbar"]');
await expect(loadingIndicator).toBeVisible();
await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
```

### スキャン機能テスト
```typescript
// スキャンボタンクリック
await page.click('button:has-text("全銘柄スキャン実行")');

// プログレス表示確認
await expect(page.locator('text=スキャン中')).toBeVisible();
await expect(page.locator('text=スキャン完了')).toBeVisible({ timeout: 30000 });
```

### フォーム操作
```typescript
// アラート作成フォーム
await page.selectOption('select[name="type"]', 'price');
await page.fill('input[name="stockCode"]', '7203');
await page.fill('input[name="targetPrice"]', '3000');
await page.click('button[type="submit"]');

// 成功メッセージ確認
await expect(page.locator('text=アラートを作成しました')).toBeVisible();
```

---

## ⚠️ 既知の問題と対策

### ネットワーク遅延
```typescript
// タイムアウト設定を長めに
await page.waitForResponse(
  response => response.url().includes('/api/scan/execute'),
  { timeout: 45000 }
);
```

### 非同期処理待機
```typescript
// データ更新完了まで確実に待機
await page.waitForFunction(
  () => document.querySelector('[data-testid="scan-results"]')?.children.length > 0,
  { timeout: 20000 }
);
```

### MUIコンポーネント
```typescript
// Accordion展開
await page.click('div[data-testid="faq-item"] button');
await expect(page.locator('div[data-testid="faq-content"]')).toBeVisible();

// Select操作
await page.click('div[role="button"]'); // Select開く
await page.click('li[data-value="price"]'); // オプション選択
```

---

## 📊 レスポンシブテスト

### ビューポート設定
```typescript
// デスクトップ
await page.setViewportSize({ width: 1920, height: 1080 });

// タブレット
await page.setViewportSize({ width: 768, height: 1024 });

// モバイル
await page.setViewportSize({ width: 375, height: 667 });
```

### レスポンシブ確認項目
- Grid2の size プロパティ動作
- メニューの折りたたみ
- ボタンサイズ調整
- テキスト折り返し

---

## 🔍 デバッグ手法

### スクリーンショット撮影
```typescript
await page.screenshot({
  path: `debug-${Date.now()}.png`,
  fullPage: true
});
```

### コンソールログ確認
```typescript
page.on('console', msg => console.log('PAGE LOG:', msg.text()));
page.on('pageerror', err => console.log('PAGE ERROR:', err));
```

### ネットワーク監視
```typescript
page.on('response', response => {
  if (response.status() >= 400) {
    console.log('ERROR RESPONSE:', response.url(), response.status());
  }
});
```

---

## 🏆 品質基準

### 必須チェック項目
1. **機能動作**: 期待動作が正常に実行される
2. **エラー処理**: 適切なエラーメッセージ表示
3. **レスポンシブ**: 3種類のビューポートで動作
4. **パフォーマンス**: 10秒以内でページ表示
5. **API統合**: 実データでの動作確認

### 成功基準
- テスト実行時間: 1テスト平均3分以内
- 成功率: 95%以上
- 再現性: 5回連続実行で安定

---

**最終更新**: 2025-11-10 21:24  
**更新者**: E2Eテストオーケストレーター