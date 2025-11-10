import { Page } from '@playwright/test';

/**
 * ログイン処理を実行するヘルパー関数
 * 認証なし個人利用版 - 直接ダッシュボードにアクセス
 * @param page - Playwrightのページオブジェクト
 * @param email - 未使用（認証なし）
 * @param password - 未使用（認証なし）
 */
export async function login(page: Page, email = 'demo@example.com', password = 'demo123') {
  // 認証なし個人利用 - 直接ダッシュボードにアクセス
  await page.goto('/');
  
  // ダッシュボードページの読み込み完了を待機
  await page.waitForLoadState('networkidle');
  
  // ダッシュボードが正常に表示されているか確認
  await page.waitForSelector('[data-testid="dashboard-container"]', { timeout: 10000 });
}