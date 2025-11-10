import { test, expect } from '@playwright/test';

test.describe('ログイン機能', () => {
  test('ログインページが正しく表示される', async ({ page }) => {
    await page.goto('/login');

    // ページタイトルを確認
    await expect(page).toHaveTitle(/frontend/);

    // ログインフォームの要素が存在することを確認
    await expect(page.getByLabel('メールアドレス')).toBeVisible();
    await expect(page.getByLabel('パスワード')).toBeVisible();
    await expect(page.getByRole('button', { name: 'ログイン' })).toBeVisible();

    // ログインボタンのテキストを確認
    const submitButton = page.getByRole('button', { name: 'ログイン' });
    await expect(submitButton).toBeVisible();
  });

  test('デモアカウントでログイン成功', async ({ page }) => {
    await page.goto('/login');

    // デモユーザーでログイン
    await page.getByLabel('メールアドレス').fill('demo@example.com');
    await page.getByLabel('パスワード').fill('demo123');
    await page.getByRole('button', { name: 'ログイン' }).click();

    // ダッシュボードページへのリダイレクトを確認
    await expect(page).toHaveURL('/');

    // ダッシュボードのヘッダーが表示されることを確認
    await expect(page.locator('header')).toBeVisible();
  });

  test('無効な認証情報でログイン失敗', async ({ page }) => {
    await page.goto('/login');

    // 無効な認証情報でログイン試行
    await page.getByLabel('メールアドレス').fill('invalid@example.com');
    await page.getByLabel('パスワード').fill('wrongpassword');
    await page.getByRole('button', { name: 'ログイン' }).click();

    // エラーメッセージまたはログインページに留まることを確認
    // (実装に応じてアサーションを調整)
    await expect(page.getByLabel('メールアドレス')).toBeVisible();
  });
});