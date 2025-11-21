import { useState, useEffect, useCallback } from 'react';
import { SignalsApiService } from '../services/api/signalsService';
import { ChartsApiService } from '../services/api/chartsService';
import { ScanApiService } from '../services/api/scanService';
import type {
  ScanStatus,
  LogicDetectionStatus,
  ManualSignalRequest,
  SignalExecutionResult,
  ChartDisplayConfig
} from '../types';

// 実API接続用サービス
const signalsApi = new SignalsApiService();
const chartsApi = new ChartsApiService();
const scanApi = new ScanApiService();

export const useDashboardData = () => {
  // 認証なし個人利用版 - 初期状態を即座に設定
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>({
    isScanning: false,
    lastScanAt: '未実行',
    statusMessage: 'スキャン待機中'
  });
  const [logicStatus, setLogicStatus] = useState<LogicDetectionStatus[]>([
    {
      logicType: 'logic_a',
      name: 'ストップ高張り付き銘柄',
      isActive: true,
      detectedStocks: [],
      status: 'completed'
    },
    {
      logicType: 'logic_b',
      name: '赤字→黒字転換銘柄',
      isActive: true,
      detectedStocks: [],
      status: 'completed'
    }
  ]);
  const [loading] = useState(false); // 即座にfalseに設定
  const [error, setError] = useState<Error | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);

  const fetchInitialData = useCallback(async () => {
    try {
      // Fetching data from API
      
      // スキャン状況を取得
      const status = await scanApi.getScanStatus();
      // Scan status fetched successfully
      setScanStatus(status);
      
      // ロジック検出結果を取得
      const logicResults = await scanApi.getLogicDetectionStatus();
      // Logic results fetched successfully
      setLogicStatus(logicResults);
      
    } catch (err) {
      // Initial data fetch error handled
      console.error('Initial data fetch error:', {
        name: (err as Error).name,
        message: (err as Error).message,
        stack: (err as Error).stack
      });
      setError(err as Error);
    }
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const executeScan = useCallback(async () => {
    let progressInterval: ReturnType<typeof setInterval> | null = null;
    try {
      setIsScanning(true);
      setScanProgress(0);
      setError(null);

      // 実際のAPIでスキャンを実行
      const scanResult = await scanApi.executeScan();
      
      // スキャン進捗をポーリングで監視
      progressInterval = setInterval(async () => {
        try {
          const status = await scanApi.getScanStatus();
          setScanStatus(status);
          
          if (status.isScanning) {
            // スキャン中の場合は進捗を更新
            setScanProgress(Math.min(90, scanProgress + 10));
          } else {
            // スキャン完了の場合は結果を更新
            clearInterval(progressInterval!);
            setScanProgress(100);
            
            // 最新の結果を取得
            const logicResults = await scanApi.getLogicDetectionStatus();
            setLogicStatus(logicResults);
            
            setTimeout(() => {
              setIsScanning(false);
              setScanProgress(0);
            }, 1000);
          }
        } catch (err) {
          // Progress monitoring error handled
        }
      }, 2000);

      return scanResult;
    } catch (err) {
      setError(err as Error);
      if (progressInterval) clearInterval(progressInterval);
      setIsScanning(false);
      throw err;
    }
  }, [scanProgress]);

  const executeManualSignal = useCallback(async (request: ManualSignalRequest): Promise<SignalExecutionResult> => {
    try {
      setError(null);
      const result = await signalsApi.executeManualSignal(request);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, []);

  const showChart = useCallback(async (stockCode: string) => {
    try {
      const config: ChartDisplayConfig = {
        stockCode,
        timeframe: '1d',
        indicators: ['rsi', 'macd']
      };
      const chartData = await chartsApi.getChartData(stockCode, config);
      return chartData;
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, []);

  return {
    scanStatus,
    logicStatus,
    loading,
    error,
    isScanning,
    scanProgress,
    executeScan,
    executeManualSignal,
    showChart,
    refetch: fetchInitialData
  };
};
