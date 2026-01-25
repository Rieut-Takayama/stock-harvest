import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth.helper';

test.describe('システム設定・管理画面', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にログインを実行
    await login(page);
  });

  // E2E-ADMIN-001: ページアクセス・初期表示確認
  test('E2E-ADMIN-001: ページアクセス・初期表示確認', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('URLが正しく設定されていることを確認', async () => {
      await expect(page).toHaveURL(/\/admin/);
    });

    await test.step('ヘッダー「システム設定・管理」表示確認', async () => {
      // h4タグでヘッダーテキスト確認
      const header = page.locator('h4:has-text("システム設定・管理")');
      await expect(header).toBeVisible();

      // SettingsIcon（SVGアイコン）の存在確認
      const settingsIcon = page.locator('h4 svg[data-testid="SettingsIcon"]');
      await expect(settingsIcon).toBeVisible();
    });

    await test.step('3つのカードセクション表示確認', async () => {
      // 1. バッチ処理ステータスカード
      const batchStatusCard = page.locator('h6:has-text("バッチ処理ステータス")');
      await expect(batchStatusCard).toBeVisible();

      // 2. データソース接続状況カード
      const dataSourceCard = page.locator('h6:has-text("データソース接続状況")');
      await expect(dataSourceCard).toBeVisible();

      // 3. 判定条件の微調整カード
      const parametersCard = page.locator('h6:has-text("判定条件の微調整")');
      await expect(parametersCard).toBeVisible();
    });

    await test.step('バッチ処理ステータスカード内のモックデータ表示確認', async () => {
      // ステータスChip確認
      const statusChip = page.locator('span.MuiChip-label:has-text("正常実行")');
      await expect(statusChip).toBeVisible();

      // 最終実行日時確認（ListItemTextのsecondaryは<p>タグを生成）
      const lastExecution = page.locator('p:has-text("2026-01-11 15:35:00")');
      await expect(lastExecution).toBeVisible();

      // 処理対象銘柄数確認（カンマ区切り）
      const processedStocks = page.locator('p:has-text("3,247銘柄")');
      await expect(processedStocks).toBeVisible();

      // 抽出結果銘柄数確認
      const extractedStocks = page.locator('p:has-text("2銘柄")');
      await expect(extractedStocks).toBeVisible();

      // 実行時間確認
      const duration = page.locator('p:has-text("28.5秒")');
      await expect(duration).toBeVisible();
    });

    await test.step('データソース接続状況カード内のモックデータ表示確認', async () => {
      // Yahoo Finance API
      const yahooFinance = page.locator('p:has-text("Yahoo Finance API")');
      await expect(yahooFinance).toBeVisible();

      // PostgreSQL (Neon)
      const postgresql = page.locator('p:has-text("PostgreSQL (Neon)")');
      await expect(postgresql).toBeVisible();

      // 決算カレンダーDB
      const earningsDB = page.locator('p:has-text("決算カレンダーDB")');
      await expect(earningsDB).toBeVisible();

      // 接続状態Chip確認（3つすべて「接続中」）
      const connectedChips = page.locator('span.MuiChip-label:has-text("接続中")');
      await expect(connectedChips).toHaveCount(3);
    });

    await test.step('判定条件の微調整カード内のモックデータ表示確認', async () => {
      // 警告Alert確認
      const warningAlert = page.locator('div[role="alert"]:has-text("これらのパラメータを変更すると")');
      await expect(warningAlert).toBeVisible();

      // 安値終値比率TextField確認
      const lowToCloseRatioField = page.locator('label:has-text("安値終値比率")');
      await expect(lowToCloseRatioField).toBeVisible();

      // 上場年数上限TextField確認
      const yearsListedField = page.locator('label:has-text("上場年数上限")');
      await expect(yearsListedField).toBeVisible();

      // ストップ高厳密判定Select確認
      const stopHighField = page.locator('label:has-text("ストップ高厳密判定")');
      await expect(stopHighField).toBeVisible();
    });

    await test.step('3つのカードがGridレイアウトで表示されている', async () => {
      // Grid2コンテナの存在確認（MUI v7のGrid2コンポーネント）
      // 複数存在するため、最初の要素（トップレベルのグリッド）を対象
      const gridContainer = page.locator('div.MuiGrid-container').first();
      await expect(gridContainer).toBeVisible();

      // Card要素が3つ存在することを確認
      const cards = page.locator('div.MuiCard-root');
      await expect(cards).toHaveCount(3);
    });
  });

  // E2E-ADMIN-002: バッチ処理ステータス表示確認
  test('E2E-ADMIN-002: バッチ処理ステータス表示確認', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('バッチ処理ステータスカードを確認', async () => {
      const batchStatusCard = page.locator('h6:has-text("バッチ処理ステータス")');
      await expect(batchStatusCard).toBeVisible();
    });

    await test.step('Chip（正常実行/エラー）のステータスを確認', async () => {
      // ステータスChipの確認（緑色「正常実行」アイコン付き）
      const statusChip = page.locator('span.MuiChip-label:has-text("正常実行")');
      await expect(statusChip).toBeVisible();

      // Chipの色が成功色（緑）であることを確認
      const chipElement = page.locator('.MuiChip-colorSuccess').first();
      await expect(chipElement).toBeVisible();
    });

    await test.step('リスト項目を確認: 最終実行日時', async () => {
      // ListItemTextのsecondaryは<p>タグを生成（MUI仕様）
      const lastExecution = page.locator('p:has-text("2026-01-11 15:35:00")');
      await expect(lastExecution).toBeVisible();
    });

    await test.step('リスト項目を確認: 処理対象銘柄数', async () => {
      // カンマ区切りで表示されることを確認
      const processedStocks = page.locator('p:has-text("3,247銘柄")');
      await expect(processedStocks).toBeVisible();
    });

    await test.step('リスト項目を確認: 抽出結果銘柄数', async () => {
      const extractedStocks = page.locator('p:has-text("2銘柄")');
      await expect(extractedStocks).toBeVisible();
    });

    await test.step('リスト項目を確認: 実行時間', async () => {
      const duration = page.locator('p:has-text("28.5秒")');
      await expect(duration).toBeVisible();
    });

    await test.step('すべてのリスト項目が表示されていることを確認', async () => {
      // 4つのリスト項目（最終実行日時、処理対象銘柄数、抽出結果銘柄数、実行時間）
      // バッチ処理ステータスカード内のリストアイテムのみを取得（スコープ限定）
      const batchCard = page.locator('h6:has-text("バッチ処理ステータス")').locator('..');
      const listItems = batchCard.locator('ul.MuiList-root li');
      await expect(listItems).toHaveCount(4);
    });
  });

  // E2E-ADMIN-003: バッチステータス更新ボタン
  test('E2E-ADMIN-003: バッチステータス更新ボタン', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('バッチ処理ステータスカードを確認', async () => {
      const batchStatusCard = page.locator('h6:has-text("バッチ処理ステータス")');
      await expect(batchStatusCard).toBeVisible();
    });

    await test.step('「ステータス更新」ボタンが表示されていることを確認', async () => {
      const updateButton = page.locator('button:has-text("ステータス更新")');
      await expect(updateButton).toBeVisible();

      // Refresh アイコンの存在確認
      const refreshIcon = updateButton.locator('svg[data-testid="RefreshIcon"]');
      await expect(refreshIcon).toBeVisible();
    });

    await test.step('「ステータス更新」ボタンクリックでページリロード', async () => {
      // ページリロードイベントを検知するためにリスナーを設定
      const reloadPromise = page.waitForLoadState('load');

      // ボタンをクリック
      const updateButton = page.locator('button:has-text("ステータス更新")');
      await updateButton.click();

      // ページがリロードされることを確認
      await reloadPromise;

      // リロード後もページが正しく表示されることを確認
      await expect(page).toHaveURL(/\/admin/);
      const header = page.locator('h4:has-text("システム設定・管理")');
      await expect(header).toBeVisible();
    });
  });

  // E2E-ADMIN-004: データソース接続状況表示
  test('E2E-ADMIN-004: データソース接続状況表示', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('データソース接続状況カードを確認', async () => {
      const dataSourceCard = page.locator('h6:has-text("データソース接続状況")');
      await expect(dataSourceCard).toBeVisible();
    });

    await test.step('3つのデータソースが表示される', async () => {
      // Yahoo Finance API
      const yahooFinance = page.locator('p:has-text("Yahoo Finance API")');
      await expect(yahooFinance).toBeVisible();

      // PostgreSQL (Neon)
      const postgresql = page.locator('p:has-text("PostgreSQL (Neon)")');
      await expect(postgresql).toBeVisible();

      // 決算カレンダーDB
      const earningsDB = page.locator('p:has-text("決算カレンダーDB")');
      await expect(earningsDB).toBeVisible();
    });

    await test.step('各データソースの接続状態Chip（緑色「接続中」）を確認', async () => {
      // 「接続中」Chipが3つ存在することを確認
      const connectedChips = page.locator('span.MuiChip-label:has-text("接続中")');
      await expect(connectedChips).toHaveCount(3);

      // 成功色（緑）のChipが存在することを確認
      const successChips = page.locator('.MuiChip-colorSuccess');
      await expect(successChips.first()).toBeVisible();
    });

    await test.step('最終確認日時が表示されることを確認', async () => {
      // 「最終確認:」というテキストが3つ存在することを確認
      const lastCheckTexts = page.locator('span.MuiTypography-caption:has-text("最終確認:")');
      await expect(lastCheckTexts).toHaveCount(3);

      // 各データソースの最終確認日時を確認
      const yahooLastCheck = page.locator('span:has-text("最終確認: 2026-01-11 15:30:00")');
      await expect(yahooLastCheck).toBeVisible();

      const postgresqlLastCheck = page.locator('span:has-text("最終確認: 2026-01-11 15:30:05")');
      await expect(postgresqlLastCheck).toBeVisible();

      const earningsLastCheck = page.locator('span:has-text("最終確認: 2026-01-11 15:30:10")');
      await expect(earningsLastCheck).toBeVisible();
    });
  });

  // E2E-ADMIN-005: 接続テスト実行ボタン
  test('E2E-ADMIN-005: 接続テスト実行ボタン', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('データソース接続状況カードを確認', async () => {
      const dataSourceCard = page.locator('h6:has-text("データソース接続状況")');
      await expect(dataSourceCard).toBeVisible();
    });

    await test.step('「接続テスト実行」ボタンが表示されていることを確認', async () => {
      const testConnectionButton = page.locator('button:has-text("接続テスト実行")');
      await expect(testConnectionButton).toBeVisible();

      // Refresh アイコンの存在確認
      const refreshIcon = testConnectionButton.locator('svg[data-testid="RefreshIcon"]');
      await expect(refreshIcon).toBeVisible();
    });

    await test.step('「接続テスト実行」ボタンクリックでアラート表示', async () => {
      // alertダイアログを検知するハンドラーを設定
      let alertMessage = '';
      page.once('dialog', async (dialog) => {
        expect(dialog.type()).toBe('alert');
        alertMessage = dialog.message();
        await dialog.accept();
      });

      // ボタンをクリック
      const testConnectionButton = page.locator('button:has-text("接続テスト実行")');
      await testConnectionButton.click();

      // アラートメッセージが正しいことを確認
      await page.waitForTimeout(500); // アラート処理完了待機
      expect(alertMessage).toBe('接続テストを実行しました（モック実装）');
    });
  });

  // E2E-ADMIN-006: 判定条件パラメータ入力
  test('E2E-ADMIN-006: 判定条件パラメータ入力', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('判定条件カードを確認', async () => {
      const parametersCard = page.locator('h6:has-text("判定条件の微調整")');
      await expect(parametersCard).toBeVisible();
    });

    await test.step('警告Alertが表示されていることを確認', async () => {
      const warningAlert = page.locator('div[role="alert"]:has-text("これらのパラメータを変更すると")');
      await expect(warningAlert).toBeVisible();
    });

    await test.step('「安値終値比率」TextFieldに値を入力', async () => {
      // TextFieldの入力要素を取得（labelからinputを特定）
      const lowToCloseRatioInput = page.locator('label:has-text("安値終値比率")').locator('..').locator('input');

      // 初期値確認
      await expect(lowToCloseRatioInput).toHaveValue('0.01');

      // 値をクリアして新しい値を入力
      await lowToCloseRatioInput.clear();
      await lowToCloseRatioInput.fill('0.02');

      // 入力が反映されたことを確認
      await expect(lowToCloseRatioInput).toHaveValue('0.02');

      // helperTextが表示されることを確認
      const helperText = page.locator('p:has-text("安値 < 終値 × [この値]")');
      await expect(helperText).toBeVisible();
    });

    await test.step('「上場年数上限」TextFieldに値を入力', async () => {
      // TextFieldの入力要素を取得
      const yearsListedInput = page.locator('label:has-text("上場年数上限")').locator('..').locator('input');

      // 初期値確認
      await expect(yearsListedInput).toHaveValue('5');

      // 値をクリアして新しい値を入力
      await yearsListedInput.clear();
      await yearsListedInput.fill('7');

      // 入力が反映されたことを確認
      await expect(yearsListedInput).toHaveValue('7');

      // helperTextが表示されることを確認
      const helperText = page.locator('p:has-text("上場から[この値]年未満の銘柄")');
      await expect(helperText).toBeVisible();
    });

    await test.step('「ストップ高厳密判定」セレクトを変更', async () => {
      // selectの入力要素を取得
      const stopHighSelect = page.locator('label:has-text("ストップ高厳密判定")').locator('..').locator('select');

      // 初期値確認
      await expect(stopHighSelect).toHaveValue('true');

      // 値を変更
      await stopHighSelect.selectOption('false');

      // 変更が反映されたことを確認
      await expect(stopHighSelect).toHaveValue('false');

      // helperTextが表示されることを確認
      const helperText = page.locator('p:has-text("始値=終値=ストップ高価格")');
      await expect(helperText).toBeVisible();
    });
  });

  // E2E-ADMIN-007: 設定保存フロー
  test('E2E-ADMIN-007: 設定保存フロー', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('判定条件カードを確認', async () => {
      const parametersCard = page.locator('h6:has-text("判定条件の微調整")');
      await expect(parametersCard).toBeVisible();
    });

    await test.step('パラメータを変更（安値終値比率を0.02に変更）', async () => {
      const lowToCloseRatioInput = page.locator('label:has-text("安値終値比率")').locator('..').locator('input');
      await lowToCloseRatioInput.clear();
      await lowToCloseRatioInput.fill('0.02');
      await expect(lowToCloseRatioInput).toHaveValue('0.02');
    });

    await test.step('「設定を保存」ボタンが表示されていることを確認', async () => {
      const saveButton = page.locator('button:has-text("設定を保存")');
      await expect(saveButton).toBeVisible();

      // Save アイコンの存在確認
      const saveIcon = saveButton.locator('svg[data-testid="SaveIcon"]');
      await expect(saveIcon).toBeVisible();
    });

    await test.step('「設定を保存」ボタンクリックでアラート表示', async () => {
      // alertダイアログを検知するハンドラーを設定
      let alertMessage = '';
      page.once('dialog', async (dialog) => {
        expect(dialog.type()).toBe('alert');
        alertMessage = dialog.message();
        await dialog.accept();
      });

      // ボタンをクリック
      const saveButton = page.locator('button:has-text("設定を保存")');
      await saveButton.click();

      // アラートメッセージが正しいことを確認
      await page.waitForTimeout(500); // アラート処理完了待機
      expect(alertMessage).toBe('設定を保存しました（モック実装）');
    });

    await test.step('パラメータ値が変更されたまま維持されていることを確認', async () => {
      const lowToCloseRatioInput = page.locator('label:has-text("安値終値比率")').locator('..').locator('input');
      await expect(lowToCloseRatioInput).toHaveValue('0.02');
    });
  });

  // E2E-ADMIN-008: デフォルト設定リセット
  test('E2E-ADMIN-008: デフォルト設定リセット', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('/admin ページへ移動', async () => {
      await page.goto('http://localhost:3247/admin');
      await page.waitForLoadState('networkidle');
    });

    await test.step('判定条件カードを確認', async () => {
      const parametersCard = page.locator('h6:has-text("判定条件の微調整")');
      await expect(parametersCard).toBeVisible();
    });

    await test.step('パラメータを変更（すべて変更）', async () => {
      // 安値終値比率を0.02に変更
      const lowToCloseRatioInput = page.locator('label:has-text("安値終値比率")').locator('..').locator('input');
      await lowToCloseRatioInput.clear();
      await lowToCloseRatioInput.fill('0.02');
      await expect(lowToCloseRatioInput).toHaveValue('0.02');

      // 上場年数上限を7に変更
      const yearsListedInput = page.locator('label:has-text("上場年数上限")').locator('..').locator('input');
      await yearsListedInput.clear();
      await yearsListedInput.fill('7');
      await expect(yearsListedInput).toHaveValue('7');

      // ストップ高厳密判定をfalseに変更
      const stopHighSelect = page.locator('label:has-text("ストップ高厳密判定")').locator('..').locator('select');
      await stopHighSelect.selectOption('false');
      await expect(stopHighSelect).toHaveValue('false');
    });

    await test.step('「デフォルトに戻す」ボタンが表示されていることを確認', async () => {
      const resetButton = page.locator('button:has-text("デフォルトに戻す")');
      await expect(resetButton).toBeVisible();
    });

    await test.step('「デフォルトに戻す」ボタンをクリック', async () => {
      const resetButton = page.locator('button:has-text("デフォルトに戻す")');
      await resetButton.click();
    });

    await test.step('パラメータが初期値に戻ることを確認', async () => {
      // 安値終値比率: 0.01
      const lowToCloseRatioInput = page.locator('label:has-text("安値終値比率")').locator('..').locator('input');
      await expect(lowToCloseRatioInput).toHaveValue('0.01');

      // 上場年数上限: 5
      const yearsListedInput = page.locator('label:has-text("上場年数上限")').locator('..').locator('input');
      await expect(yearsListedInput).toHaveValue('5');

      // ストップ高厳密判定: true（「有効」）
      const stopHighSelect = page.locator('label:has-text("ストップ高厳密判定")').locator('..').locator('select');
      await expect(stopHighSelect).toHaveValue('true');
    });
  });
});
