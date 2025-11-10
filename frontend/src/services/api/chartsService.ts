// charts API サービス
import type { ChartData, ChartDisplayConfig } from '../../types';

const API_BASE_URL = 'http://localhost:8432';

export class ChartsApiService {
  private async makeRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Chart API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
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
      
      console.log(`Chart data fetched for ${stockCode}:`, {
        stockName: result.stockName,
        dataCount: result.dataCount,
        timeframe: result.timeframe,
        period: result.period
      });
      
      return result;
    } catch (error) {
      console.error(`Failed to fetch chart data for ${stockCode}:`, error);
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
      console.error('Charts health check failed:', error);
      throw new Error(`Charts health check failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}