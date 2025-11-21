/**
 * 手動決済シグナルAPIサービス
 * Stock Harvest AI プロジェクト
 * 
 * バックエンドの手動決済シグナル機能との統合
 */

import type { 
  ManualSignalRequest, 
  SignalExecutionResult 
} from '../../types';
import { API_PATHS } from '../../types';

export class SignalsApiService {
  private readonly baseUrl: string;

  constructor() {
    this.baseUrl = 'http://localhost:8432';
  }

  /**
   * 手動決済シグナル実行
   */
  async executeManualSignal(request: ManualSignalRequest): Promise<SignalExecutionResult> {
    try {
      const response = await fetch(`${this.baseUrl}${API_PATHS.SIGNALS.MANUAL_EXECUTE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: request.type,
          stockCode: request.stockCode,
          reason: request.reason
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      
      // バックエンドのレスポンス形式をフロントエンドの型に変換
      return {
        success: data.success,
        signalType: request.type,
        executedAt: data.executedAt,
        message: data.message,
        affectedPositions: data.affectedPositions
      };
    } catch (error) {
      // Manual close signal error handled
      throw error;
    }
  }

  /**
   * ヘルスチェック用 - 手動決済API機能が利用可能かチェック
   */
  async checkHealth(): Promise<boolean> {
    try {
      // テスト用の無効なリクエストを送信して、APIが応答するかチェック
      const response = await fetch(`${this.baseUrl}${API_PATHS.SIGNALS.MANUAL_EXECUTE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type: 'health_check' })
      });
      
      // 400エラー（バリデーションエラー）が返ってくればAPIは生きている
      return response.status === 400 || response.ok;
    } catch (error) {
      // Manual close API health check error handled
      return false;
    }
  }
}