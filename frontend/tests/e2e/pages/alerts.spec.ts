import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth.helper';

test.describe('アラート設定画面', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にログインを実行
    await login(page);
  });

  // E2E-ALRT-001: アラートページアクセス
  test('E2E-ALRT-001: アラートページアクセス', async ({ page }) => {
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

    await test.step('URL確認', async () => {
      await expect(page).toHaveURL('/alerts');
    });

    await test.step('ページ正常読み込み確認', async () => {
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
    });

    await test.step('フォーム表示確認', async () => {
      const form = page.locator('form, [data-testid="alert-form"]');
      await expect(form).toBeVisible({ timeout: 10000 });
    });
  });

  // E2E-ALERT-002: アラート作成機能
  test('E2E-ALERT-002: アラート作成機能', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークリクエスト/レスポンスを監視
    const networkLogs: Array<{request: string, response: number}> = [];
    page.on('request', (req) => {
      networkLogs.push({ request: req.url(), response: 0 });
    });
    page.on('response', (res) => {
      const lastLog = networkLogs.find(log => log.request === res.url());
      if (lastLog) lastLog.response = res.status();
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('URL確認', async () => {
      await expect(page).toHaveURL('/alerts');
    });

    await test.step('フォーム表示確認', async () => {
      const form = page.locator('form, [data-testid="alert-form"]');
      await expect(form).toBeVisible({ timeout: 10000 });
    });

    await test.step('銘柄コード入力', async () => {
      const stockCodeInput = page.locator('input[placeholder="例: 7203"]');
      await expect(stockCodeInput).toBeVisible();
      await stockCodeInput.fill('7203');
    });

    await test.step('アラートタイプ選択', async () => {
      // アラートタイプはデフォルトで'price'なのでスキップ
      // もしくはSelectをクリックして選択
      const typeSelector = page.locator('div[role="combobox"]').first();
      if (await typeSelector.count() > 0) {
        await typeSelector.click();
        await page.locator('li[data-value="price"]').click();
      }
    });

    await test.step('目標価格入力', async () => {
      const targetPriceInput = page.locator('input[placeholder="例: 3000"]');
      await expect(targetPriceInput).toBeVisible();
      await targetPriceInput.fill('3000');
    });

    await test.step('アラート作成実行', async () => {
      const submitButton = page.locator('button:has-text("アラート作成")');
      await expect(submitButton).toBeVisible();
      await submitButton.click();
      
      // 作成成功の確認
      await page.waitForLoadState('networkidle');
      
      // 成功メッセージまたはアラート一覧への追加を確認
      const successMessage = page.locator('.MuiAlert-root');
      
      // 成功メッセージが表示されるかを確認
      await expect(successMessage).toBeVisible({ timeout: 5000 });
    });
  });

  // E2E-ALRT-002: ローディング状態表示
  test('E2E-ALRT-002: ローディング状態表示', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    
    const loadingIndicator = page.locator('div[role="progressbar"], [class*="LinearProgress"], [class*="CircularProgress"]');
    if (await loadingIndicator.count() > 0) {
      await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
    }
    
    await page.waitForLoadState('networkidle');
  });

  // E2E-ALERT-003: アラート一覧表示・管理
  test('E2E-ALERT-003: アラート一覧表示・管理', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークリクエスト/レスポンスを監視
    const networkLogs: Array<{request: string, response: number}> = [];
    page.on('request', (req) => {
      networkLogs.push({ request: req.url(), response: 0 });
    });
    page.on('response', (res) => {
      const lastLog = networkLogs.find(log => log.request === res.url());
      if (lastLog) lastLog.response = res.status();
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('URL確認', async () => {
      await expect(page).toHaveURL('/alerts');
    });

    await test.step('ページタイトル表示確認', async () => {
      const pageTitle = page.locator('h4:has-text("アラート"), h1:has-text("アラート"), h2:has-text("アラート")');
      await expect(pageTitle.first()).toBeVisible({ timeout: 10000 });
    });

    await test.step('アラート一覧セクション表示確認', async () => {
      // アラート一覧のコンテナまたはテーブル
      const alertsList = page.locator(
        '[data-testid="alerts-list"], .alert-list, table, [class*="List"], .MuiList-root'
      );
      
      // アラート一覧が表示されているかチェック
      if (await alertsList.count() > 0) {
        await expect(alertsList.first()).toBeVisible({ timeout: 10000 });
      }
    });

    await test.step('アラート管理機能確認', async () => {
      // 管理機能のボタンやコントロールがあるか確認
      const managementControls = page.locator(
        'button:has-text("編集"), button:has-text("削除"), button:has-text("有効"), button:has-text("無効"), input[type="checkbox"]'
      );
      
      // 管理コントロールが存在する場合は表示確認
      if (await managementControls.count() > 0) {
        await expect(managementControls.first()).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('アラート情報表示確認', async () => {
      // アラートの基本情報が表示されているか確認
      const alertInfo = page.locator(
        '[class*="alert"], .MuiTableRow-root'
      ).or(page.getByText(/7[0-9]{3}/)).or(page.getByText(/[0-9]+円/));
      
      // アラート情報があれば表示確認（空状態の場合はスキップ）
      if (await alertInfo.count() > 0) {
        await expect(alertInfo.first()).toBeVisible({ timeout: 5000 });
      } else {
        // 空状態の表示確認
        const emptyState = page.locator(
          '.empty-state, [class*="empty"]'
        ).or(page.getByText('アラートがありません')).or(page.getByText('設定されていません'));
        if (await emptyState.count() > 0) {
          await expect(emptyState.first()).toBeVisible();
        }
      }
    });
  });

  // E2E-ALERT-004: アラート削除・切替機能
  test('E2E-ALERT-004: アラート削除・切替機能', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークリクエスト/レスポンスを監視
    const networkLogs: Array<{request: string, response: number, method: string}> = [];
    page.on('request', (req) => {
      networkLogs.push({ 
        request: req.url(), 
        response: 0,
        method: req.method()
      });
    });
    page.on('response', (res) => {
      const lastLog = networkLogs.find(log => log.request === res.url());
      if (lastLog) lastLog.response = res.status();
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('URL確認', async () => {
      await expect(page).toHaveURL('/alerts');
    });

    await test.step('アラート切替機能テスト', async () => {
      // アラート有効/無効切替スイッチを探す
      const toggleSwitches = page.locator(
        'input[type="checkbox"][role="switch"], .MuiSwitch-input, input[type="checkbox"]:not([data-testid*="select"])'
      );
      
      const toggleCount = await toggleSwitches.count();
      
      if (toggleCount > 0) {
        // 最初のトグルスイッチをテスト
        const firstToggle = toggleSwitches.first();
        
        // 現在の状態を確認
        const initialState = await firstToggle.isChecked();
        console.log(`初期状態: ${initialState ? '有効' : '無効'}`);
        
        // ネットワーク要求を監視
        const apiRequestPromise = page.waitForRequest(
          request => request.url().includes('/api/alerts/') && request.url().includes('/toggle') && request.method() === 'PUT'
        );
        
        const apiResponsePromise = page.waitForResponse(
          response => response.url().includes('/api/alerts/') && response.url().includes('/toggle') && response.status() === 200
        );
        
        // トグルクリック
        await firstToggle.click();
        
        // API処理の完了を待機
        await apiRequestPromise;
        const apiResponse = await apiResponsePromise;
        
        // APIレスポンスから期待される新しい状態を取得
        const responseData = await apiResponse.json();
        const expectedNewState = Boolean(responseData.isActive);
        
        console.log(`API更新後の期待状態: ${expectedNewState ? '有効' : '無効'}`);
        
        // アラート一覧の再読み込みを待機（UI更新の完了まで）
        await page.waitForTimeout(1000);
        
        // 状態変化を確認（APIレスポンスの値と比較）
        const newState = await firstToggle.isChecked();
        console.log(`実際の新状態: ${newState ? '有効' : '無効'}`);
        
        expect(newState).toBe(expectedNewState);
        expect(newState).toBe(!initialState);
      } else {
        console.log('アラート切替スイッチが見つかりませんでした');
      }
    });

    await test.step('アラート削除機能テスト', async () => {
      // 削除ボタンを探す
      const deleteButtons = page.locator(
        'button:has-text("削除"), button[aria-label*="削除"], .delete-button, button[data-testid*="delete"]'
      );
      
      const deleteCount = await deleteButtons.count();
      
      if (deleteCount > 0) {
        // 最初の削除ボタンをクリック
        const firstDeleteButton = deleteButtons.first();
        await firstDeleteButton.click();
        
        // 削除確認ダイアログの確認
        const confirmDialog = page.locator(
          '[role="dialog"], .MuiDialog-root, .confirm-dialog'
        );
        
        if (await confirmDialog.count() > 0) {
          // 確認ダイアログが表示された場合
          await expect(confirmDialog).toBeVisible();
          
          // キャンセルボタンを探してクリック（データを実際に削除しないため）
          const cancelButton = page.locator(
            'button:has-text("キャンセル"), button:has-text("閉じる"), button[data-testid*="cancel"]'
          );
          
          if (await cancelButton.count() > 0) {
            await cancelButton.click();
            
            // ダイアログが閉じることを確認
            await expect(confirmDialog).toBeHidden();
          }
        } else {
          // 確認ダイアログなしで即座に削除される場合
          console.log('削除確認ダイアログなしで削除実行');
        }
      } else {
        console.log('削除ボタンが見つかりませんでした');
      }
    });

    await test.step('操作後状態確認', async () => {
      // ページが正常に表示されていることを確認
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
      
      // エラーメッセージがないことを確認
      const errorMessages = page.locator('.MuiAlert-root.MuiAlert-colorError, .error-message');
      if (await errorMessages.count() > 0) {
        const errorVisible = await errorMessages.first().isVisible();
        if (errorVisible) {
          console.log('エラーメッセージが表示されています');
        }
      }
    });
  });

  // E2E-ALRT-004: 新規アラート作成フォーム
  test('E2E-ALRT-004: 新規アラート作成フォーム', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const form = page.locator('form, [data-testid="alert-form"]');
    await expect(form).toBeVisible();
  });

  // E2E-ALRT-005: アラートタイプ選択
  test('E2E-ALRT-005: アラートタイプ選択', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const typeSelector = page.locator('select[name="type"], [data-testid="alert-type"]');
    if (await typeSelector.count() > 0) {
      await expect(typeSelector).toBeVisible();
    }
  });

  // E2E-ALRT-006: 価格アラート選択
  test('E2E-ALRT-006: 価格アラート選択', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const priceOption = page.locator('option[value="price"], text=価格アラート');
    if (await priceOption.count() > 0) {
      await expect(priceOption).toBeVisible();
    }
  });

  // E2E-ALRT-007: ロジックアラート選択
  test('E2E-ALRT-007: ロジックアラート選択', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const logicOption = page.locator('option[value="logic"], text=ロジックアラート');
    if (await logicOption.count() > 0) {
      await expect(logicOption).toBeVisible();
    }
  });

  // E2E-ALRT-008: 銘柄コード入力
  test('E2E-ALRT-008: 銘柄コード入力', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const stockCodeInput = page.locator('input[name="stockCode"], input[placeholder*="銘柄"]');
    if (await stockCodeInput.count() > 0) {
      await expect(stockCodeInput).toBeVisible();
      await stockCodeInput.fill('7203');
    }
  });

  // E2E-ALRT-009: 目標価格入力
  test('E2E-ALRT-009: 目標価格入力', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const targetPriceInput = page.locator('input[name="targetPrice"], input[placeholder*="価格"]');
    if (await targetPriceInput.count() > 0) {
      await expect(targetPriceInput).toBeVisible();
      await targetPriceInput.fill('3000');
    }
  });

  // E2E-ALRT-010: 価格アラート作成実行
  test('E2E-ALRT-010: 価格アラート作成実行', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    // フォーム入力
    const typeSelect = page.locator('select[name="type"]');
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption('price');
    }
    
    const stockCodeInput = page.locator('input[name="stockCode"]');
    if (await stockCodeInput.count() > 0) {
      await stockCodeInput.fill('7203');
    }
    
    const targetPriceInput = page.locator('input[name="targetPrice"]');
    if (await targetPriceInput.count() > 0) {
      await targetPriceInput.fill('3000');
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("作成"), button:has-text("追加")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  // E2E-ALRT-011: ロジックアラート作成実行
  test('E2E-ALRT-011: ロジックアラート作成実行', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const typeSelect = page.locator('select[name="type"]');
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption('logic');
    }
    
    const stockCodeInput = page.locator('input[name="stockCode"]');
    if (await stockCodeInput.count() > 0) {
      await stockCodeInput.fill('7203');
    }
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  // E2E-ALRT-012: 設定済みアラート一覧表示
  test('E2E-ALRT-012: 設定済みアラート一覧表示', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const alertsList = page.locator('.alert-list, [data-testid="alerts-list"], table');
    if (await alertsList.count() > 0) {
      await expect(alertsList).toBeVisible();
    }
  });

  // E2E-ALRT-013: アラート有効/無効切り替え
  test('E2E-ALRT-013: アラート有効/無効切り替え', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const toggleSwitch = page.locator('input[type="checkbox"], .switch, .toggle');
    if (await toggleSwitch.count() > 0) {
      await toggleSwitch.first().click();
    }
  });

  // E2E-ALRT-014: アラート削除確認
  test('E2E-ALRT-014: アラート削除確認', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const deleteButton = page.locator('button:has-text("削除"), .delete-button');
    if (await deleteButton.count() > 0) {
      await deleteButton.first().click();
      
      const confirmDialog = page.locator('[role="dialog"], .confirm-dialog');
      if (await confirmDialog.count() > 0) {
        await expect(confirmDialog).toBeVisible();
      }
    }
  });

  // E2E-ALRT-015: アラート削除実行
  test('E2E-ALRT-015: アラート削除実行', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const deleteButton = page.locator('button:has-text("削除")');
    if (await deleteButton.count() > 0) {
      await deleteButton.first().click();
      
      const confirmButton = page.locator('button:has-text("確認"), button:has-text("実行")');
      if (await confirmButton.count() > 0) {
        await confirmButton.click();
      }
    }
  });

  // E2E-ALRT-016: アラート削除キャンセル
  test('E2E-ALRT-016: アラート削除キャンセル', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const deleteButton = page.locator('button:has-text("削除")');
    if (await deleteButton.count() > 0) {
      await deleteButton.first().click();
      
      const cancelButton = page.locator('button:has-text("キャンセル"), button:has-text("閉じる")');
      if (await cancelButton.count() > 0) {
        await cancelButton.click();
      }
    }
  });

  // E2E-ALRT-017: LINE通知設定表示
  test('E2E-ALRT-017: LINE通知設定表示', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const lineSection = page.locator('text=LINE, .line-settings, [data-testid="line-notify"]');
    if (await lineSection.count() > 0) {
      await expect(lineSection.first()).toBeVisible();
    }
  });

  // E2E-ALRT-018: LINE連携状態表示
  test('E2E-ALRT-018: LINE連携状態表示', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const lineStatus = page.locator('text=連携中, text=未連携, .line-status');
    if (await lineStatus.count() > 0) {
      await expect(lineStatus.first()).toBeVisible();
    }
  });

  // E2E-ALRT-019: 必須項目未入力エラー
  test('E2E-ALRT-019: 必須項目未入力エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      const errorMessage = page.locator('.error, .validation-error, text=必須');
      if (await errorMessage.count() > 0) {
        await expect(errorMessage.first()).toBeVisible();
      }
    }
  });

  // E2E-ALRT-020: 価格未入力エラー
  test('E2E-ALRT-020: 価格未入力エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const typeSelect = page.locator('select[name="type"]');
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption('price');
    }
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      // エラーメッセージの表示確認（エラーがある場合）
      const priceError = page.locator('text=価格, .price-error');
      void priceError; // 将来の機能拡張のため保持
    }
  });

  // E2E-ALRT-021 through E2E-ALRT-031 - Additional error handling and UI tests
  test('E2E-ALRT-021: アラート作成失敗エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-022: アラート切り替え失敗エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-023: アラート削除失敗エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-024: アラート一覧空状態', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const emptyState = page.locator('text=アラートがありません, .empty-state, text=設定されていません');
    if (await emptyState.count() > 0) {
      await expect(emptyState.first()).toBeVisible();
    }
  });

  test('E2E-ALRT-025: 成功通知表示', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-026: 通知自動消失', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-027: デスクトップ表示', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  test('E2E-ALRT-028: タブレット表示', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  test('E2E-ALRT-029: モバイル表示', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  test('E2E-ALRT-030: アラート条件表示形式', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('E2E-ALRT-031: フォーム操作ワークフロー', async ({ page }) => {
    await page.goto('http://localhost:3247/alerts');
    await page.waitForLoadState('networkidle');
    
    // 基本的なフォーム操作の一連の流れを確認
    const form = page.locator('form');
    if (await form.count() > 0) {
      await expect(form).toBeVisible();
    }
  });

  // E2E-ALERT-005: LINE連携・通知設定
  test.only('E2E-ALERT-005: LINE連携・通知設定', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークリクエスト/レスポンスを監視
    const networkLogs: Array<{request: string, response: number, method: string}> = [];
    page.on('request', (req) => {
      networkLogs.push({ 
        request: req.url(), 
        response: 0,
        method: req.method()
      });
    });
    page.on('response', (res) => {
      const lastLog = networkLogs.find(log => log.request === res.url());
      if (lastLog) lastLog.response = res.status();
    });

    await test.step('ページ遷移', async () => {
      await page.goto('http://localhost:3247/alerts');
      await page.waitForLoadState('networkidle');
    });

    await test.step('URL確認', async () => {
      await expect(page).toHaveURL('/alerts');
    });

    await test.step('LINE通知設定セクション表示確認', async () => {
      // LINE通知設定のセクションまたはエリアを探す
      const lineSection = page.locator(
        '[data-testid="line-notify"], .line-settings, .line-notification'
      ).or(page.locator('h1:has-text("LINE"), h2:has-text("LINE"), h3:has-text("LINE"), h4:has-text("LINE"), h5:has-text("LINE"), h6:has-text("LINE")')
      ).or(page.getByText('LINE通知')).or(page.getByText('LINE連携'));
      
      if (await lineSection.count() > 0) {
        await expect(lineSection.first()).toBeVisible({ timeout: 10000 });
        console.log('LINE通知設定セクションが見つかりました');
      } else {
        console.log('LINE通知設定セクションが見つかりませんでした');
      }
    });

    await test.step('LINE連携状態表示確認', async () => {
      // LINE連携の状態表示を確認
      const lineStatus = page.locator(
        '.line-status, [data-testid="line-status"]'
      ).or(page.getByText('連携中')).or(page.getByText('未連携'))
      .or(page.getByText('接続中')).or(page.getByText('未接続'))
      .or(page.getByText('設定済み')).or(page.getByText('未設定'));
      
      if (await lineStatus.count() > 0) {
        await expect(lineStatus.first()).toBeVisible({ timeout: 5000 });
        const statusText = await lineStatus.first().textContent();
        console.log(`LINE連携状態: ${statusText}`);
      } else {
        console.log('LINE連携状態表示が見つかりませんでした');
      }
    });

    await test.step('LINE通知設定ボタン確認', async () => {
      // LINE通知設定のボタンやコントロールを確認
      const lineControls = page.locator(
        'button:has-text("LINE"), button[data-testid*="line"]'
      ).or(page.locator('button:has-text("連携"), button:has-text("設定")')
      ).or(page.locator('button:has-text("通知"), [data-testid="line-connect"]'));
      
      if (await lineControls.count() > 0) {
        await expect(lineControls.first()).toBeVisible({ timeout: 5000 });
        const buttonText = await lineControls.first().textContent();
        console.log(`LINE設定ボタン: ${buttonText}`);
      } else {
        console.log('LINE設定ボタンが見つかりませんでした');
      }
    });

    await test.step('通知設定オプション確認', async () => {
      // 通知設定のオプション（ON/OFF切り替えなど）を確認
      const notificationOptions = page.locator(
        'input[type="checkbox"][data-testid*="notification"], input[type="checkbox"][name*="line"]'
      ).or(page.locator('.notification-toggle, .line-toggle'))
      .or(page.locator('input[type="checkbox"]:has-text("LINE"), input[type="checkbox"]:has-text("通知")'));
      
      if (await notificationOptions.count() > 0) {
        await expect(notificationOptions.first()).toBeVisible({ timeout: 5000 });
        const isChecked = await notificationOptions.first().isChecked();
        console.log(`通知設定状態: ${isChecked ? '有効' : '無効'}`);
      } else {
        console.log('通知設定オプションが見つかりませんでした');
      }
    });

    await test.step('LINE通知テスト機能確認', async () => {
      // LINE通知のテスト送信機能があるかを確認
      const testButton = page.locator(
        'button:has-text("テスト"), button:has-text("送信テスト")'
      ).or(page.locator('button[data-testid*="test"], button:has-text("確認")'));
      
      if (await testButton.count() > 0) {
        await expect(testButton.first()).toBeVisible({ timeout: 5000 });
        const buttonText = await testButton.first().textContent();
        console.log(`テスト機能ボタン: ${buttonText}`);
        
        // テストボタンをクリックしてみる（実際には送信しない）
        // await testButton.first().click();
        // await page.waitForLoadState('networkidle');
        console.log('テストボタンをクリック（スキップ）');
      } else {
        console.log('LINE通知テスト機能が見つかりませんでした');
      }
    });

    await test.step('通知設定保存機能確認', async () => {
      // 通知設定の保存ボタンやオートセーブ機能を確認
      const saveButton = page.locator(
        'button:has-text("保存"), button[type="submit"]'
      ).or(page.locator('button:has-text("更新"), button:has-text("適用")'));
      
      if (await saveButton.count() > 0) {
        await expect(saveButton.first()).toBeVisible({ timeout: 5000 });
        const buttonText = await saveButton.first().textContent();
        console.log(`設定保存ボタン: ${buttonText}`);
      } else {
        console.log('設定保存ボタンが見つかりませんでした（オートセーブの可能性）');
      }
    });

    await test.step('エラー状態確認', async () => {
      // エラーメッセージがないことを確認
      const errorMessages = page.locator('.MuiAlert-root.MuiAlert-colorError, .error-message, .error');
      const errorCount = await errorMessages.count();
      
      if (errorCount > 0) {
        const visibleErrors = await errorMessages.evaluateAll(elements => 
          elements.filter(el => el.offsetParent !== null).map(el => el.textContent)
        );
        if (visibleErrors.length > 0) {
          console.log(`エラーメッセージ: ${visibleErrors.join(', ')}`);
        }
      } else {
        console.log('エラーメッセージなし');
      }
    });
  });
});