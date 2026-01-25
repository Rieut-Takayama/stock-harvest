// charts API サービス
import type { ChartData, ChartDisplayConfig } from '../../types';
import { logger } from '@/lib/logger';
import { API_BASE_URL } from '@/config/api';

export class ChartsApiService {
  private async makeRequest<T>(url: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('Charts API Error:', { method: 'makeRequest', url, error: errorMessage });
      throw new Error(`[ChartsService] ${errorMessage}`);
    }
  }

  /**
   * 指定した銘柄のチャートデータを取得
   * @param stockCode 銘柄コード (例: '7203')
   * @param config チャート設定 (オプション)
   * @returns チャートデータ
   */
  async getChartData(stockCode: string, config?: Partial<ChartDisplayConfig>): Promise<ChartData> {
    try {
      // API_PATHSを直接使用せずにエンドポイントを構築
      const endpoint = `/api/charts/data/${stockCode}`;
      
      // クエリパラメータを構築
      const queryParams = new URLSearchParams();
      if (config?.timeframe) {
        queryParams.append('timeframe', config.timeframe);
      }
      if (config?.indicators && config.indicators.length > 0) {
        queryParams.append('indicators', config.indicators.join(','));
      }
      
      const url = queryParams.toString() ? `${endpoint}?${queryParams.toString()}` : endpoint;
      
      const result = await this.makeRequest<ChartData>(url);
      
      // Chart data fetched successfully
      
      return result;
    } catch (error) {
      throw new Error(`Failed to fetch chart data for ${stockCode}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * チャート機能のヘルスチェック
   * @returns ヘルスチェック結果
   */
  async getChartsHealth(): Promise<{ status: string; service: string; details: Record<string, unknown> }> {
    try {
      const result = await this.makeRequest<{ status: string; service: string; details: Record<string, unknown> }>('/api/charts/health');
      return result;
    } catch (error) {
      throw new Error(`Charts health check failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}