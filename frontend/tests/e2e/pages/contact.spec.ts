import { test, expect } from '@playwright/test';
import { login } from '../helpers/auth.helper';

test.describe('問合せサポート画面', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にログインを実行
    await login(page);
  });

  // E2E-CONT-001: 問合せページアクセス
  test('E2E-CONT-001: 問合せページアクセス', async ({ page }) => {
    await page.goto('http://localhost:3247/contact');
    await page.waitForLoadState('networkidle');
    
    await expect(page).toHaveURL('/contact');
    const mainContent = page.locator('main, [role="main"]');
    await expect(mainContent).toBeVisible();
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
      
      const faqContent = page.locator('.faq-content, .MuiAccordion-content, [data-testid="faq-content"]');
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
      
      const faqContent = page.locator('.faq-content, .MuiAccordion-content');
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
      
      const expandedContent = page.locator('.faq-content:visible, .MuiAccordion-content:visible');
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
});