import type { User } from '../types';

interface Tokens {
  accessToken: string;
  refreshToken: string;
}

class TokenService {
  private ACCESS_TOKEN_KEY = 'accessToken';
  private REFRESH_TOKEN_KEY = 'refreshToken';

  // アクセストークンの取得
  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  // リフレッシュトークンの取得
  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  // トークンの設定
  setTokens({ accessToken, refreshToken }: Tokens): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  // 永続化トークンの設定（Remember Me機能）
  setPersistentTokens({ accessToken, refreshToken }: Tokens): void {
    // 本番環境では httpOnly Cookie を使用する予定
    // 開発環境では localStorage を使用
    localStorage.setItem(`${this.ACCESS_TOKEN_KEY}_persistent`, accessToken);
    localStorage.setItem(`${this.REFRESH_TOKEN_KEY}_persistent`, refreshToken);
  }

  // トークンのクリア
  clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(`${this.ACCESS_TOKEN_KEY}_persistent`);
    localStorage.removeItem(`${this.REFRESH_TOKEN_KEY}_persistent`);
  }

  // トークンの有効期限チェック
  isTokenExpired(token: string): boolean {
    try {
      const payload = this.getTokenPayload(token);
      if (!(payload.exp as number)) return true;
      
      const now = Math.floor(Date.now() / 1000);
      return (payload.exp as number) < now;
    } catch {
      return true;
    }
  }

  // トークンからユーザー情報を取得
  getUserFromToken(token: string): User | null {
    try {
      const payload = this.getTokenPayload(token);
      
      return {
        id: (payload.sub as string) || (payload.userId as string),
        email: payload.email as string,
        name: payload.name as string,
        role: (payload.role as 'user' | 'admin') || 'user',
        avatar: payload.avatar as string | undefined,
        permissions: (payload.permissions as string[]) || [],
        createdAt: (payload.createdAt as string) || new Date().toISOString(),
      };
    } catch {
      return null;
    }
  }

  // JWT ペイロードの取得
  private getTokenPayload(token: string): Record<string, unknown> {
    try {
      // JWT は base64url エンコードされているため、標準の base64 でデコード
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      
      // Unicode対応デコード
      const jsonPayload = this.base64DecodeUnicode(base64);

      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('JWT デコードエラー:', error);
      throw new Error('無効なトークン形式');
    }
  }

  // Unicode対応のBase64デコード関数
  private base64DecodeUnicode(str: string): string {
    try {
      return decodeURIComponent(atob(str).split('').map((c) => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
    } catch {
      throw new Error('Base64デコードに失敗しました');
    }
  }

  // Authorization ヘッダーの取得
  getAuthHeader(): { Authorization: string } | Record<string, never> {
    const token = this.getAccessToken();
    if (token && !this.isTokenExpired(token)) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }

  // トークンの自動リフレッシュが必要かチェック
  shouldRefreshToken(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const payload = this.getTokenPayload(token);
      if (!(payload.exp as number)) return true;

      const now = Math.floor(Date.now() / 1000);
      const expiresIn = (payload.exp as number) - now;
      
      // 5分以内に期限切れになる場合はリフレッシュ
      return expiresIn < 300;
    } catch {
      return true;
    }
  }
}

export const tokenService = new TokenService();