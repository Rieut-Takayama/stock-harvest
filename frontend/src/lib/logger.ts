/**
 * Logger utility for Stock Harvest AI
 * 開発時のみ出力、本番では無効化される
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  data?: Record<string, unknown>;
  timestamp: string;
}

class Logger {
  private isDevelopment = import.meta.env.DEV;
  private context = 'StockHarvestAI';

  private log(level: LogLevel, message: string, data?: Record<string, unknown>): void {
    if (!this.isDevelopment) return;

    const entry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString()
    };

    const prefix = `[${this.context}] ${entry.timestamp}`;
    const formattedMessage = `${prefix} ${level.toUpperCase()}: ${message}`;

    switch (level) {
      case 'debug':
         
        console.debug(formattedMessage, data || '');
        break;
      case 'info':
         
        console.info(formattedMessage, data || '');
        break;
      case 'warn':
         
        console.warn(formattedMessage, data || '');
        break;
      case 'error':
         
        console.error(formattedMessage, data || '');
        break;
      default:
         
        console.log(formattedMessage, data || '');
    }
  }

  debug(message: string, data?: Record<string, unknown>): void {
    this.log('debug', message, data);
  }

  info(message: string, data?: Record<string, unknown>): void {
    this.log('info', message, data);
  }

  warn(message: string, data?: Record<string, unknown>): void {
    this.log('warn', message, data);
  }

  error(message: string, data?: Record<string, unknown>): void {
    this.log('error', message, data);
  }

  // エラーオブジェクトからメッセージとスタックトレースを抽出
  logError(error: Error, context?: string, data?: Record<string, unknown>): void {
    const errorData = {
      message: error.message,
      stack: error.stack,
      name: error.name,
      context,
      ...data
    };

    this.error(`Error occurred${context ? ` in ${context}` : ''}`, errorData);
  }

  // パフォーマンス測定開始
  time(label: string): void {
    if (!this.isDevelopment) return;
     
    console.time(`[${this.context}] ${label}`);
  }

  // パフォーマンス測定終了
  timeEnd(label: string): void {
    if (!this.isDevelopment) return;
     
    console.timeEnd(`[${this.context}] ${label}`);
  }

  // グループ化ログ開始
  group(label: string): void {
    if (!this.isDevelopment) return;
     
    console.group(`[${this.context}] ${label}`);
  }

  // グループ化ログ終了
  groupEnd(): void {
    if (!this.isDevelopment) return;
     
    console.groupEnd();
  }
}

// シングルトンインスタンスをエクスポート
export const logger = new Logger();

// 開発者向けヘルパー関数
export const createScopedLogger = (scope: string) => ({
  debug: (message: string, data?: Record<string, unknown>) => 
    logger.debug(`[${scope}] ${message}`, data),
  info: (message: string, data?: Record<string, unknown>) => 
    logger.info(`[${scope}] ${message}`, data),
  warn: (message: string, data?: Record<string, unknown>) => 
    logger.warn(`[${scope}] ${message}`, data),
  error: (message: string, data?: Record<string, unknown>) => 
    logger.error(`[${scope}] ${message}`, data),
});

export default logger;