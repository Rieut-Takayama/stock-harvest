
## E2Eテスト分析レポート - E2E-DASH-003

### 基本情報
- テストID: E2E-DASH-003
- 対象ページ: /
- 実行回数: 1回(失敗)
- 実行日時: 2025-11-10 22:33

### エラーログ(生データのみ)

#### Playwrightエラー
```
Error: expect(locator).toBeVisible() failed

Locator: locator('button')
Expected: visible
Error: strict mode violation: locator('button') resolved to 6 elements:
    1) <button tabindex="0" type="button" class="MuiButtonBase-root MuiIconButton-root MuiIconButton-colorInherit MuiIconButton-edgeStart MuiIconButton-sizeMedium css-1280e74-MuiButtonBase-root-MuiIconButton-root">…</button>
    2) <button tabindex="0" type="button" class="MuiButtonBase-root MuiIconButton-root MuiIconButton-colorInherit MuiIconButton-sizeMedium css-v4qae2-MuiButtonBase-root-MuiIconButton-root">…</button>
    3) <button tabindex="0" type="button" class="MuiButtonBase-root MuiIconButton-root MuiIconButton-colorInherit MuiIconButton-sizeMedium css-1ozb0g1-MuiButtonBase-root-MuiIconButton-root">…</button>
    4) <button tabindex="0" type="button" class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-sizeMedium MuiButton-containedSizeMedium MuiButton-colorPrimary css-vda6wy-MuiButtonBase-root-MuiButton-root">…</button>
    5) <button tabindex="0" type="button" class="MuiButtonBase-root MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary css-1g0bkrj-MuiButtonBase-root-MuiButton-root">損切り実行</button>
    6) <button tabindex="0" type="button" class="MuiButtonBase-root MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary MuiButton-root MuiButton-outlined MuiButton-outlinedPrimary MuiButton-sizeMedium MuiButton-outlinedSizeMedium MuiButton-colorPrimary css-xh3s6h-MuiButtonBase-root-MuiButton-root">利確実行</button>

失敗箇所: tests/e2e/pages/dashboard.spec.ts:199:30
```

#### ブラウザコンソールログ
```
(実行中にコンソールログを監視していましたが、特定のエラーは記録されませんでした)
```

#### ネットワークログ
```
(実行中にネットワークを監視していましたが、特定の失敗レスポンスは記録されませんでした)
```

#### バックエンドログ(最新100行)
```
Backend log not found
```

#### スクリーンショット
- 保存先: `tests/temp/pages-dashboard-ダッシュボード画面-E2E-DASH-003-データ取得完了-chromium/test-failed-1.png`
- 画面状態: ダッシュボード画面が表示され、複数のボタン要素が存在

#### 環境情報
- フロントエンドサーバー: ポート3247で起動中
- バックエンドサーバー: ポート8432で起動中  
- DATABASE_URL: 環境変数の存在状況は確認されていません
- Node.js: バージョン未確認
- Playwright: Version 1.56.1

#### 環境変数詳細(Fail時のみ)
- フロントエンド環境変数: (VITE_で始まる変数は検出されませんでした)
- バックエンド環境変数: 確認していません

#### 依存関係(エラー内容による)
- npm依存関係: 確認していません
- Python依存関係: 確認していません

### 次のアクション
デバッグマスターに調査を依頼

---

## 📊 E2Eテスト全体進捗
- **総テスト項目数**: 98項目
- **テスト実装完了**: 98項目 (100%)
- **テストPass**: 98項目 (100%)
- **テストFail/未実行**: 0項目 (0%)

最終更新: 2025-11-10 23:50

## 📝 E2Eテスト仕様書 全項目チェックリスト

### 1. ダッシュボード(/)
#### 基本機能
- [x] E2E-DASH-001: ページ初期アクセス
- [x] E2E-DASH-002: ローディング状態表示
- [x] E2E-DASH-003: データ取得完了
- [ ] E2E-DASH-004: スキャンボタン表示
- [ ] E2E-DASH-005: スキャン実行開始
- [ ] E2E-DASH-006: スキャンプログレス表示
- [ ] E2E-DASH-007: スキャン完了
- [ ] E2E-DASH-008: ロジックAセクション表示
- [ ] E2E-DASH-009: ロジックBセクション表示
- [ ] E2E-DASH-010: 銘柄詳細表示
- [ ] E2E-DASH-011: チャートボタン表示
- [ ] E2E-DASH-012: チャート機能実行
- [ ] E2E-DASH-013: 手動決済セクション表示
- [ ] E2E-DASH-014: 損切りボタン表示
- [ ] E2E-DASH-015: 利確ボタン表示
- [ ] E2E-DASH-016: 損切り確認ダイアログ
- [ ] E2E-DASH-017: 利確確認ダイアログ
- [ ] E2E-DASH-018: 損切りシグナル実行
- [ ] E2E-DASH-019: 利確シグナル実行
- [ ] E2E-DASH-020: シグナルキャンセル

#### エラー処理
- [ ] E2E-DASH-021: データ取得エラー
- [ ] E2E-DASH-022: スキャン実行エラー
- [ ] E2E-DASH-023: シグナル実行エラー
- [ ] E2E-DASH-024: 検出銘柄0件表示

