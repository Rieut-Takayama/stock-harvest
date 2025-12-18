import { useState, useEffect, useCallback } from 'react';
import type { 
  ManualScoreEvaluation, 
  ScoreChangeHistory, 
  ScoreEvaluationRequest,
  ManualScoreValue,
  AIScoreCalculationStatus,
  ScoreEvaluationFormData
} from '@/types';
import { scoreEvaluationService } from '@/services/api/scoreEvaluationService';
import { logger } from '@/lib/logger';

const service = scoreEvaluationService;

export const useScoreEvaluation = (stockCode?: string) => {
  // 基本データ状態
  const [currentEvaluation, setCurrentEvaluation] = useState<ManualScoreEvaluation | null>(null);
  const [history, setHistory] = useState<ScoreChangeHistory[]>([]);
  const [aiCalculationStatus, setAiCalculationStatus] = useState<AIScoreCalculationStatus>({
    isCalculating: false
  });

  // 読み込み状態
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // フォーム状態
  const [formData, setFormData] = useState<ScoreEvaluationFormData>({
    selectedScore: null,
    evaluationReason: '',
    isSubmitting: false
  });

  // データ取得
  const fetchData = useCallback(async (targetStockCode: string) => {
    try {
      setLoading(true);
      setError(null);

      logger.debug('Fetching score evaluation data', { 
        stockCode: targetStockCode,
        hookName: 'useScoreEvaluation'
      });

      const [evaluation, historyData, aiStatus] = await Promise.all([
        service.getEvaluation(targetStockCode),
        service.getHistoryCompact(targetStockCode),
        service.getAICalculationStatus(targetStockCode)
      ]);

      setCurrentEvaluation(evaluation);
      setHistory(historyData);
      setAiCalculationStatus(aiStatus);

      logger.info('Score evaluation data fetched successfully', {
        stockCode: targetStockCode,
        hasEvaluation: !!evaluation,
        historyCount: historyData.length,
        isAICalculating: aiStatus.isCalculating
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Failed to fetch score evaluation data', {
        error: error.message,
        stockCode: targetStockCode
      });
      setError(error);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初期データ読み込み
  useEffect(() => {
    if (stockCode) {
      logger.debug('Hook mounted with stockCode', { 
        stockCode,
        hookName: 'useScoreEvaluation'
      });
      fetchData(stockCode);
    }
  }, [stockCode, fetchData]);

  // AI計算状態のポーリング
  useEffect(() => {
    if (!stockCode || !aiCalculationStatus.isCalculating) return;

    logger.debug('Starting AI calculation polling', { stockCode });

    const interval = setInterval(async () => {
      try {
        const status = await service.getAICalculationStatus(stockCode);
        setAiCalculationStatus(status);

        if (!status.isCalculating) {
          logger.info('AI calculation completed, stopping polling', { stockCode });
          clearInterval(interval);
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        logger.error('Failed to poll AI calculation status', {
          error: error.message,
          stockCode
        });
      }
    }, 1000);

    return () => {
      logger.debug('Clearing AI calculation polling', { stockCode });
      clearInterval(interval);
    };
  }, [stockCode, aiCalculationStatus.isCalculating]);

  // スコア評価の保存
  const saveEvaluation = async (
    targetStockCode: string, 
    score: ManualScoreValue, 
    reason: string,
    logicType: 'logic_a' | 'logic_b' = 'logic_a'
  ) => {
    try {
      setFormData(prev => ({ ...prev, isSubmitting: true }));

      logger.debug('Saving score evaluation', {
        stockCode: targetStockCode,
        score,
        logicType
      });

      const request: ScoreEvaluationRequest = {
        stockCode: targetStockCode,
        score,
        reason,
        logicType
      };

      const newEvaluation = await service.createEvaluation(request);
      setCurrentEvaluation(newEvaluation);

      // 履歴を更新
      if (stockCode === targetStockCode) {
        const updatedHistory = await service.getHistoryCompact(targetStockCode);
        setHistory(updatedHistory);
      }

      // フォームをリセット
      setFormData({
        selectedScore: null,
        evaluationReason: '',
        isSubmitting: false
      });

      logger.info('Score evaluation saved successfully', {
        stockCode: targetStockCode,
        score,
        evaluationId: newEvaluation.id
      });

      return newEvaluation;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Failed to save score evaluation', {
        error: error.message,
        stockCode: targetStockCode,
        score
      });

      setFormData(prev => ({ ...prev, isSubmitting: false }));
      throw error;
    }
  };

  // AI計算開始
  const startAICalculation = (targetStockCode: string) => {
    logger.debug('Starting AI calculation', { stockCode: targetStockCode });

    service.startAICalculation(targetStockCode);
    
    // 即座に計算中状態に変更
    setAiCalculationStatus({
      isCalculating: true,
      stockCode: targetStockCode,
      startedAt: new Date().toISOString(),
      estimatedCompletion: new Date(Date.now() + 3000).toISOString()
    });

    logger.info('AI calculation started', { stockCode: targetStockCode });
  };

  // フォーム状態の更新
  const updateFormData = (updates: Partial<ScoreEvaluationFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  // フォームリセット
  const resetForm = () => {
    setFormData({
      selectedScore: null,
      evaluationReason: '',
      isSubmitting: false
    });
    logger.debug('Score evaluation form reset');
  };

  // バリデーション
  const canSaveEvaluation = formData.selectedScore !== null && !formData.isSubmitting;

  return {
    // データ
    currentEvaluation,
    history,
    aiCalculationStatus,
    
    // 状態
    loading,
    error,
    
    // フォーム
    formData,
    canSaveEvaluation,
    
    // アクション
    fetchData,
    saveEvaluation,
    startAICalculation,
    updateFormData,
    resetForm,
    
    // ヘルパー
    refetch: () => stockCode ? fetchData(stockCode) : Promise.resolve()
  };
};