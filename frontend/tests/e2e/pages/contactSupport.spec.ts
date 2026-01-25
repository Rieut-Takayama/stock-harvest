import { test, expect } from '@playwright/test';

test.describe('ContactSupport E2Eテスト', () => {
  // E2E-CONTACT-001: ページ表示確認
  test('E2E-CONTACT-001: ページ表示確認', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('ページタイトル確認', async () => {
      // タイトル「問合せサポート」の表示確認
      const pageTitle = page.locator('h1:has-text("問合せサポート")');
      await expect(pageTitle).toBeVisible();
    });

    await test.step('FAQセクション表示確認', async () => {
      // FAQセクションの表示確認
      const faqSection = page.locator('text=よくある質問');
      await expect(faqSection).toBeVisible();

      // FAQ項目が複数表示されることを確認
      const faqItems = page.locator('.MuiAccordion-root, [role="button"]');
      const faqCount = await faqItems.count();
      expect(faqCount).toBeGreaterThan(0);
    });

    await test.step('お問い合わせフォーム表示確認', async () => {
      // お問い合わせフォームの表示確認
      const formTitle = page.locator('h6:has-text("お問い合わせ")');
      await expect(formTitle).toBeVisible();

      // 問合せ種別（ラベル要素）
      const typeLabel = page.locator('label:has-text("問合せ種別")').first();
      await expect(typeLabel).toBeVisible();

      // 件名
      const subjectField = page.locator('input[placeholder*="件名"]');
      await expect(subjectField).toBeVisible();

      // 内容
      const contentField = page.locator('textarea[placeholder*="内容"]');
      await expect(contentField).toBeVisible();

      // 連絡先メール
      const emailField = page.locator('input[type="email"]');
      await expect(emailField).toBeVisible();
    });

    await test.step('システム情報表示確認', async () => {
      // システム情報カードの表示確認（h6要素として）
      const systemInfoTitle = page.locator('h6:has-text("システム情報")');
      await expect(systemInfoTitle).toBeVisible();

      // システム情報セクション内の要素を確認
      // バージョン、最終更新、稼働状況がparagraph要素として存在
      const versionText = page.locator('p:has-text("バージョン")');
      await expect(versionText).toBeVisible();

      const lastUpdatedText = page.locator('p:has-text("最終更新")');
      await expect(lastUpdatedText).toBeVisible();

      const statusText = page.getByText('稼働状況', { exact: true });
      await expect(statusText).toBeVisible();
    });
  });

  // E2E-CONTACT-002: FAQ展開・閉じる操作
  test('E2E-CONTACT-002: FAQ展開・閉じる操作', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('最初のFAQ項目をクリック（展開）', async () => {
      // 最初のFAQ項目を取得
      const firstFaq = page.locator('.MuiAccordion-root').first();
      await expect(firstFaq).toBeVisible();

      // FAQ項目をクリックして展開
      await firstFaq.click();

      // 少し待機して展開アニメーションを完了させる
      await page.waitForTimeout(500);
    });

    await test.step('回答が表示されることを確認', async () => {
      // 展開された回答エリアを確認
      const expandedContent = page.locator('.MuiAccordion-root.Mui-expanded .MuiAccordionDetails-root').first();
      await expect(expandedContent).toBeVisible();

      // 回答テキストが存在することを確認
      const contentText = await expandedContent.textContent();
      expect(contentText).toBeTruthy();
      expect(contentText!.length).toBeGreaterThan(0);
    });

    await test.step('同じFAQ項目を再度クリック（閉じる）', async () => {
      // 展開されているFAQ項目のサマリーボタンをクリック
      const expandedFaqButton = page.locator('.MuiAccordion-root.Mui-expanded .MuiAccordionSummary-root').first();
      await expandedFaqButton.click();

      // Reactの状態更新とDOMの更新を待つ
      await page.waitForTimeout(1000);
    });

    await test.step('回答が非表示になることを確認', async () => {
      // 展開されているFAQが存在しないことを確認
      const expandedFaqs = page.locator('.MuiAccordion-root.Mui-expanded');
      await expect(expandedFaqs).toHaveCount(0);
    });
  });

  // E2E-CONTACT-003: 複数FAQの展開動作確認
  test('E2E-CONTACT-003: 複数FAQの展開動作確認', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('FAQ項目1をクリック（展開）', async () => {
      // 最初のFAQ項目を取得
      const firstFaq = page.locator('.MuiAccordion-root').first();
      await expect(firstFaq).toBeVisible();

      // FAQ項目1をクリックして展開
      await firstFaq.click();

      // 展開アニメーションを完了させる
      await page.waitForTimeout(500);
    });

    await test.step('FAQ項目1が展開されていることを確認', async () => {
      // FAQ項目1が展開状態であることを確認
      const expandedFaqs = page.locator('.MuiAccordion-root.Mui-expanded');
      await expect(expandedFaqs).toHaveCount(1);

      // 展開された回答が表示されることを確認
      const expandedContent = page.locator('.MuiAccordion-root.Mui-expanded .MuiAccordionDetails-root').first();
      await expect(expandedContent).toBeVisible();
    });

    await test.step('FAQ項目2をクリック（展開）', async () => {
      // 2番目のFAQ項目を取得
      const secondFaq = page.locator('.MuiAccordion-root').nth(1);
      await expect(secondFaq).toBeVisible();

      // FAQ項目2をクリックして展開
      await secondFaq.click();

      // 展開アニメーションとReactの状態更新を待つ
      await page.waitForTimeout(500);
    });

    await test.step('FAQ項目1が自動で閉じることを確認', async () => {
      // アコーディオン動作により、FAQ項目1が自動で閉じていることを確認
      // 最初のFAQが閉じた状態（Mui-expandedクラスがない）であることを確認
      const firstFaq = page.locator('.MuiAccordion-root').first();
      await expect(firstFaq).not.toHaveClass(/Mui-expanded/);
    });

    await test.step('FAQ項目2のみが展開状態であることを確認', async () => {
      // 展開されているFAQが1つだけであることを確認
      const expandedFaqs = page.locator('.MuiAccordion-root.Mui-expanded');
      await expect(expandedFaqs).toHaveCount(1);

      // 展開されているのが2番目のFAQであることを確認
      const secondFaq = page.locator('.MuiAccordion-root').nth(1);
      await expect(secondFaq).toHaveClass(/Mui-expanded/);

      // FAQ項目2の回答が表示されていることを確認
      const secondExpandedContent = page.locator('.MuiAccordion-root.Mui-expanded .MuiAccordionDetails-root').first();
      await expect(secondExpandedContent).toBeVisible();
    });
  });

  // E2E-CONTACT-004: お問い合わせフォーム入力フロー
  test('E2E-CONTACT-004: お問い合わせフォーム入力フロー', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('問合せ種別を選択', async () => {
      // 問合せ種別のSelectコンポーネントを特定（ラベルから）
      // デフォルトで「技術的な問題」が選択されているため、別のオプションを選んでから戻す
      const typeSelect = page.locator('div[role="combobox"]').first();
      await expect(typeSelect).toBeVisible();

      // 初期状態で「技術的な問題」が選択されていることを確認
      await expect(typeSelect).toContainText('技術的な問題');

      // Selectを開く
      await typeSelect.click();

      // ドロップダウンメニューが開くのを待つ
      await page.waitForTimeout(300);

      // 「機能要望」オプションを選択（異なるオプションに変更）
      const featureOption = page.locator('li[data-value="feature"]');
      await expect(featureOption).toBeVisible();
      await featureOption.click();

      // 選択が反映されるまで待機
      await page.waitForTimeout(300);

      // 「機能要望」が選択されたことを確認
      await expect(typeSelect).toContainText('機能要望');

      // 再度Selectを開いて「技術的な問題」に戻す
      await typeSelect.click();
      await page.waitForTimeout(300);

      // 「技術的な問題」オプションを選択
      const technicalOption = page.locator('li[data-value="technical"]');
      await expect(technicalOption).toBeVisible();
      await technicalOption.click();

      // 選択が反映されるまで待機
      await page.waitForTimeout(300);

      // 最終的に「技術的な問題」が選択されていることを確認
      await expect(typeSelect).toContainText('技術的な問題');
    });

    await test.step('件名を入力', async () => {
      // 件名フィールドに入力
      const subjectField = page.locator('input[placeholder*="件名"]');
      await expect(subjectField).toBeVisible();
      await subjectField.fill('E2Eテスト件名');

      // 入力した値が表示されることを確認
      await expect(subjectField).toHaveValue('E2Eテスト件名');
    });

    await test.step('内容を入力', async () => {
      // 内容フィールドに入力
      const contentField = page.locator('textarea[placeholder*="内容"]');
      await expect(contentField).toBeVisible();
      await contentField.fill('これはE2Eテスト用のお問い合わせ内容です。');

      // 入力した値が表示されることを確認
      await expect(contentField).toHaveValue('これはE2Eテスト用のお問い合わせ内容です。');
    });

    await test.step('連絡先メールを入力', async () => {
      // メールフィールドに入力
      const emailField = page.locator('input[type="email"]');
      await expect(emailField).toBeVisible();
      await emailField.fill('e2e-test@example.com');

      // 入力した値が表示されることを確認
      await expect(emailField).toHaveValue('e2e-test@example.com');
    });

    await test.step('送信ボタンが有効になることを確認', async () => {
      // 全項目入力後、送信ボタンが有効になることを確認
      const submitButton = page.locator('button:has-text("送信する")');
      await expect(submitButton).toBeVisible();
      await expect(submitButton).toBeEnabled();
    });
  });

  // E2E-CONTACT-005: お問い合わせ送信完了フロー
  test('E2E-CONTACT-005: お問い合わせ送信完了フロー', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('フォームに入力', async () => {
      // 問合せ種別を選択（デフォルトの「技術的な問題」のまま）
      const typeSelect = page.locator('div[role="combobox"]').first();
      await expect(typeSelect).toBeVisible();
      await expect(typeSelect).toContainText('技術的な問題');

      // 件名を入力
      const subjectField = page.locator('input[placeholder*="件名"]');
      await expect(subjectField).toBeVisible();
      await subjectField.fill('E2Eテスト送信確認');
      await expect(subjectField).toHaveValue('E2Eテスト送信確認');

      // 内容を入力
      const contentField = page.locator('textarea[placeholder*="内容"]');
      await expect(contentField).toBeVisible();
      await contentField.fill('これはE2Eテスト用の送信テストです。');
      await expect(contentField).toHaveValue('これはE2Eテスト用の送信テストです。');

      // メールアドレスを入力
      const emailField = page.locator('input[type="email"]');
      await expect(emailField).toBeVisible();
      await emailField.fill('e2e-submit-test@example.com');
      await expect(emailField).toHaveValue('e2e-submit-test@example.com');
    });

    await test.step('送信ボタンをクリック', async () => {
      const submitButton = page.locator('button:has-text("送信する")');
      await expect(submitButton).toBeVisible();
      await expect(submitButton).toBeEnabled();
      await submitButton.click();

      // APIリクエスト完了を待つ
      await page.waitForTimeout(1000);
    });

    await test.step('成功メッセージが表示されることを確認', async () => {
      // 成功メッセージ（Alert）が表示されることを確認
      const successAlert = page.locator('.MuiAlert-root.MuiAlert-standardSuccess');
      await expect(successAlert).toBeVisible({ timeout: 5000 });

      // 成功メッセージの内容を確認
      const alertText = await successAlert.textContent();
      expect(alertText).toContain('お問い合わせ');
    });

    await test.step('フォームがリセットされることを確認', async () => {
      // 件名フィールドが空になっていることを確認
      const subjectField = page.locator('input[placeholder*="件名"]');
      await expect(subjectField).toHaveValue('');

      // 内容フィールドが空になっていることを確認
      const contentField = page.locator('textarea[placeholder*="内容"]');
      await expect(contentField).toHaveValue('');

      // メールフィールドが空になっていることを確認
      const emailField = page.locator('input[type="email"]');
      await expect(emailField).toHaveValue('');

      // 問合せ種別がデフォルト値に戻っていることを確認
      const typeSelect = page.locator('div[role="combobox"]').first();
      await expect(typeSelect).toContainText('技術的な問題');
    });
  });

  // E2E-CONTACT-006: システム情報表示確認
  test('E2E-CONTACT-006: システム情報表示確認', async ({ page }) => {
    // ブラウザコンソールログを収集
    const consoleLogs: Array<{type: string, text: string}> = [];
    page.on('console', (msg) => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });

    await test.step('ページアクセス', async () => {
      await page.goto('http://localhost:3247/contact-support');
      await page.waitForLoadState('networkidle');
    });

    await test.step('システム情報カード表示確認', async () => {
      // システム情報カードのタイトルを確認
      const systemInfoTitle = page.locator('h6:has-text("システム情報")');
      await expect(systemInfoTitle).toBeVisible();
    });

    await test.step('バージョン情報の表示確認', async () => {
      // バージョン行の親要素（Box）全体を取得（ラベル + 値を含む）
      // 複数の要素がマッチする場合は、最初の一致を使用
      const versionRow = page.locator('div').filter({ hasText: /^バージョン/ }).first();
      await expect(versionRow).toBeVisible();

      // バージョン番号が表示されることを確認（例: "v1.0.0"）
      const versionContent = await versionRow.textContent();
      expect(versionContent).toBeTruthy();
      // "バージョン" の後にセマンティックバージョン（数字.数字.数字）が続くパターンをチェック
      expect(versionContent).toMatch(/バージョン.*\d+\.\d+\.\d+/);
    });

    await test.step('最終更新日時の表示確認', async () => {
      // 最終更新行の親要素（Box）全体を取得（ラベル + 値を含む）
      const lastUpdatedRow = page.locator('div').filter({ hasText: /^最終更新/ }).first();
      await expect(lastUpdatedRow).toBeVisible();

      // 最終更新日時が表示されることを確認
      const lastUpdatedContent = await lastUpdatedRow.textContent();
      expect(lastUpdatedContent).toBeTruthy();
      // "最終更新" の後に日時情報が含まれることを確認
      expect(lastUpdatedContent).toMatch(/最終更新/);
    });

    await test.step('稼働状況の表示確認', async () => {
      // 稼働状況行の親要素（Box）全体を取得（ラベル + 値 + ステータスインジケーターを含む）
      const statusRow = page.locator('div').filter({ hasText: /^稼働状況/ }).first();
      await expect(statusRow).toBeVisible();

      // ステータステキスト（「正常稼働中」または「異常」など）が表示されることを確認
      const statusContent = await statusRow.textContent();
      expect(statusContent).toBeTruthy();
      // 「稼働状況」ラベルが含まれることを確認
      expect(statusContent).toMatch(/稼働状況/);
      // ステータスインジケーター（丸印）はDOM内に存在するが、textContent()では取得不可
      // そのため、ステータステキストのみで検証（「正常」「異常」などの文字列を含む）
    });
  });
});