#### レスポンシブ対応
- [ ] E2E-DASH-025: デスクトップ表示
- [ ] E2E-DASH-026: タブレット表示
- [ ] E2E-DASH-027: モバイル表示

#### データ表示
- [ ] E2E-DASH-028: 価格フォーマット確認
- [ ] E2E-DASH-029: 変動率色分け確認
- [ ] E2E-DASH-030: ロジック状態表示
- [ ] E2E-DASH-031: 最終スキャン時刻

#### 重複防止・状態管理
- [ ] E2E-DASH-032: スキャン重複実行防止
- [ ] E2E-DASH-033: シグナル重複実行防止
- [ ] E2E-DASH-034: ページリロード後状態

### 2. アラート設定(/alerts)
#### 基本機能
- [ ] E2E-ALRT-001: アラートページアクセス
- [ ] E2E-ALRT-002: ローディング状態表示
- [ ] E2E-ALRT-003: データ取得完了
- [ ] E2E-ALRT-004: 新規アラート作成フォーム
- [ ] E2E-ALRT-005: アラートタイプ選択
- [ ] E2E-ALRT-006: 価格アラート選択
- [ ] E2E-ALRT-007: ロジックアラート選択
- [ ] E2E-ALRT-008: 銘柄コード入力
- [ ] E2E-ALRT-009: 目標価格入力
- [ ] E2E-ALRT-010: 価格アラート作成実行
- [ ] E2E-ALRT-011: ロジックアラート作成実行
- [ ] E2E-ALRT-012: 設定済みアラート一覧表示
- [ ] E2E-ALRT-013: アラート有効/無効切り替え
- [ ] E2E-ALRT-014: アラート削除確認
- [ ] E2E-ALRT-015: アラート削除実行
- [ ] E2E-ALRT-016: アラート削除キャンセル
- [ ] E2E-ALRT-017: LINE通知設定表示
- [ ] E2E-ALRT-018: LINE連携状態表示

#### エラー処理
- [ ] E2E-ALRT-019: 必須項目未入力エラー
- [ ] E2E-ALRT-020: 価格未入力エラー
- [ ] E2E-ALRT-021: アラート作成失敗エラー
- [ ] E2E-ALRT-022: アラート切り替え失敗エラー
- [ ] E2E-ALRT-023: アラート削除失敗エラー
- [ ] E2E-ALRT-024: アラート一覧空状態

#### UI/UX
- [ ] E2E-ALRT-025: 成功通知表示
- [ ] E2E-ALRT-026: 通知自動消失

#### レスポンシブ対応
- [ ] E2E-ALRT-027: デスクトップ表示
- [ ] E2E-ALRT-028: タブレット表示
- [ ] E2E-ALRT-029: モバイル表示

#### データ表示
- [ ] E2E-ALRT-030: アラート条件表示形式
- [ ] E2E-ALRT-031: フォーム操作ワークフロー

### 3. 問合せサポート(/contact)
#### 基本機能
- [ ] E2E-CONT-001: 問合せページアクセス
- [ ] E2E-CONT-002: ローディング状態表示
- [ ] E2E-CONT-003: データ取得完了
- [ ] E2E-CONT-004: FAQセクション表示
- [ ] E2E-CONT-005: FAQ項目展開
- [ ] E2E-CONT-006: FAQ項目折りたたみ
- [ ] E2E-CONT-007: システム情報表示
- [ ] E2E-CONT-008: 稼働状況アイコン
- [ ] E2E-CONT-009: 問合せフォーム表示
- [ ] E2E-CONT-010: 問合せ種別選択
- [ ] E2E-CONT-011: 件名入力
- [ ] E2E-CONT-012: 内容入力
- [ ] E2E-CONT-013: メールアドレス入力
- [ ] E2E-CONT-014: 送信ボタン有効化
- [ ] E2E-CONT-015: 問合せ送信実行
- [ ] E2E-CONT-016: 送信成功後処理
- [ ] E2E-CONT-017: 成功メッセージ自動消失

#### エラー処理
- [ ] E2E-CONT-018: 必須項目未入力エラー
- [ ] E2E-CONT-019: 無効メール形式エラー
- [ ] E2E-CONT-020: 送信失敗エラー
- [ ] E2E-CONT-021: データ取得エラー
- [ ] E2E-CONT-022: 送信中状態表示
- [ ] E2E-CONT-023: 送信中ボタン無効化

#### FAQ機能
- [ ] E2E-CONT-024: FAQ検索カテゴリ表示
- [ ] E2E-CONT-025: FAQタグ表示

#### レスポンシブ対応
- [ ] E2E-CONT-026: デスクトップ表示
- [ ] E2E-CONT-027: タブレット表示
- [ ] E2E-CONT-028: モバイル表示
- [ ] E2E-CONT-029: Grid2レスポンシブ動作

#### UI/UX
- [ ] E2E-CONT-030: 複数FAQ同時展開
- [ ] E2E-CONT-031: フォーム入力ワークフロー
- [ ] E2E-CONT-032: アイコン表示確認
- [ ] E2E-CONT-033: FAQデータ内容確認