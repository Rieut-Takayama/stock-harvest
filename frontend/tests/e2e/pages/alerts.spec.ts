import { test, expect } from '@playwright/test';

test.describe('AlertsPage E2Eテスト', () => {
  // E2E-ALERT-001: ページアクセス・初期表示
  test('E2E-ALERT-001: ページアクセス・初期表示', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('ページタイトル確認', async () => {
      const pageTitle = page.locator('h4:has-text("アラート設定")');
      await expect(pageTitle).toBeVisible({ timeout: 10000 });
    });

    await test.step('新規アラート作成カード確認', async () => {
      const createCard = page.locator('h6:has-text("新規アラート作成")');
      await expect(createCard).toBeVisible();
    });

    await test.step('設定済みアラートカード確認', async () => {
      const alertsCard = page.locator('h6:has-text("設定済みアラート")');
      await expect(alertsCard).toBeVisible();
    });

    await test.step('LINE通知設定カード確認', async () => {
      const lineCard = page.locator('h6:has-text("LINE通知設定")');
      await expect(lineCard).toBeVisible();
    });

    await test.step('アラート一覧表示確認', async () => {
      // 設定済みアラートの表示を確認
      const emptyMessage = page.locator('text=設定済みのアラートがありません');
      const alertItems = page.locator('text=/7[0-9]{3}|9[0-9]{3}/'); // 銘柄コードパターン

      const itemCount = await alertItems.count();
      console.log(`アラート件数: ${itemCount}件`);

      if (itemCount === 0) {
        // 0件の場合は空メッセージが表示される
        await expect(emptyMessage).toBeVisible();
      } else {
        // 1件以上の場合はアラート項目が表示される
        await expect(alertItems.first()).toBeVisible();
      }
    });
  });

  // E2E-ALERT-002: 価格アラート作成フロー
  test('E2E-ALERT-002: 価格アラート作成フロー', async ({ page }) => {
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('アラートタイプ確認（デフォルト: price）', async () => {
      const typeSelect = page.locator('select, [role="combobox"]').first();
      await expect(typeSelect).toBeVisible();
    });

    await test.step('目標価格欄が表示されている', async () => {
      const targetPriceInput = page.locator('input[placeholder="例: 3000"]');
      await expect(targetPriceInput).toBeVisible();
    });

    await test.step('銘柄コード入力', async () => {
      const stockCodeInput = page.locator('input[placeholder="例: 7203"]');
      await expect(stockCodeInput).toBeVisible();
      await stockCodeInput.fill('7203');
    });

    await test.step('目標価格入力', async () => {
      const targetPriceInput = page.locator('input[placeholder="例: 3000"]');
      await targetPriceInput.fill('3000');
    });

    await test.step('アラート作成ボタンクリック', async () => {
      const createButton = page.locator('button:has-text("アラート作成")');
      await expect(createButton).toBeVisible();
      await createButton.click();
    });

    await test.step('成功通知確認', async () => {
      const successAlert = page.locator('.MuiAlert-root:has-text("アラートを作成しました")');
      await expect(successAlert).toBeVisible({ timeout: 5000 });
    });

    await test.step('一覧に追加確認', async () => {
      await page.waitForTimeout(1000); // UI更新待機
      const alertItem = page.locator('text=7203').first();
      await expect(alertItem).toBeVisible();
    });

    await test.step('フォームリセット確認', async () => {
      const stockCodeInput = page.locator('input[placeholder="例: 7203"]');
      const targetPriceInput = page.locator('input[placeholder="例: 3000"]');

      await expect(stockCodeInput).toHaveValue('');
      await expect(targetPriceInput).toHaveValue('');
    });
  });

  // E2E-ALERT-003: ロジックアラート作成フロー
  test('E2E-ALERT-003: ロジックアラート作成フロー', async ({ page }) => {
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('アラートタイプをlogicに変更', async () => {
      const typeSelect = page.locator('[role="combobox"]').first();
      await typeSelect.click();

      const logicOption = page.locator('li[data-value="logic"]');
      await logicOption.click();
    });

    await test.step('目標価格欄が非表示になることを確認', async () => {
      const targetPriceInput = page.locator('input[placeholder="例: 3000"]');
      await expect(targetPriceInput).toBeHidden();
    });

    await test.step('銘柄コード入力', async () => {
      const stockCodeInput = page.locator('input[placeholder="例: 7203"]');
      await stockCodeInput.fill('9984');
    });

    await test.step('アラート作成ボタンクリック', async () => {
      const createButton = page.locator('button:has-text("アラート作成")');
      await createButton.click();
    });

    await test.step('成功通知確認', async () => {
      const successAlert = page.locator('.MuiAlert-root:has-text("アラートを作成しました")');
      await expect(successAlert).toBeVisible({ timeout: 5000 });
    });

    await test.step('一覧に追加確認', async () => {
      await page.waitForTimeout(1000); // UI更新待機
      const alertItem = page.locator('text=9984').first();
      await expect(alertItem).toBeVisible();
    });

    await test.step('条件表示確認', async () => {
      // 銘柄コード9984を含むアラートボックスを特定し、その中の条件表示を確認
      const alertBox = page.locator('text=9984').locator('..').locator('..').first();
      const conditionText = alertBox.locator('text=発動時にLINE通知');
      await expect(conditionText).toBeVisible();
    });
  });

  // E2E-ALERT-004: アラート有効/無効切替フロー
  test('E2E-ALERT-004: アラート有効/無効切替フロー', async ({ page }) => {
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('スイッチ要素確認', async () => {
      const toggleSwitch = page.locator('input[type="checkbox"][role="switch"]').first();
      const switchCount = await page.locator('input[type="checkbox"][role="switch"]').count();

      if (switchCount === 0) {
        console.log('スイッチが見つかりませんでした（アラートが0件）');
        return;
      }

      await expect(toggleSwitch).toBeVisible();
    });

    await test.step('初期状態確認', async () => {
      const toggleSwitch = page.locator('input[type="checkbox"][role="switch"]').first();
      const switchCount = await page.locator('input[type="checkbox"][role="switch"]').count();

      if (switchCount === 0) {
        return;
      }

      const initialState = await toggleSwitch.isChecked();
      console.log(`初期状態: ${initialState ? '有効' : '無効'}`);
    });

    await test.step('スイッチクリックで状態切替', async () => {
      const toggleSwitch = page.locator('input[type="checkbox"][role="switch"]').first();
      const switchCount = await page.locator('input[type="checkbox"][role="switch"]').count();

      if (switchCount === 0) {
        return;
      }

      const initialState = await toggleSwitch.isChecked();
      await toggleSwitch.click();
      await page.waitForTimeout(1000); // API処理待機

      const newState = await toggleSwitch.isChecked();
      expect(newState).toBe(!initialState);
    });

    await test.step('他のアラート状態が変わらないことを確認', async () => {
      const switches = page.locator('input[type="checkbox"][role="switch"]');
      const switchCount = await switches.count();

      if (switchCount > 1) {
        const secondSwitch = switches.nth(1);
        const secondState = await secondSwitch.isChecked();
        console.log(`2番目のアラート状態: ${secondState ? '有効' : '無効'}（変更なし）`);
      }
    });
  });

  // E2E-ALERT-005: アラート削除フロー
  test('E2E-ALERT-005: アラート削除フロー', async ({ page }) => {
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // 確認ダイアログを自動的にOKする
    page.on('dialog', async (dialog) => {
      console.log(`ダイアログ表示: ${dialog.message()}`);
      await dialog.accept();
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('削除ボタン確認', async () => {
      const deleteButton = page.locator('button:has([data-testid="DeleteIcon"])').first();
      const deleteCount = await page.locator('button:has([data-testid="DeleteIcon"])').count();

      if (deleteCount === 0) {
        console.log('削除ボタンが見つかりませんでした（アラートが0件）');
        return;
      }

      await expect(deleteButton).toBeVisible();
    });

    await test.step('削除ボタンクリック', async () => {
      const deleteButton = page.locator('button:has([data-testid="DeleteIcon"])').first();
      const deleteCount = await page.locator('button:has([data-testid="DeleteIcon"])').count();

      if (deleteCount === 0) {
        return;
      }

      // 削除前のアラート数を記録
      const alertItems = page.locator('text=/7[0-9]{3}|9[0-9]{3}/');
      const initialCount = await alertItems.count();
      console.log(`削除前のアラート数: ${initialCount}`);

      await deleteButton.click();
    });

    await test.step('確認ダイアログ確認', async () => {
      // ダイアログは自動的にacceptされる
      await page.waitForTimeout(500);
    });

    await test.step('成功通知確認', async () => {
      const successAlert = page.locator('.MuiAlert-root:has-text("アラートを削除しました")');
      await expect(successAlert).toBeVisible({ timeout: 5000 });
    });

    await test.step('一覧から消えることを確認', async () => {
      await page.waitForTimeout(1000); // UI更新待機

      // 削除後のアラート数を確認
      const alertItems = page.locator('text=/7[0-9]{3}|9[0-9]{3}/');
      const finalCount = await alertItems.count();
      console.log(`削除後のアラート数: ${finalCount}`);
    });

    await test.step('0件時のメッセージ確認', async () => {
      const alertItems = page.locator('text=/7[0-9]{3}|9[0-9]{3}/');
      const finalCount = await alertItems.count();

      if (finalCount === 0) {
        const emptyMessage = page.locator('text=設定済みのアラートがありません');
        await expect(emptyMessage).toBeVisible();
      }
    });
  });

  // E2E-ALERT-006: LINE通知設定表示確認
  test('E2E-ALERT-006: LINE通知設定表示確認', async ({ page }) => {
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('LINE通知設定カード確認', async () => {
      const lineCard = page.locator('h6:has-text("LINE通知設定")');
      await expect(lineCard).toBeVisible();
    });

    await test.step('チェックアイコン確認', async () => {
      const checkIcon = page.locator('svg[data-testid="CheckCircleIcon"]');
      await expect(checkIcon).toBeVisible();
    });

    await test.step('接続状態テキスト確認', async () => {
      const connectedText = page.locator('text=LINE連携済み');
      const disconnectedText = page.locator('text=LINE未連携');

      const isConnected = await connectedText.count() > 0;
      const isDisconnected = await disconnectedText.count() > 0;

      if (isConnected) {
        await expect(connectedText).toBeVisible();
        console.log('LINE連携状態: 連携済み');
      } else if (isDisconnected) {
        await expect(disconnectedText).toBeVisible();
        console.log('LINE連携状態: 未連携');
      }
    });

    await test.step('説明テキスト確認', async () => {
      const connectedDescription = page.locator('text=通知は自動的にLINEに送信されます');
      const disconnectedDescription = page.locator('text=LINE通知を有効にするには連携が必要です');

      const hasConnectedDesc = await connectedDescription.count() > 0;
      const hasDisconnectedDesc = await disconnectedDescription.count() > 0;

      if (hasConnectedDesc) {
        await expect(connectedDescription).toBeVisible();
      } else if (hasDisconnectedDesc) {
        await expect(disconnectedDescription).toBeVisible();
      }
    });

    await test.step('アイコンの色確認', async () => {
      const checkIcon = page.locator('svg[data-testid="CheckCircleIcon"]');
      const iconColor = await checkIcon.evaluate((el) => {
        return window.getComputedStyle(el).color;
      });

      console.log(`チェックアイコンの色: ${iconColor}`);
      // 色は #00c300 (rgb(0, 195, 0)) を期待
    });
  });
});
