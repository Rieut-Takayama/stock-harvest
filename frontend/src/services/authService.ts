import axios from 'axios';
import type { AuthResponse, LoginCredentials, User } from '../types';

// 本番用認証サービス
class AuthService {
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8432/api';
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/auth/login`, credentials);
      return response.data;
    } catch {
      // ログインサービスエラー時のエラーメッセージを統一
      throw new Error('ログインに失敗しました');
    }
  }

  async logout(): Promise<void> {
    try {
      await axios.post(`${this.baseURL}/auth/logout`);
    } catch {
      // ログアウトエラーは無視して継続
    }
  }

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${this.baseURL}/auth/refresh`, {
        refreshToken,
      });
      return response.data;
    } catch {
      // トークンリフレッシュエラー時のエラーメッセージを統一
      throw new Error('認証の更新に失敗しました');
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await axios.get(`${this.baseURL}/auth/me`);
      return response.data;
    } catch {
      // ユーザー情報取得エラー時のエラーメッセージを統一
      throw new Error('ユーザー情報の取得に失敗しました');
    }
  }
}


export const authService = new AuthService();