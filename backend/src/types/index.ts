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
  manualEvaluation?: ManualScoreEvaluation;
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

// チャートデータ関連
export interface ChartOHLCData {
  date: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartCurrentPrice {
  price: number;
  change: number;
  changeRate: number;
  volume: number;
}

export interface ChartPriceRange {
  min: number;
  max: number;
  period: string;
}

export interface ChartData {
  success: boolean;
  stockCode: string;
  symbol: string;
  stockName: string;
  timeframe: string;
  period: string;
  dataCount: number;
  lastUpdated: string;
  ohlcData: ChartOHLCData[];
  technicalIndicators: Record<string, unknown>;
  currentPrice: ChartCurrentPrice;
  priceRange: ChartPriceRange;
}

// 手動決済シグナル実行結果
export interface SignalExecutionResult {
  success: boolean;
  signalType: 'stop_loss' | 'take_profit';
  executedAt: string;
  message: string;
  affectedPositions?: number;
}

// 決済シグナル履歴関連
export interface SignalHistoryItem {
  id: string;
  signalType: 'stop_loss' | 'take_profit';
  stockCode?: string;
  reason?: string;
  status: 'pending' | 'executed' | 'failed';
  createdAt: string;
  executedAt?: string;
  affectedPositions?: number;
  executionResult?: Record<string, unknown>;
  errorMessage?: string;
}

export interface SignalHistoryResponse {
  success: boolean;
  signals: SignalHistoryItem[];
  total: number;
}

// 手動スコア評価関連
export type ManualScoreValue = 'S' | 'A+' | 'A' | 'B' | 'C';

export interface ManualScoreEvaluation {
  id: string;
  stockCode: string;
  stockName: string;
  score: ManualScoreValue;
  reason: string;
  evaluatedBy: string;
  evaluatedAt: string;
  logicType: 'logic_a' | 'logic_b';
  scanResultId?: string;
  aiScoreCalculating?: boolean;
}

export interface ScoreChangeHistory {
  id: string;
  stockCode: string;
  stockName: string;
  oldScore: ManualScoreValue | null;
  newScore: ManualScoreValue;
  changeReason: string;
  changedBy: string;
  changedAt: string;
  logicType: 'logic_a' | 'logic_b';
  scanResultId?: string;
}

export interface ScoreEvaluationRequest {
  stockCode: string;
  score: ManualScoreValue;
  reason: string;
  logicType: 'logic_a' | 'logic_b';
  scanResultId?: string;
}

export interface ScoreEvaluationFormData {
  selectedScore: ManualScoreValue | null;
  evaluationReason: string;
  isSubmitting: boolean;
}

export interface ScoreHistoryCompact {
  stockCode: string;
  items: ScoreChangeHistory[];
  maxDisplayCount: number;
}

// AI スコア計算状態
export interface AIScoreCalculationStatus {
  isCalculating: boolean;
  stockCode?: string;
  startedAt?: string;
  estimatedCompletion?: string;
}

// 🆕 決算スケジュール関連
export interface EarningsSchedule {
  id: string;
  stockCode: string;
  stockName: string;
  fiscalYear: number;
  fiscalQuarter: 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'FY';
  scheduledDate?: string;
  actualDate?: string;
  announcementTime?: 'pre_market' | 'after_market' | 'trading_hours';
  earningsStatus: 'scheduled' | 'announced' | 'delayed' | 'cancelled';
  revenueEstimate?: number;
  profitEstimate?: number;
  revenueActual?: number;
  profitActual?: number;
  profitPrevious?: number;
  isBlackInkConversion: boolean;
  forecastRevision?: Record<string, unknown>;
  earningsSummary?: string;
  dataSource: 'irbank' | 'kabutan' | 'manual' | 'api';
  lastUpdatedFromSource?: string;
  nextEarningsDate?: string;
  isTargetForLogicB: boolean;
  createdAt: string;
  updatedAt: string;
  metadataInfo?: Record<string, unknown>;
}

export interface EarningsScheduleFormData {
  stockCode: string;
  fiscalYear: number;
  fiscalQuarter: 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'FY';
  scheduledDate?: string;
  revenueEstimate?: number;
  profitEstimate?: number;
}

// 🆕 売買履歴関連
export interface TradingHistory {
  id: string;
  stockCode: string;
  stockName: string;
  tradeType: 'BUY' | 'SELL';
  logicType?: 'logic_a' | 'logic_b' | 'manual';
  entryPrice: number;
  exitPrice?: number;
  quantity: number;
  totalCost: number;
  commission: number;
  profitLoss?: number;
  profitLossRate?: number;
  holdingPeriod?: number;
  tradeDate: string;
  settlementDate?: string;
  orderMethod: 'market' | 'limit' | 'stop' | 'ifdoco';
  targetProfit?: number;
  stopLoss?: number;
  riskRewardRatio?: number;
  signalId?: string;
  scanResultId?: string;
  entryReason?: string;
  exitReason?: 'profit_target' | 'stop_loss' | 'manual' | 'time_limit';
  marketConditions?: Record<string, unknown>;
  performanceAnalysis?: Record<string, unknown>;
  status: 'open' | 'closed' | 'cancelled';
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface TradingHistoryFormData {
  stockCode: string;
  tradeType: 'BUY' | 'SELL';
  entryPrice: number;
  quantity: number;
  orderMethod: 'market' | 'limit' | 'stop' | 'ifdoco';
  targetProfit?: number;
  stopLoss?: number;
  entryReason?: string;
}

// 🆕 銘柄アーカイブ関連
export interface StockArchive {
  id: string;
  stockCode: string;
  stockName: string;
  logicType: 'logic_a' | 'logic_b';
  detectionDate: string;
  scanId: string;
  priceAtDetection: number;
  volumeAtDetection: number;
  marketCapAtDetection?: number;
  technicalSignalsSnapshot?: Record<string, unknown>;
  logicSpecificData?: Record<string, unknown>;
  performanceAfter1d?: number;
  performanceAfter1w?: number;
  performanceAfter1m?: number;
  maxGain?: number;
  maxLoss?: number;
  outcomeClassification?: 'success' | 'failure' | 'neutral' | 'pending';
  manualScore?: ManualScoreValue;
  manualScoreReason?: string;
  tradeExecution?: Record<string, unknown>;
  lessonsLearned?: string;
  marketConditionsSnapshot?: Record<string, unknown>;
  followUpNotes?: string;
  archiveStatus: 'active' | 'archived' | 'deleted';
  createdAt: string;
  updatedAt: string;
}

export interface ArchiveSearchRequest {
  stockCode?: string;
  logicType?: 'logic_a' | 'logic_b';
  dateFrom?: string;
  dateTo?: string;
  outcomeClassification?: 'success' | 'failure' | 'neutral' | 'pending';
  manualScore?: ManualScoreValue;
  page?: number;
  limit?: number;
}

export interface ArchiveSearchResponse {
  success: boolean;
  archives: StockArchive[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
}

// 🆕 拡張された手動スコア評価（データベース対応）
export interface ManualScoreWithHistory {
  id: string;
  stockCode: string;
  stockName: string;
  score: ManualScoreValue;
  logicType: 'logic_a' | 'logic_b';
  scanResultId?: string;
  evaluationReason: string;
  evaluatedBy: string;
  evaluatedAt: string;
  confidenceLevel?: 'high' | 'medium' | 'low';
  priceAtEvaluation?: number;
  marketContext?: Record<string, unknown>;
  aiScoreBefore?: ManualScoreValue;
  aiScoreAfter?: ManualScoreValue;
  scoreChangeHistory?: Record<string, unknown>;
  followUpRequired: boolean;
  followUpDate?: string;
  performanceValidation?: Record<string, unknown>;
  tags?: string[];
  isLearningCase: boolean;
  status: 'active' | 'archived' | 'superseded';
  createdAt: string;
  updatedAt: string;
}

// 🆕 Discord通知設定関連
export interface DiscordConfig {
  id: number;
  webhookUrl?: string;
  isEnabled: boolean;
  channelName?: string;
  serverName?: string;
  notificationTypes: string[];
  mentionRole?: string;
  notificationFormat: 'standard' | 'compact' | 'detailed';
  rateLimitPerHour: number;
  lastNotificationAt?: string;
  notificationCountToday: number;
  totalNotificationsSent: number;
  errorCount: number;
  lastErrorMessage?: string;
  lastErrorAt?: string;
  connectionStatus: 'connected' | 'disconnected' | 'error';
  webhookTestResult?: Record<string, unknown>;
  customMessageTemplate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DiscordConfigFormData {
  webhookUrl: string;
  channelName: string;
  serverName: string;
  notificationTypes: string[];
  mentionRole?: string;
  notificationFormat: 'standard' | 'compact' | 'detailed';
  customMessageTemplate?: string;
}

export interface DiscordNotificationTest {
  success: boolean;
  message?: string;
  error?: string;
  response?: Record<string, unknown>;
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
    DISCORD_CONFIG: '/api/notifications/discord',
    DISCORD_TEST: '/api/notifications/discord/test',
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
    DATA: (stockCode: string) => `/api/charts/data/${stockCode}`,
  },
  SCORES: {
    CREATE_EVALUATION: '/api/scores/evaluate',
    GET_EVALUATION: (stockCode: string) => `/api/scores/${stockCode}`,
    UPDATE_EVALUATION: (id: string) => `/api/scores/${id}`,
    GET_HISTORY: (stockCode: string) => `/api/scores/${stockCode}/history`,
    GET_HISTORY_COMPACT: (stockCode: string) => `/api/scores/${stockCode}/history/compact`,
    AI_CALCULATION_STATUS: (stockCode: string) => `/api/scores/${stockCode}/ai-status`,
  },
  ARCHIVE: {
    SEARCH: '/api/archive/search',
    GET_BY_ID: (id: string) => `/api/archive/${id}`,
    UPDATE: (id: string) => `/api/archive/${id}`,
    DELETE: (id: string) => `/api/archive/${id}`,
  },
  EARNINGS: {
    LIST: '/api/earnings',
    GET_BY_STOCK: (stockCode: string) => `/api/earnings/${stockCode}`,
    CREATE: '/api/earnings',
    UPDATE: (id: string) => `/api/earnings/${id}`,
  },
  TRADING: {
    HISTORY: '/api/trading/history',
    CREATE: '/api/trading',
    GET_BY_ID: (id: string) => `/api/trading/${id}`,
    UPDATE: (id: string) => `/api/trading/${id}`,
    PERFORMANCE: '/api/trading/performance',
  },
} as const;