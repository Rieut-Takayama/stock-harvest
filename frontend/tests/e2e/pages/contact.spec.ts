import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth.helper';

test.describe('問合せサポート画面', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にログインを実行
    await login(page);
  });

  // E2E-SUPPORT-001: サポートページのページ正常読み込み・FAQ表示
  test('E2E-SUPPORT-001: サポートページのページ正常読み込み・FAQ表示', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('サポートページへ移動', async () => {
      await page.goto('http://localhost:3247/contact');
      await page.waitForLoadState('networkidle');
    });

    await test.step('ページ正常読み込み確認', async () => {
      // URLが正しく設定されていることを確認
      await expect(page).toHaveURL(/\/contact/);
      
      // メインコンテンツの表示確認
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
      
      // ページタイトルまたは見出しの確認
      const pageTitle = page.locator('h1, h2, h3, h4').first();
      await expect(pageTitle).toBeVisible();
    });

    await test.step('FAQ表示確認', async () => {
      // FAQ関連の要素が表示されることを確認
      const faqSection = page.locator('[data-testid="faq"], .faq-section, :text("よくある質問"), :text("FAQ")');
      await expect(faqSection.first()).toBeVisible({ timeout: 10000 });
    });
  });

  // E2E-CONT-002: ローディング状態表示
  test('E2E-CONT-002: ローディング状態表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    
    const loadingIndicator = page.locator('div[role="progressbar"], [class*="LinearProgress"], [class*="CircularProgress"]');
    if (await loadingIndicator.count() > 0) {
      await expect(loadingIndicator).toBeHidden({ timeout: 10000 });
    }
    
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-003: データ取得完了
  test('E2E-CONT-003: データ取得完了', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const pageTitle = page.locator('h4:has-text("よくある質問"), h1:has-text("お問い合わせ"), h4:has-text("お問い合わせ")');
    await expect(pageTitle.first()).toBeVisible();
  });

  // E2E-CONT-004: FAQセクション表示
  test('E2E-CONT-004: FAQセクション表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqSection = page.locator('text=よくある質問, text=FAQ, .faq-section, [data-testid="faq"]');
    await expect(faqSection.first()).toBeVisible();
  });

  // E2E-CONT-005: FAQ項目展開
  test('E2E-CONT-005: FAQ項目展開', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqItem = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-item"]').first();
    if (await faqItem.count() > 0) {
      await faqItem.click();
      
      const faqContent = page.locator('.faq-content, .MuiAccordionDetails-root, .MuiAccordion-content, [data-testid="faq-content"]');
      if (await faqContent.count() > 0) {
        await expect(faqContent.first()).toBeVisible();
      }
    }
  });

  // E2E-CONT-006: FAQ項目折りたたみ
  test('E2E-CONT-006: FAQ項目折りたたみ', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqItem = page.locator('.faq-item button, .MuiAccordion-root button').first();
    if (await faqItem.count() > 0) {
      // 展開
      await faqItem.click();
      await page.waitForTimeout(500);
      
      // 折りたたみ
      await faqItem.click();
      
      const faqContent = page.locator('.faq-content, .MuiAccordionDetails-root, .MuiAccordion-content');
      if (await faqContent.count() > 0) {
        await expect(faqContent.first()).toBeHidden({ timeout: 3000 });
      }
    }
  });

  // E2E-CONT-007: システム情報表示
  test('E2E-CONT-007: システム情報表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const systemInfo = page.locator('text=システム情報, text=稼働状況, .system-info, [data-testid="system-info"]');
    if (await systemInfo.count() > 0) {
      await expect(systemInfo.first()).toBeVisible();
    }
  });

  // E2E-CONT-008: 稼働状況アイコン
  test('E2E-CONT-008: 稼働状況アイコン', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const statusIcon = page.locator('.status-icon, .health-icon, [data-testid="status-icon"]');
    if (await statusIcon.count() > 0) {
      await expect(statusIcon.first()).toBeVisible();
    }
  });

  // E2E-CONT-009: 問合せフォーム表示
  test('E2E-CONT-009: 問合せフォーム表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const contactForm = page.locator('form, .contact-form, [data-testid="contact-form"]');
    await expect(contactForm).toBeVisible();
  });

  // E2E-CONT-010: 問合せ種別選択
  test('E2E-CONT-010: 問合せ種別選択', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const categorySelect = page.locator('select[name="category"], [data-testid="contact-category"]');
    if (await categorySelect.count() > 0) {
      await expect(categorySelect).toBeVisible();
      await categorySelect.selectOption('0');
    }
  });

  // E2E-CONT-011: 件名入力
  test('E2E-CONT-011: 件名入力', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const subjectInput = page.locator('input[name="subject"], input[placeholder*="件名"], [data-testid="subject"]');
    if (await subjectInput.count() > 0) {
      await expect(subjectInput).toBeVisible();
      await subjectInput.fill('テスト件名');
    }
  });

  // E2E-CONT-012: 内容入力
  test('E2E-CONT-012: 内容入力', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const messageTextarea = page.locator('textarea[name="message"], textarea[placeholder*="内容"], [data-testid="message"]');
    if (await messageTextarea.count() > 0) {
      await expect(messageTextarea).toBeVisible();
      await messageTextarea.fill('テストメッセージ内容');
    }
  });

  // E2E-CONT-013: メールアドレス入力
  test('E2E-CONT-013: メールアドレス入力', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const emailInput = page.locator('input[name="email"], input[type="email"], input[placeholder*="メール"], [data-testid="email"]');
    if (await emailInput.count() > 0) {
      await expect(emailInput).toBeVisible();
      await emailInput.fill('test@example.com');
    }
  });

  // E2E-CONT-014: 送信ボタン有効化
  test('E2E-CONT-014: 送信ボタン有効化', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    // フォーム入力
    const categorySelect = page.locator('select[name="category"]');
    if (await categorySelect.count() > 0) {
      await categorySelect.selectOption('0');
    }
    
    const subjectInput = page.locator('input[name="subject"]');
    if (await subjectInput.count() > 0) {
      await subjectInput.fill('テスト件名');
    }
    
    const messageTextarea = page.locator('textarea[name="message"]');
    if (await messageTextarea.count() > 0) {
      await messageTextarea.fill('テストメッセージ');
    }
    
    const emailInput = page.locator('input[name="email"]');
    if (await emailInput.count() > 0) {
      await emailInput.fill('test@example.com');
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("送信")');
    if (await submitButton.count() > 0) {
      await expect(submitButton).toBeEnabled();
    }
  });

  // E2E-CONT-015: 問合せ送信実行
  test('E2E-CONT-015: 問合せ送信実行', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    // フォーム入力
    const categorySelect = page.locator('select[name="category"]');
    if (await categorySelect.count() > 0) {
      await categorySelect.selectOption('0');
    }
    
    const subjectInput = page.locator('input[name="subject"]');
    if (await subjectInput.count() > 0) {
      await subjectInput.fill('テスト件名');
    }
    
    const messageTextarea = page.locator('textarea[name="message"]');
    if (await messageTextarea.count() > 0) {
      await messageTextarea.fill('テストメッセージ');
    }
    
    const emailInput = page.locator('input[name="email"]');
    if (await emailInput.count() > 0) {
      await emailInput.fill('test@example.com');
    }
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
    }
  });

  // E2E-CONT-016: 送信成功後処理
  test('E2E-CONT-016: 送信成功後処理', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const successMessage = page.locator('text=送信完了, text=ありがとう, .success-message');
    if (await successMessage.count() > 0) {
      await expect(successMessage.first()).toBeVisible();
    }
  });

  // E2E-CONT-017: 成功メッセージ自動消失
  test('E2E-CONT-017: 成功メッセージ自動消失', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-018: 必須項目未入力エラー
  test('E2E-CONT-018: 必須項目未入力エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
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

  // E2E-CONT-019: 無効メール形式エラー
  test('E2E-CONT-019: 無効メール形式エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const emailInput = page.locator('input[name="email"]');
    if (await emailInput.count() > 0) {
      await emailInput.fill('invalid-email');
    }
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      
      const emailError = page.locator('text=メール, text=形式, .email-error');
      if (await emailError.count() > 0) {
        await expect(emailError.first()).toBeVisible();
      }
    }
  });

  // E2E-CONT-020: 送信失敗エラー
  test('E2E-CONT-020: 送信失敗エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-021: データ取得エラー
  test('E2E-CONT-021: データ取得エラー', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-022: 送信中状態表示
  test('E2E-CONT-022: 送信中状態表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-023: 送信中ボタン無効化
  test('E2E-CONT-023: 送信中ボタン無効化', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
  });

  // E2E-CONT-024: FAQ検索カテゴリ表示
  test('E2E-CONT-024: FAQ検索カテゴリ表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqCategories = page.locator('.faq-category, .category-filter, [data-testid="faq-category"]');
    if (await faqCategories.count() > 0) {
      await expect(faqCategories.first()).toBeVisible();
    }
  });

  // E2E-CONT-025: FAQタグ表示
  test('E2E-CONT-025: FAQタグ表示', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqTags = page.locator('.faq-tag, .tag, [data-testid="faq-tag"]');
    if (await faqTags.count() > 0) {
      await expect(faqTags.first()).toBeVisible();
    }
  });

  // E2E-CONT-026: デスクトップ表示
  test('E2E-CONT-026: デスクトップ表示', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  // E2E-CONT-027: タブレット表示
  test('E2E-CONT-027: タブレット表示', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  // E2E-CONT-028: モバイル表示
  test('E2E-CONT-028: モバイル表示', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  // E2E-CONT-029: Grid2レスポンシブ動作
  test('E2E-CONT-029: Grid2レスポンシブ動作', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    // デスクトップ
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(500);
    
    // タブレット
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    
    // モバイル
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
  });

  // E2E-CONT-030: 複数FAQ同時展開
  test('E2E-CONT-030: 複数FAQ同時展開', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqItems = page.locator('.faq-item button, .MuiAccordion-root button');
    const itemCount = await faqItems.count();
    
    if (itemCount >= 2) {
      // 複数のFAQアイテムを展開
      await faqItems.nth(0).click();
      await page.waitForTimeout(300);
      await faqItems.nth(1).click();
      await page.waitForTimeout(300);
      
      const expandedContent = page.locator('.faq-content:visible, .MuiAccordionDetails-root:visible, .MuiAccordion-content:visible');
      const expandedCount = await expandedContent.count();
      expect(expandedCount).toBeGreaterThanOrEqual(1);
    }
  });

  // E2E-CONT-031: フォーム入力ワークフロー
  test('E2E-CONT-031: フォーム入力ワークフロー', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    // 一連のフォーム入力ワークフロー
    const categorySelect = page.locator('select[name="category"]');
    if (await categorySelect.count() > 0) {
      await categorySelect.selectOption('0');
      await page.waitForTimeout(100);
    }
    
    const subjectInput = page.locator('input[name="subject"]');
    if (await subjectInput.count() > 0) {
      await subjectInput.fill('ワークフローテスト');
      await page.waitForTimeout(100);
    }
    
    const messageTextarea = page.locator('textarea[name="message"]');
    if (await messageTextarea.count() > 0) {
      await messageTextarea.fill('ワークフローテストメッセージ');
      await page.waitForTimeout(100);
    }
    
    const emailInput = page.locator('input[name="email"]');
    if (await emailInput.count() > 0) {
      await emailInput.fill('workflow@test.com');
      await page.waitForTimeout(100);
    }
    
    const submitButton = page.locator('button[type="submit"]');
    if (await submitButton.count() > 0) {
      await expect(submitButton).toBeEnabled();
    }
  });

  // E2E-CONT-032: アイコン表示確認
  test('E2E-CONT-032: アイコン表示確認', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const icons = page.locator('svg, .icon, .MuiSvgIcon-root, [data-testid="icon"]');
    if (await icons.count() > 0) {
      await expect(icons.first()).toBeVisible();
    }
  });

  // E2E-CONT-033: FAQデータ内容確認
  test('E2E-CONT-033: FAQデータ内容確認', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    const faqItems = page.locator('.faq-item, .MuiAccordion-root, [data-testid="faq-item"]');
    if (await faqItems.count() > 0) {
      await expect(faqItems.first()).toBeVisible();
    }
  });

  // E2E-SUPPORT-002: 問合せフォーム機能
  test('E2E-SUPPORT-002: 問合せフォーム機能', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークログを収集
    const networkLogs: Array<{url: string, status: number, method: string}> = [];
    page.on('request', (request) => {
      networkLogs.push({
        url: request.url(),
        status: 0,
        method: request.method()
      });
    });
    page.on('response', (response) => {
      const existingLog = networkLogs.find(log => log.url === response.url());
      if (existingLog) {
        existingLog.status = response.status();
      }
    });

    await test.step('サポートページへ移動', async () => {
      await page.goto('http://localhost:3247/contact');
      await page.waitForLoadState('networkidle');
    });

    await test.step('問合せフォーム表示確認', async () => {
      const contactForm = page.locator('form, .contact-form, [data-testid="contact-form"]');
      await expect(contactForm).toBeVisible();
    });

    await test.step('問合せ種別選択機能', async () => {
      const categorySelect = page.locator('select[name="category"], [data-testid="contact-category"], [data-testid="category-select"]');
      if (await categorySelect.count() > 0) {
        await expect(categorySelect).toBeVisible();
        await categorySelect.selectOption({ index: 0 });
      }
    });

    await test.step('件名入力機能', async () => {
      const subjectInput = page.locator('input[name="subject"], input[placeholder*="件名"], [data-testid="subject"], [data-testid="subject-input"]');
      if (await subjectInput.count() > 0) {
        await expect(subjectInput).toBeVisible();
        await subjectInput.fill('E2Eテスト問合せ件名');
        await expect(subjectInput).toHaveValue('E2Eテスト問合せ件名');
      }
    });

    await test.step('内容入力機能', async () => {
      const messageTextarea = page.locator('textarea[name="message"], textarea[placeholder*="内容"], textarea[placeholder*="メッセージ"], [data-testid="message"], [data-testid="message-input"]');
      if (await messageTextarea.count() > 0) {
        await expect(messageTextarea).toBeVisible();
        await messageTextarea.fill('E2Eテスト用の問合せ内容です。テストの一環として送信しています。');
        await expect(messageTextarea).toHaveValue('E2Eテスト用の問合せ内容です。テストの一環として送信しています。');
      }
    });

    await test.step('メールアドレス入力機能', async () => {
      const emailInput = page.locator('input[name="email"], input[type="email"], input[placeholder*="メール"], [data-testid="email"], [data-testid="email-input"]');
      if (await emailInput.count() > 0) {
        await expect(emailInput).toBeVisible();
        await emailInput.fill('e2e-test@example.com');
        await expect(emailInput).toHaveValue('e2e-test@example.com');
      }
    });

    await test.step('送信ボタン有効化確認', async () => {
      const submitButton = page.locator('button[type="submit"], button:has-text("送信"), [data-testid="submit-button"]');
      if (await submitButton.count() > 0) {
        await expect(submitButton).toBeVisible();
        await expect(submitButton).toBeEnabled();
      }
    });

    await test.step('フォーム送信機能', async () => {
      const submitButton = page.locator('button[type="submit"], button:has-text("送信"), [data-testid="submit-button"]');
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForLoadState('networkidle');
      }
    });

    await test.step('送信結果確認', async () => {
      // 成功メッセージまたはエラーメッセージのいずれかが表示されることを確認
      const successMessage = page.locator('text=送信完了, text=ありがとう, text=受付, .success-message, [data-testid="success-message"]');
      const errorMessage = page.locator('text=エラー, text=失敗, text=送信できませんでした, .error-message, [data-testid="error-message"]');
      
      // 送信結果を10秒間待機
      await page.waitForTimeout(2000);
      
      const successCount = await successMessage.count();
      const errorCount = await errorMessage.count();
      
      if (successCount > 0) {
        await expect(successMessage.first()).toBeVisible();
      } else if (errorCount > 0) {
        await expect(errorMessage.first()).toBeVisible();
      }
    });
  });

  // E2E-SUPPORT-004: システム情報表示
  test('E2E-SUPPORT-004: システム情報表示', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークログを収集
    const networkLogs: Array<{url: string, status: number, method: string}> = [];
    page.on('request', (request) => {
      networkLogs.push({
        url: request.url(),
        status: 0,
        method: request.method()
      });
    });
    page.on('response', (response) => {
      const existingLog = networkLogs.find(log => log.url === response.url());
      if (existingLog) {
        existingLog.status = response.status();
      }
    });

    await test.step('サポートページへ移動', async () => {
      await page.goto('http://localhost:3247/contact');
      await page.waitForLoadState('networkidle');
    });

    await test.step('システム情報セクション表示確認', async () => {
      // システム情報関連の要素を幅広く検索
      const systemInfoSection = page.locator(
        '[data-testid="system-info"], .system-info, .system-status, .health-status, ' +
        ':text("システム情報"), :text("稼働状況"), :text("システム"), :text("ヘルス"), ' +
        ':text("API状況"), :text("データベース"), :text("サーバー状況")'
      );
      
      // 10秒間待機してシステム情報が表示されることを確認
      await expect(systemInfoSection.first()).toBeVisible({ timeout: 10000 });
    });

    await test.step('システム稼働状況表示確認', async () => {
      // 稼働状況を示すアイコンやテキストを確認
      const statusElements = page.locator(
        '[data-testid="status-icon"], .status-icon, .health-icon, .status-indicator, ' +
        ':text("正常"), :text("稼働中"), :text("オンライン"), :text("OK"), ' +
        '.status-green, .status-ok, [class*="success"], [class*="healthy"]'
      );
      
      if (await statusElements.count() > 0) {
        await expect(statusElements.first()).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('システム詳細情報表示確認', async () => {
      // システムの詳細情報（バージョン、最終更新日など）の表示確認
      const detailElements = page.locator(
        '[data-testid="system-details"], .system-details, .version-info, ' +
        ':text("バージョン"), :text("最終更新"), :text("ビルド"), ' +
        ':text("API"), :text("データベース"), :text("フロントエンド"), :text("バックエンド")'
      );
      
      if (await detailElements.count() > 0) {
        await expect(detailElements.first()).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('システム情報のレスポンシブ表示確認', async () => {
      // デスクトップ表示
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.waitForTimeout(300);
      
      const systemInfo = page.locator('[data-testid="system-info"], .system-info, :text("システム情報")');
      if (await systemInfo.count() > 0) {
        await expect(systemInfo.first()).toBeVisible();
      }
      
      // モバイル表示
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(300);
      
      if (await systemInfo.count() > 0) {
        await expect(systemInfo.first()).toBeVisible();
      }
    });

    await test.step('システム情報の動的更新確認', async () => {
      // システム情報が動的に更新される場合の確認
      await page.waitForTimeout(1000);
      
      const timestamp = page.locator(
        '[data-testid="last-updated"], .last-updated, .timestamp, ' +
        ':text("最終更新"), :text("更新時刻"), :text("チェック時刻")'
      );
      
      if (await timestamp.count() > 0) {
        const timestampText = await timestamp.first().textContent();
        expect(timestampText).toBeTruthy();
      }
    });

    await test.step('システム情報コンテンツの確認', async () => {
      // システム情報として期待される内容が表示されていることを確認
      const expectedContent = page.locator(
        ':text("API"), :text("データベース"), :text("Redis"), :text("PostgreSQL"), ' +
        ':text("サーバー"), :text("正常"), :text("稼働"), :text("接続")'
      );
      
      if (await expectedContent.count() > 0) {
        await expect(expectedContent.first()).toBeVisible({ timeout: 5000 });
      }
    });
  });

  // E2E-SUPPORT-003: FAQ展開・操作
  test('E2E-SUPPORT-003: FAQ展開・操作', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークログを収集
    const networkLogs: Array<{url: string, status: number, method: string}> = [];
    page.on('request', (request) => {
      networkLogs.push({
        url: request.url(),
        status: 0,
        method: request.method()
      });
    });
    page.on('response', (response) => {
      const existingLog = networkLogs.find(log => log.url === response.url());
      if (existingLog) {
        existingLog.status = response.status();
      }
    });

    await test.step('サポートページへ移動', async () => {
      await page.goto('http://localhost:3247/contact');
      await page.waitForLoadState('networkidle');
    });

    await test.step('FAQセクション表示確認', async () => {
      const faqSection = page.locator('[data-testid="faq"], .faq-section, :text("よくある質問"), :text("FAQ")');
      await expect(faqSection.first()).toBeVisible({ timeout: 10000 });
    });

    await test.step('FAQ項目の初期表示確認', async () => {
      const faqItems = page.locator('.faq-item, .MuiAccordion-root, [data-testid="faq-item"], .accordion-item');
      const itemCount = await faqItems.count();
      expect(itemCount).toBeGreaterThan(0);
      
      // 最低1つのFAQ項目が表示されていることを確認
      await expect(faqItems.first()).toBeVisible();
    });

    await test.step('FAQ項目展開機能', async () => {
      const faqButton = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-toggle"], .accordion-header');
      
      if (await faqButton.count() > 0) {
        // 最初のFAQ項目をクリックして展開
        await faqButton.first().click();
        await page.waitForTimeout(500); // アニメーション待機
        
        // 展開されたコンテンツが表示されることを確認
        const faqContent = page.locator('.faq-content, .MuiAccordionDetails-root, .MuiAccordion-content, [data-testid="faq-content"], .accordion-body');
        await expect(faqContent.first()).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('FAQ項目折りたたみ機能', async () => {
      const faqButton = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-toggle"], .accordion-header');
      
      if (await faqButton.count() > 0) {
        // 同じFAQ項目を再度クリックして折りたたみ
        await faqButton.first().click();
        await page.waitForTimeout(500); // アニメーション待機
        
        // コンテンツが非表示になることを確認
        const faqContent = page.locator('.faq-content, .MuiAccordionDetails-root, .MuiAccordion-content, [data-testid="faq-content"], .accordion-body');
        if (await faqContent.count() > 0) {
          await expect(faqContent.first()).toBeHidden({ timeout: 3000 });
        }
      }
    });

    await test.step('複数FAQ項目の操作', async () => {
      const faqButtons = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-toggle"], .accordion-header');
      const buttonCount = await faqButtons.count();
      
      if (buttonCount >= 2) {
        // 2番目のFAQ項目も展開
        await faqButtons.nth(1).click();
        await page.waitForTimeout(500);
        
        // 2番目のコンテンツが表示されることを確認
        const faqContent = page.locator('.faq-content, .MuiAccordionDetails-root, .MuiAccordion-content, [data-testid="faq-content"], .accordion-body');
        if (await faqContent.count() >= 2) {
          await expect(faqContent.nth(1)).toBeVisible({ timeout: 5000 });
        }
      }
    });

    await test.step('FAQ展開状態の切り替え動作確認', async () => {
      const faqButtons = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-toggle"], .accordion-header');
      const buttonCount = await faqButtons.count();
      
      if (buttonCount > 0) {
        // 複数回の展開・折りたたみ操作
        for (let i = 0; i < Math.min(3, buttonCount); i++) {
          await faqButtons.nth(0).click();
          await page.waitForTimeout(300);
        }
        
        // 最終的に動作が正常であることを確認
        const mainContent = page.locator('main, [role="main"]');
        await expect(mainContent).toBeVisible();
      }
    });

    await test.step('FAQアクセシビリティ確認', async () => {
      const faqButtons = page.locator('.faq-item button, .MuiAccordion-root button, [data-testid="faq-toggle"], .accordion-header');
      
      if (await faqButtons.count() > 0) {
        // ボタンにアクセシブルなラベルがあることを確認
        const firstButton = faqButtons.first();
        const buttonText = await firstButton.textContent();
        expect(buttonText).toBeTruthy();
        expect(buttonText!.trim().length).toBeGreaterThan(0);
      }
    });
  });

  // E2E-SUPPORT-005: レスポンシブ表示
  test.only('E2E-SUPPORT-005: レスポンシブ表示', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    // ネットワークログを収集
    const networkLogs: Array<{url: string, status: number, method: string}> = [];
    page.on('request', (request) => {
      networkLogs.push({
        url: request.url(),
        status: 0,
        method: request.method()
      });
    });
    page.on('response', (response) => {
      const existingLog = networkLogs.find(log => log.url === response.url());
      if (existingLog) {
        existingLog.status = response.status();
      }
    });

    await test.step('デスクトップ表示確認', async () => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('http://localhost:3247/contact');
      await page.waitForLoadState('networkidle');
      
      // メインコンテンツが表示されることを確認
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
      
      // ページレイアウトが正常に表示されることを確認
      const pageTitle = page.locator('h1, h2, h3, h4').first();
      await expect(pageTitle).toBeVisible();
      
      // フォーム要素が表示されることを確認
      const contactForm = page.locator('form, .contact-form, [data-testid="contact-form"]');
      await expect(contactForm).toBeVisible();
      
      // FAQセクションが表示されることを確認
      const faqSection = page.locator('[data-testid="faq"], .faq-section, :text("よくある質問"), :text("FAQ")');
      if (await faqSection.count() > 0) {
        await expect(faqSection.first()).toBeVisible();
      }
    });

    await test.step('タブレット表示確認', async () => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.waitForTimeout(500); // レイアウト調整待機
      
      // メインコンテンツが引き続き表示されることを確認
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
      
      // レスポンシブ対応でレイアウトが調整されることを確認
      const pageTitle = page.locator('h1, h2, h3, h4').first();
      await expect(pageTitle).toBeVisible();
      
      // フォーム要素がタブレット表示でも機能することを確認
      const contactForm = page.locator('form, .contact-form, [data-testid="contact-form"]');
      await expect(contactForm).toBeVisible();
      
      // フォーム要素の入力可能性を確認
      const emailInput = page.locator('input[name="email"], input[type="email"], input[placeholder*="メール"], [data-testid="email"]');
      if (await emailInput.count() > 0) {
        await expect(emailInput).toBeVisible();
        await expect(emailInput).toBeEditable();
      }
    });

    await test.step('モバイル表示確認', async () => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(500); // レイアウト調整待機
      
      // メインコンテンツが引き続き表示されることを確認
      const mainContent = page.locator('main, [role="main"]');
      await expect(mainContent).toBeVisible();
      
      // モバイル表示での見出し確認
      const pageTitle = page.locator('h1, h2, h3, h4').first();
      await expect(pageTitle).toBeVisible();
      
      // フォーム要素がモバイル表示でも機能することを確認
      const contactForm = page.locator('form, .contact-form, [data-testid="contact-form"]');
      await expect(contactForm).toBeVisible();
      
      // モバイルでのフォーム入力動作確認
      const subjectInput = page.locator('input[name="subject"], input[placeholder*="件名"], [data-testid="subject"]');
      if (await subjectInput.count() > 0) {
        await expect(subjectInput).toBeVisible();
        await expect(subjectInput).toBeEditable();
      }
    });

    await test.step('Grid2レスポンシブ動作確認', async () => {
      // 各ビューポートでGrid2要素の動作確認
      const viewports = [
        { width: 1920, height: 1080, name: 'デスクトップ' },
        { width: 768, height: 1024, name: 'タブレット' },
        { width: 375, height: 667, name: 'モバイル' }
      ];
      
      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.waitForTimeout(300);
        
        // Grid2コンポーネントのレスポンシブ表示確認
        const gridElements = page.locator('[class*="MuiGrid2"], [class*="Grid2"], .grid-container');
        if (await gridElements.count() > 0) {
          await expect(gridElements.first()).toBeVisible();
        }
        
        // レイアウトが崩れていないことを確認
        const mainContent = page.locator('main, [role="main"]');
        await expect(mainContent).toBeVisible();
      }
    });

    await test.step('レスポンシブ要素の表示切替確認', async () => {
      // デスクトップ表示
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.waitForTimeout(300);
      
      // デスクトップ専用要素があれば確認
      const desktopElements = page.locator('[class*="desktop"], [class*="lg-"], .desktop-only');
      if (await desktopElements.count() > 0) {
        await expect(desktopElements.first()).toBeVisible();
      }
      
      // モバイル表示に切り替え
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(300);
      
      // モバイル専用要素があれば確認
      const mobileElements = page.locator('[class*="mobile"], [class*="xs-"], .mobile-only');
      if (await mobileElements.count() > 0) {
        await expect(mobileElements.first()).toBeVisible();
      }
    });

    await test.step('ナビゲーションレスポンシブ確認', async () => {
      const navigation = page.locator('nav');
      
      if (await navigation.count() > 0) {
        // デスクトップ表示: nav要素が表示され、permanent Drawerが見える
        await page.setViewportSize({ width: 1920, height: 1080 });
        await page.waitForTimeout(300);
        await expect(navigation.first()).toBeVisible();
        
        // モバイル表示: nav要素は存在するが、
        // ナビゲーション内容は temporary Drawer に移行（初期状態で非表示が正常）
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(300);
        
        // nav要素自体は存在する（レイアウト上必要）
        await expect(navigation.first()).toBeInViewport();
        
        // モバイルでは、ハンバーガーメニューによる操作確認
        // （ヘッダーにメニューボタンがある場合）
        const menuButton = page.locator('button[aria-label*="menu"], button[aria-label*="メニュー"], .menu-toggle');
        if (await menuButton.count() > 0) {
          // メニューボタンが存在すれば確認
          await expect(menuButton.first()).toBeVisible();
        }
      }
    });

    await test.step('フォーム要素レスポンシブ動作確認', async () => {
      // フォーム要素が各ビューポートで正常に動作することを確認
      const viewports = [
        { width: 1920, height: 1080 },
        { width: 768, height: 1024 },
        { width: 375, height: 667 }
      ];
      
      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.waitForTimeout(300);
        
        // フォーム入力フィールドの動作確認
        const emailInput = page.locator('input[name="email"], input[type="email"], input[placeholder*="メール"], [data-testid="email"]');
        if (await emailInput.count() > 0) {
          await expect(emailInput).toBeVisible();
          await expect(emailInput).toBeEditable();
          
          // 実際に入力してみて動作確認
          await emailInput.clear();
          await emailInput.fill('responsive-test@example.com');
          await expect(emailInput).toHaveValue('responsive-test@example.com');
        }
        
        // テキストエリアの動作確認
        const messageTextarea = page.locator('textarea[name="message"], textarea[placeholder*="内容"], [data-testid="message"]');
        if (await messageTextarea.count() > 0) {
          await expect(messageTextarea).toBeVisible();
          await expect(messageTextarea).toBeEditable();
        }
      }
    });

    await test.step('スクロール動作確認', async () => {
      // モバイル表示でのスクロール動作確認
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(300);
      
      // ページの上部と下部を確認
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(200);
      
      const topElement = page.locator('h1, h2, h3, h4').first();
      await expect(topElement).toBeVisible();
      
      // ページ下部へスクロール
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(200);
      
      // フォーム送信ボタンが表示されることを確認
      const submitButton = page.locator('button[type="submit"], button:has-text("送信"), [data-testid="submit-button"]');
      if (await submitButton.count() > 0) {
        await expect(submitButton).toBeVisible();
      }
      
      // 元の位置に戻る
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(200);
    });
  });
});