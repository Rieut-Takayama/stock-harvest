import React, { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthContextType } from './AuthContextTypes';
import type { User, LoginCredentials } from '../types';
import { authService } from '../services/authService';
import { tokenService } from '../services/tokenService';
import { AuthContext } from './AuthContextDefinition';



interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初期化時に保存済み認証情報を確認
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = tokenService.getAccessToken();
        if (token && !tokenService.isTokenExpired(token)) {
          // 有効なトークンがある場合はユーザー情報を復元
          const userData = tokenService.getUserFromToken(token);
          if (userData) {
            setUser(userData);
          }
        }
      } catch (error) {
        console.error('認証初期化エラー:', error);
        tokenService.clearTokens();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 複数タブ間の認証状態同期
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'accessToken') {
        if (!e.newValue) {
          // トークンが削除された場合はログアウト
          setUser(null);
        } else {
          // 新しいトークンの場合はユーザー情報を更新
          const userData = tokenService.getUserFromToken(e.newValue);
          setUser(userData);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setLoading(true);
      const response = await authService.login(credentials);
      
      // トークンを保存
      tokenService.setTokens({
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      });

      // Remember Me が有効な場合は永続化
      if (credentials.rememberMe) {
        tokenService.setPersistentTokens({
          accessToken: response.accessToken,
          refreshToken: response.refreshToken,
        });
      }

      setUser(response.user);
    } catch (error) {
      console.error('ログインエラー:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = (): void => {
    try {
      // トークンをクリア
      tokenService.clearTokens();
      setUser(null);
      
      // 無効化APIを呼び出し
      authService.logout().catch(console.error);
    } catch (error) {
      console.error('ログアウトエラー:', error);
    }
  };

  const refreshAuth = async (): Promise<void> => {
    try {
      const refreshToken = tokenService.getRefreshToken();
      if (!refreshToken) {
        throw new Error('リフレッシュトークンがありません');
      }

      const response = await authService.refreshToken(refreshToken);
      
      tokenService.setTokens({
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      });

      setUser(response.user);
    } catch (error) {
      console.error('認証更新エラー:', error);
      logout();
      throw error;
    }
  };

  const hasPermission = (permission: string): boolean => {
    return user?.permissions.includes(permission) || false;
  };

  const hasRole = (role: string): boolean => {
    return user?.role === role;
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    refreshAuth,
    isAuthenticated: !!user,
    hasPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

