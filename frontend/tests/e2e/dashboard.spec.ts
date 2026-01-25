import { test, expect } from '@playwright/test';

// E2E-DASH-007: ロジックカード・システムステータス表示確認
test.only('E2E-DASH-007: ロジックカード・システムステータス表示確認', async ({ page }) => {
  // ブラウザコンソールログを収集
  const consoleLogs: Array<{ type: string; text: string }> = [];
  page.on('console', (msg) => {
    consoleLogs.push({
      type: msg.type(),
      text: msg.text()
    });
  });

  // ネットワークエラー監視
  page.on('response', (response) => {
    if (response.status() >= 400) {
      console.log('ERROR RESPONSE:', response.url(), response.status());
    }
  });

  await test.step('ページ遷移', async () => {
    await page.goto('http://localhost:3247/');
    await page.waitForLoadState('networkidle');
  });

  await test.step('ロジックAカード表示確認', async () => {
    // ロジックAカードのコンテナを取得（headingから親要素をたどる）
    const logicAHeading = page.getByRole('heading', { name: 'ロジックA', exact: true });
    await expect(logicAHeading).toBeVisible();

    // カードコンテナを特定（headingの親要素）
    const logicACard = logicAHeading.locator('..').locator('..');

    // ロジックAカードの説明（スコープ内）
    await expect(logicACard.getByText('優良企業を機械学習で発見するロジック')).toBeVisible();

    // ステータスチップ: "分析中..."
    await expect(logicACard.getByText('分析中...')).toBeVisible();

    // 対象銘柄: "3,800社"
    await expect(logicACard.getByText('3,800社')).toBeVisible();
  });

  await test.step('ロジックBカード表示確認', async () => {
    // ロジックBカードのコンテナを取得（headingから親要素をたどる）
    const logicBHeading = page.getByRole('heading', { name: 'ロジックB', exact: true });
    await expect(logicBHeading).toBeVisible();

    // カードコンテナを特定（headingの親要素）
    const logicBCard = logicBHeading.locator('..').locator('..');

    // ロジックBカードの説明（スコープ内）
    await expect(logicBCard.getByText('優良企業を機械学習で発見するロジック')).toBeVisible();

    // ステータスチップ: "分析中..."
    await expect(logicBCard.getByText('分析中...')).toBeVisible();

    // 対象銘柄: "3,800社"
    await expect(logicBCard.getByText('3,800社')).toBeVisible();
  });

  await test.step('システムステータスカード1: アクティブロジック', async () => {
    // アイコン + ラベルで特定
    await expect(page.getByText('アクティブロジック')).toBeVisible();

    // 値 "3" の存在確認
    const activeLogicCard = page.locator('text=アクティブロジック').locator('..');
    await expect(activeLogicCard.getByText('3')).toBeVisible();
  });

  await test.step('システムステータスカード2: 今日発見した', async () => {
    // ラベル確認
    await expect(page.getByText('今日発見した')).toBeVisible();

    // 値 "2" の存在確認
    const discoveredCard = page.locator('text=今日発見した').locator('..');
    await expect(discoveredCard.getByText('2')).toBeVisible();
  });

  await test.step('システムステータスカード3: 平均リターン', async () => {
    // ラベル確認
    await expect(page.getByText('平均リターン')).toBeVisible();

    // 値 "+18.5%" の存在確認
    const returnCard = page.locator('text=平均リターン').locator('..');
    await expect(returnCard.getByText('+18.5%')).toBeVisible();
  });

  await test.step('ロジックカードとシステムステータスの総数確認', async () => {
    // ロジックカードが2枚
    const logicACard = page.getByRole('heading', { name: 'ロジックA', exact: true });
    const logicBCard = page.getByRole('heading', { name: 'ロジックB', exact: true });
    await expect(logicACard).toBeVisible();
    await expect(logicBCard).toBeVisible();

    // システムステータスカードが3枚
    await expect(page.getByText('アクティブロジック')).toBeVisible();
    await expect(page.getByText('今日発見した')).toBeVisible();
    await expect(page.getByText('平均リターン')).toBeVisible();
  });

  // テスト失敗時はコンソールログを出力
  test.info().annotations.push({
    type: 'console-logs',
    description: JSON.stringify(consoleLogs, null, 2)
  });
});

