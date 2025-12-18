import type { Meta, StoryObj } from '@storybook/react';
import { LoginPage } from './LoginPage';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContextDefinition';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// QueryClientのセットアップ
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

// モックAuthContext
const mockAuthContext = {
  user: null,
  login: async () => { 
    console.log('Login function called'); 
  },
  logout: () => { 
    console.log('Logout function called'); 
  },
  refreshAuth: async () => {
    console.log('RefreshAuth function called');
  },
  isAuthenticated: false,
  loading: false,
  hasPermission: (permission: string) => {
    console.log('hasPermission called with:', permission);
    return false;
  },
  hasRole: (role: string) => {
    console.log('hasRole called with:', role);
    return false;
  },
};

const meta: Meta<typeof LoginPage> = {
  title: 'Pages/LoginPage',
  component: LoginPage,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'ログインページのコンポーネント。メール・パスワードでのログイン、デモアカウント機能を提供します。',
      },
    },
  },
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={mockAuthContext}>
          <MemoryRouter initialEntries={['/login']}>
            <Story />
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof LoginPage>;

// 基本表示
export const Default: Story = {
  parameters: {
    docs: {
      description: {
        story: 'ログインページの基本表示状態。メールアドレス・パスワード入力フィールドとデモアカウントボタンが表示されます。',
      },
    },
  },
};

// エラー状態
export const WithError: Story = {
  decorators: [
    (Story) => {
      // エラー状態を再現するため、loginが失敗するモックを作成
      const errorAuthContext = {
        ...mockAuthContext,
        login: async () => {
          throw new Error('Login failed');
        },
        refreshAuth: async () => {
          console.log('RefreshAuth function called');
        },
        hasPermission: (permission: string) => {
          console.log('hasPermission called with:', permission);
          return false;
        },
        hasRole: (role: string) => {
          console.log('hasRole called with:', role);
          return false;
        },
      };

      return (
        <QueryClientProvider client={queryClient}>
          <AuthContext.Provider value={errorAuthContext}>
            <MemoryRouter initialEntries={['/login']}>
              <Story />
            </MemoryRouter>
          </AuthContext.Provider>
        </QueryClientProvider>
      );
    },
  ],
  parameters: {
    docs: {
      description: {
        story: 'ログインエラー時の表示状態。エラーメッセージが画面上部に赤色で表示されます。',
      },
    },
  },
};

// ローディング状態
export const Loading: Story = {
  decorators: [
    (Story) => {
      const loadingAuthContext = {
        ...mockAuthContext,
        loading: true,
        login: async () => {
          // ローディング状態を長時間保持するため、Promiseを解決しない
          return new Promise<void>(() => {});
        },
        refreshAuth: async () => {
          console.log('RefreshAuth function called');
        },
        hasPermission: (permission: string) => {
          console.log('hasPermission called with:', permission);
          return false;
        },
        hasRole: (role: string) => {
          console.log('hasRole called with:', role);
          return false;
        },
      };

      return (
        <QueryClientProvider client={queryClient}>
          <AuthContext.Provider value={loadingAuthContext}>
            <MemoryRouter initialEntries={['/login']}>
              <Story />
            </MemoryRouter>
          </AuthContext.Provider>
        </QueryClientProvider>
      );
    },
  ],
  parameters: {
    docs: {
      description: {
        story: 'ログイン処理中の状態。ログインボタンが「ログイン中...」の表示に変わり、無効化されます。',
      },
    },
  },
};