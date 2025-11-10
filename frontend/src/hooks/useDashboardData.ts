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
    // 認証なし個人利用版 - APIアクセスなし、デモデータのみ使用
    console.log('認証なし個人利用版 - デモデータを使用');
    // 何もしない - 初期値のままでOK
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

      // スキャン進行のシミュレート
      progressInterval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 90) {
            if (progressInterval) clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      // スキャン実行
      const scanResult = await scanApi.executeScan();
      
      if (progressInterval) clearInterval(progressInterval);
      setScanProgress(100);
      
      // スキャン結果を反映
      setScanStatus({
        isScanning: false,
        lastScanAt: scanResult.executedAt,
        statusMessage: 'スキャン完了'
      });

      // ロジック状態を更新
      setLogicStatus([
        {
          logicType: 'logic_a',
          name: 'ストップ高張り付き銘柄',
          isActive: true,
          detectedStocks: scanResult.logicAResults.stocks,
          status: 'completed'
        },
        {
          logicType: 'logic_b',
          name: '赤字→黒字転換銘柄',
          isActive: true,
          detectedStocks: scanResult.logicBResults.stocks,
          status: 'completed'
        }
      ]);

      return scanResult;
    } catch (err) {
      setError(err as Error);
      if (progressInterval) clearInterval(progressInterval);
      throw err;
    } finally {
      setTimeout(() => {
        setIsScanning(false);
        setScanProgress(0);
      }, 1000);
    }
  }, []);

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
