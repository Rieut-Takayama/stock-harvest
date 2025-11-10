// Stock Harvest AI - 型定義
// バックエンドとの同期必須: src/types/index.ts

// ユーザー・認証関連
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  avatar?: string;
  permissions: string[];
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

// 株価・銘柄関連
export interface StockData {
  code: string;
  name: string;
  price: number;
  change: number;
  changeRate: number;
  volume: number;
  marketCap?: number;
  signals: TechnicalSignals;
}

export interface TechnicalSignals {
  rsi: number;
  macd: number;
  bollingerPosition: number;
  volumeRatio: number;
  trendDirection: 'up' | 'down' | 'sideways';
}

// スキャン結果関連
export interface ScanResult {
  id: string;
  executedAt: string;
  totalStocks: number;
  detectedStocks: number;
  scanConditions: ScanConditions;
  topStocks: StockData[];
  logicAResults: LogicResult;
  logicBResults: LogicResult;
}

export interface ScanConditions {
  logicA: boolean; // ストップ高張り付き
  logicB: boolean; // 赤字→黒字転換
  volumeThreshold: number;
  priceChangeThreshold: number;
}

export interface LogicResult {
  enabled: boolean;
  detectedCount: number;
  stocks: StockData[];
}

// アラート関連
export type AlertType = 'price' | 'logic';

export interface Alert {
  id: string;
  stockCode: string;
  stockName: string;
  type: AlertType;
  condition: AlertCondition;
  isActive: boolean;
  createdAt: string;
  lineNotificationEnabled: boolean;
}

export interface AlertCondition {
  // 価格到達アラートの場合
  targetPrice?: number;
  priceDirection?: 'above' | 'below';
  // ロジック発動アラートの場合
  logic?: 'logic_a' | 'logic_b';
  logicName?: string;
}

export interface AlertFormData {
  alertType: AlertType;
  stockCode: string;
  targetPrice?: number;
}

export interface LineNotificationConfig {
  isConnected: boolean;
  token?: string;
  status: 'connected' | 'disconnected' | 'error';
  lastNotificationAt?: string;
}

// ポートフォリオ関連（将来用）
export interface PortfolioItem {
  id: string;
  stockCode: string;
  stockName: string;
  quantity: number;
  purchasePrice: number;
  currentPrice: number;
  targetPrice: number;
  stopLossPrice: number;
  purchaseDate: string;
}

// API応答関連
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
}

// 問合せ関連
export interface ContactForm {
  type: 'technical' | 'feature' | 'bug' | 'other';
  subject: string;
  content: string;
  email: string;
  priority: 'low' | 'medium' | 'high';
}

export interface FAQ {
  id: string;
  category: string;
  question: string;
  answer: string;
  tags: string[];
}

// システム情報
export interface SystemInfo {
  version: string;
  status: 'healthy' | 'degraded' | 'down';
  lastScanAt: string;
  activeAlerts: number;
  totalUsers: number;
  databaseStatus: 'connected' | 'disconnected';
  lastUpdated: string;
  statusDisplay: string;
}

// ロジックスキャナーダッシュボード関連
export interface ScanStatus {
  isScanning: boolean;
  lastScanAt: string;
  scanProgress?: number;
  statusMessage: string;
}

export interface LogicDetectionStatus {
  logicType: 'logic_a' | 'logic_b';
  name: string;
  isActive: boolean;
  detectedStocks: StockData[];
  status: 'detecting' | 'completed' | 'error';
}

export interface ManualSignalRequest {
  type: 'stop_loss' | 'take_profit';
  stockCode?: string;
  reason?: string;
  timestamp: string;
}

export interface ChartDisplayConfig {
  stockCode: string;
  timeframe: '1d' | '1w' | '1m' | '3m';
  indicators: string[];
}

// 手動決済シグナル実行結果
export interface SignalExecutionResult {
  success: boolean;
  signalType: 'stop_loss' | 'take_profit';
  executedAt: string;
  message: string;
  affectedPositions?: number;
}

// APIパス定数
export const API_PATHS = {
  ALERTS: {
    LIST: '/api/alerts',
    CREATE: '/api/alerts',
    UPDATE: (id: string) => `/api/alerts/${id}`,
    DELETE: (id: string) => `/api/alerts/${id}`,
    TOGGLE: (id: string) => `/api/alerts/${id}/toggle`,
  },
  NOTIFICATIONS: {
    LINE_CONFIG: '/api/notifications/line',
    LINE_CONNECT: '/api/notifications/line/connect',
    LINE_STATUS: '/api/notifications/line/status',
  },
  CONTACT: {
    SUBMIT: '/api/contact/submit',
    FAQ: '/api/contact/faq',
  },
  SYSTEM: {
    INFO: '/api/system/info',
    STATUS: '/api/system/status',
  },
  SCAN: {
    EXECUTE: '/api/scan/execute',
    STATUS: '/api/scan/status',
    RESULTS: '/api/scan/results',
  },
  SIGNALS: {
    MANUAL_EXECUTE: '/api/signals/manual-execute',
    HISTORY: '/api/signals/history',
  },
  CHARTS: {
    DATA: (stockCode: string) => `/api/charts/${stockCode}`,
  },
} as const;