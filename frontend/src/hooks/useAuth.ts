import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContextDefinition';
import type { AuthContextType } from '../contexts/AuthContextTypes';

// カスタムフック - AuthProviderからコンテキストを取得
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth は AuthProvider 内で使用する必要があります');
  }
  return context;
};