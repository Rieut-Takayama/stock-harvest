import type { 
  ManualScoreEvaluation, 
  ScoreChangeHistory, 
  ScoreEvaluationRequest,
  ManualScoreValue,
  AIScoreCalculationStatus
} from '@/types';
import { logger } from '@/lib/logger';

const API_BASE_URL = 'http://localhost:8432';

export class ScoreEvaluationService {
  /**
   * スコア評価を作成
   */
  async createEvaluation(request: ScoreEvaluationRequest): Promise<ManualScoreEvaluation> {
    logger.debug('Creating score evaluation via API', { 
      stockCode: request.stockCode,
      score: request.score,
      logicType: request.logicType
    });

    try {
      const response = await fetch(`${API_BASE_URL}/api/scores/manual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stock_code: request.stockCode,
          stock_name: this.getStockName(request.stockCode), // 必須フィールド
          score: request.score,
          evaluation_reason: request.reason, // フィールド名修正
          logic_type: request.logicType,
          scan_result_id: request.scanResultId
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        evaluation: ManualScoreEvaluation;
      };

      if (!data.success || !data.evaluation) {
        throw new Error('Invalid API response format');
      }

      logger.info('Score evaluation created successfully via API', { 
        evaluationId: data.evaluation.id,
        stockCode: request.stockCode,
        score: request.score
      });

      return data.evaluation;
    } catch (error) {
      logger.error('Failed to create score evaluation via API', { 
        error,
        request
      });
      throw error;
    }
  }

  /**
   * スコア評価を取得
   */
  async getEvaluation(stockCode: string, logicType?: string): Promise<ManualScoreEvaluation | null> {
    logger.debug('Fetching score evaluation via API', { stockCode, logicType });

    try {
      let url = `${API_BASE_URL}/api/scores/${stockCode}`;
      if (logicType) {
        url += `?logic_type=${encodeURIComponent(logicType)}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          logger.debug('Score evaluation not found (404)', { stockCode });
          return null;
        }
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        evaluation?: ManualScoreEvaluation;
      };

      if (!data.success) {
        logger.warn('API response indicates failure', { stockCode, response: data });
        return null;
      }

      logger.info('Score evaluation fetched via API', { 
        stockCode,
        found: !!data.evaluation
      });

      return data.evaluation || null;
    } catch (error) {
      logger.error('Failed to fetch score evaluation via API', { 
        error,
        stockCode
      });
      throw error;
    }
  }

  /**
   * スコア履歴を取得
   */
  async getHistory(stockCode: string): Promise<ScoreChangeHistory[]> {
    logger.debug('Fetching score history via API', { stockCode });

    try {
      const response = await fetch(`${API_BASE_URL}/api/scores/history/${stockCode}?compact=false`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        history: ScoreChangeHistory[];
      };

      if (!data.success) {
        throw new Error('API response indicates failure');
      }

      const history = data.history || [];

      logger.info('Score history fetched via API', { 
        stockCode,
        count: history.length
      });

      return history;
    } catch (error) {
      logger.error('Failed to fetch score history via API', { 
        error,
        stockCode
      });
      throw error;
    }
  }

  /**
   * コンパクトなスコア履歴を取得（最新5件）
   */
  async getHistoryCompact(stockCode: string): Promise<ScoreChangeHistory[]> {
    logger.debug('Fetching compact score history via API', { stockCode });

    try {
      const response = await fetch(`${API_BASE_URL}/api/scores/history/${stockCode}?compact=true`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        history: ScoreChangeHistory[];
      };

      if (!data.success) {
        throw new Error('API response indicates failure');
      }

      const history = data.history || [];

      logger.info('Compact score history fetched via API', { 
        stockCode,
        count: history.length
      });

      return history;
    } catch (error) {
      logger.error('Failed to fetch compact score history via API', { 
        error,
        stockCode
      });
      throw error;
    }
  }

  /**
   * AI計算状態を取得
   */
  async getAICalculationStatus(stockCode: string): Promise<AIScoreCalculationStatus> {
    logger.debug('Fetching AI calculation status via API', { stockCode });

    try {
      const response = await fetch(`${API_BASE_URL}/api/scores/ai-status/${stockCode}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          // ステータスが存在しない場合はデフォルト値を返す
          const defaultStatus: AIScoreCalculationStatus = {
            isCalculating: false,
            stockCode,
            startedAt: undefined,
            estimatedCompletion: undefined
          };

          logger.debug('AI calculation status not found (404), returning default', { stockCode });
          return defaultStatus;
        }
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        status: AIScoreCalculationStatus;
      };

      if (!data.success || !data.status) {
        // ステータスが存在しない場合はデフォルト値を返す
        const defaultStatus: AIScoreCalculationStatus = {
          isCalculating: false,
          stockCode,
          startedAt: undefined,
          estimatedCompletion: undefined
        };

        logger.debug('AI calculation status not found, returning default', { stockCode });
        return defaultStatus;
      }

      logger.info('AI calculation status fetched via API', { 
        stockCode,
        isCalculating: data.status.isCalculating
      });

      return data.status;
    } catch (error) {
      logger.error('Failed to fetch AI calculation status via API', { 
        error,
        stockCode
      });
      throw error;
    }
  }

  /**
   * AI計算を開始
   * 注意: 実際のAI計算開始APIは別途実装される予定
   */
  startAICalculation(stockCode: string): void {
    logger.debug('Starting AI calculation', { stockCode });

    // この実装は暫定的なもので、実際のAI計算APIが実装されたら置き換える
    logger.warn('AI calculation start is placeholder implementation - replace with actual API', { 
      stockCode,
      action: 'startAICalculation'
    });

    logger.info('AI calculation started', { stockCode });
  }

  /**
   * ヘルパーメソッド: 銘柄名の取得
   */
  private getStockName(stockCode: string): string {
    const stockNames: Record<string, string> = {
      '1234': 'テクノロジー株式会社',
      '5678': 'グロース企業',
      '9012': '新興IT企業'
    };

    return stockNames[stockCode] || `銘柄${stockCode}`;
  }

  /**
   * スコア評価統計を取得
   */
  async getEvaluationStatistics() {
    logger.debug('Fetching evaluation statistics via API');

    try {
      const response = await fetch(`${API_BASE_URL}/api/scores/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as {
        success: boolean;
        statistics: {
          total_evaluations: number;
          score_distribution: Record<ManualScoreValue, number>;
          recent_activity: number;
          logic_type_breakdown: Record<string, number>;
        };
      };

      if (!data.success) {
        throw new Error('API response indicates failure');
      }

      logger.info('Evaluation statistics fetched via API', { 
        totalEvaluations: data.statistics?.total_evaluations || 0
      });

      return data.statistics;
    } catch (error) {
      logger.error('Failed to fetch evaluation statistics via API', { error });
      throw error;
    }
  }
}

// シングルトンインスタンスをエクスポート
export const scoreEvaluationService = new ScoreEvaluationService();