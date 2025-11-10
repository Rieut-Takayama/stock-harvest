import type { 
  ScanResult,
  ScanStatus,
  LogicDetectionStatus
} from '../../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8432';

export class ScanApiService {
  /**
   * 全銘柄スキャンを実行
   */
  async executeScan(): Promise<ScanResult> {
    try {
      const response = await fetch(`${API_BASE}/api/scan/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logicA: true,
          logicB: true
        })
      });

      if (!response.ok) {
        throw new Error(`スキャン実行に失敗しました: ${response.status}`);
      }

      const data = await response.json();
      
      // バックエンドAPIのレスポンスをフロントエンド型に変換
      return {
        id: data.scanId,
        executedAt: new Date().toISOString(),
        totalStocks: 0, // 実際の値は後でスキャン結果から取得
        detectedStocks: 0, // 実際の値は後でスキャン結果から取得
        scanConditions: {
          logicA: true,
          logicB: true,
          volumeThreshold: 1000000,
          priceChangeThreshold: 2.0
        },
        topStocks: [], // 実際の値は後でスキャン結果から取得
        logicAResults: {
          enabled: true,
          detectedCount: 0,
          stocks: []
        },
        logicBResults: {
          enabled: true,
          detectedCount: 0,
          stocks: []
        }
      };
    } catch (error) {
      console.error('スキャン実行エラー:', error);
      throw error;
    }
  }

  /**
   * スキャン状況を取得
   */
  async getScanStatus(): Promise<ScanStatus> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8秒タイムアウト
      
      const response = await fetch(`${API_BASE}/api/scan/status`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`スキャン状況取得に失敗しました: ${response.status}`);
      }

      const data = await response.json();
      
      // バックエンドAPIのレスポンスをフロントエンド型に変換
      return {
        isScanning: data.isRunning,
        lastScanAt: '', // バックエンドから提供されない場合は空文字
        statusMessage: data.message
      };
    } catch (error) {
      console.error('スキャン状況取得エラー:', error);
      throw error;
    }
  }

  /**
   * ロジック検出状況を取得
   */
  async getLogicDetectionStatus(): Promise<LogicDetectionStatus[]> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8秒タイムアウト
      
      const response = await fetch(`${API_BASE}/api/scan/results`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`スキャン結果取得に失敗しました: ${response.status}`);
      }

      const data = await response.json();
      
      // バックエンドAPIのレスポンスをフロントエンド型に変換
      return [
        {
          logicType: 'logic_a',
          name: 'ストップ高張り付き銘柄',
          isActive: true,
          detectedStocks: data.logicA?.stocks?.map((stock: { code: string; name: string; price: number; change: number; changeRate: number; volume: number }) => ({
            code: stock.code,
            name: stock.name,
            price: stock.price,
            change: stock.change,
            changeRate: stock.changeRate,
            volume: stock.volume,
            signals: {
              rsi: 0, // バックエンドから提供されない場合のデフォルト値
              macd: 0,
              bollingerPosition: 0,
              volumeRatio: 0,
              trendDirection: 'up' as const
            }
          })) || [],
          status: 'completed' as const
        },
        {
          logicType: 'logic_b',
          name: '赤字→黒字転換銘柄',
          isActive: true,
          detectedStocks: data.logicB?.stocks?.map((stock: { code: string; name: string; price: number; change: number; changeRate: number; volume: number }) => ({
            code: stock.code,
            name: stock.name,
            price: stock.price,
            change: stock.change,
            changeRate: stock.changeRate,
            volume: stock.volume,
            signals: {
              rsi: 0, // バックエンドから提供されない場合のデフォルト値
              macd: 0,
              bollingerPosition: 0,
              volumeRatio: 0,
              trendDirection: 'up' as const
            }
          })) || [],
          status: 'completed' as const
        }
      ];
    } catch (error) {
      console.error('ロジック検出状況取得エラー:', error);
      throw error;
    }
  }
}