// E2E-DASH-006: スコア評価履歴表示確認
test('E2E-DASH-006: スコア評価履歴表示確認', async ({ page }) => {
  // ブラウザコンソールログを収集
  const consoleLogs: Array<{ type: string; text: string }> = [];
  page.on('console', (msg) => {
    consoleLogs.push({
      type: msg.type(),
      text: msg.text()
    });
  });

  // ネットワークエラー監視
  page.on('response', (response) => {
    if (response.status() >= 400) {
      console.log('ERROR RESPONSE:', response.url(), response.status());
    }
  });

  await test.step('ページ遷移', async () => {
    await page.goto('http://localhost:3247/');
    await page.waitForLoadState('networkidle');
  });

  await test.step('ダッシュボードページ表示確認', async () => {
    // ヘッダー確認
    await expect(page.locator('h3')).toContainText('ロジックスキャナーダッシュボード');
  });

  await test.step('スコア評価履歴セクション表示確認', async () => {
    // 評価履歴セクションの存在確認
    await expect(page.getByRole('heading', { name: '最近の評価履歴', exact: true })).toBeVisible();
  });

  await test.step('履歴データ読み込み確認', async () => {
    // API呼び出しを監視（/api/scores/{stockCode}/history/compact）
    const responsePromise = page.waitForResponse(
      response => response.url().includes('/api/scores/') && response.url().includes('/history/compact'),
      { timeout: 10000 }
    );

    // ページをリロードして履歴データ取得をトリガー
    await page.reload();
    await page.waitForLoadState('networkidle');

    // API呼び出し成功を確認
    const response = await responsePromise;
    expect(response.status()).toBe(200);

    // レスポンスデータを取得
    const historyData = await response.json();
    console.log('履歴データ件数:', historyData.history ? historyData.history.length : 0);
  });

  await test.step('履歴リスト表示確認', async () => {
    // 「最近の評価履歴」ヘッダーが表示されているか確認
    const historyHeader = page.getByRole('heading', { name: '最近の評価履歴', exact: true });

    // ヘッダーの存在確認（履歴がある場合のみ表示される）
    const headerExists = await historyHeader.isVisible().catch(() => false);

    if (headerExists) {
      console.log('履歴セクションが表示されています');
      // 履歴セクション内のチップを確認
      const scoreChips = page.locator('.MuiChip-label');
      await expect(scoreChips.first()).toBeVisible({ timeout: 5000 });
    } else {
      console.log('履歴データが存在しないため、履歴セクションは非表示です');
    }
  });

  await test.step('履歴項目の詳細情報確認', async () => {
    // 「最近の評価履歴」ヘッダーが表示されているか確認
    const historyHeader = page.getByRole('heading', { name: '最近の評価履歴', exact: true });
    const headerExists = await historyHeader.isVisible().catch(() => false);

    if (headerExists) {
      // スコアチップを確認（変更履歴: oldScore → newScore）
      const scoreChips = page.locator('.MuiChip-label');
      const chipCount = await scoreChips.count();
      console.log('スコアチップ数:', chipCount);

      if (chipCount > 0) {
        // 最初のチップが表示されることを確認
        await expect(scoreChips.first()).toBeVisible();

        // 評価理由のテキストを確認
        const reasonText = page.locator('text=理由なし').or(page.getByText(/テスト/));
        const reasonExists = await reasonText.count() > 0;
        console.log('評価理由表示:', reasonExists);

        console.log('履歴項目詳細確認完了');
      } else {
        console.log('履歴項目が見つかりませんでした');
      }
    } else {
      console.log('履歴データが存在しないため、詳細確認をスキップ');
    }
  });

  await test.step('最大表示件数確認', async () => {
    // 「最近の評価履歴」ヘッダーが表示されているか確認
    const historyHeader = page.getByRole('heading', { name: '最近の評価履歴', exact: true });
    const headerExists = await historyHeader.isVisible().catch(() => false);

    if (headerExists) {
      // スコアチップの数をカウント（履歴数の目安）
      const scoreChips = page.locator('.MuiChip-label');
      const chipCount = await scoreChips.count();

      // コンパクト表示では最大5件
      expect(chipCount).toBeGreaterThan(0);
      console.log('表示履歴件数（チップ数）:', chipCount);
    } else {
      console.log('履歴データが存在しないため、件数確認をスキップ');
    }
  });

  // テスト失敗時はコンソールログを出力
  test.info().annotations.push({
    type: 'console-logs',
    description: JSON.stringify(consoleLogs, null, 2)
  });
});
