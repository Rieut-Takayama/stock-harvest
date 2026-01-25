// Stock Harvest AI - Alerts API Service
import { API_PATHS } from '../../types';
import type {
  Alert,
  AlertFormData,
  LineNotificationConfig,
  AlertCondition
} from '../../types';
import { API_BASE_URL } from '@/config/api';

// APIレスポンス型（バックエンドの実際の型）
interface AlertApiResponse {
  id: string;
  stockCode: string;
  stockName: string;
  type: 'price' | 'logic';
  condition: string; // JSON文字列
  isActive: number; // 0/1
  createdAt: string;
  lineNotificationEnabled: number; // 0/1
}

// APIレスポンス → フロントエンド型変換
function transformAlertResponse(apiAlert: AlertApiResponse): Alert {
  let conditionObj: AlertCondition;

  try {
    const parsed = JSON.parse(apiAlert.condition);

    // API構造 → フロントエンド構造に変換
    if (parsed.type === 'price') {
      conditionObj = {
        targetPrice: parsed.value,
        priceDirection: parsed.operator === '>=' ? 'above' : 'below'
      };
    } else if (parsed.type === 'logic') {
      conditionObj = {
        logic: parsed.logicType,
        logicName: parsed.logicType === 'logic_a' ? 'ストップ高張り付き' : '赤字→黒字転換'
      };
    } else {
      conditionObj = {};
    }
  } catch {
    // パースエラー時はデフォルト値
    conditionObj = {};
  }

  return {
    id: apiAlert.id,
    stockCode: apiAlert.stockCode,
    stockName: apiAlert.stockName,
    type: apiAlert.type,
    condition: conditionObj,
    isActive: apiAlert.isActive === 1,
    createdAt: apiAlert.createdAt,
    lineNotificationEnabled: apiAlert.lineNotificationEnabled === 1
  };
}

export class AlertsService {
  
  async getAlerts(): Promise<Alert[]> {
    // 実API統合: GET /api/alerts
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.ALERTS.LIST}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.status}`);
      }

      const apiAlerts: AlertApiResponse[] = await response.json();
      const alerts: Alert[] = apiAlerts.map(transformAlertResponse);
      return alerts;
    } catch {
      // アラート取得失敗時のエラーメッセージを統一
      throw new Error('Failed to fetch alerts');
    }
  }

  async createAlert(formData: AlertFormData): Promise<Alert> {
    // 実API統合: POST /api/alerts
    try {
      // フロントエンド型 → バックエンドAPI型に変換
      const apiRequest = {
        type: formData.alertType,
        stockCode: formData.stockCode,
        condition: formData.alertType === 'price' ? {
          type: 'price',
          operator: '>=',
          value: formData.targetPrice || 0
        } : {
          type: 'logic',
          logicType: 'logic_a'
        }
      };

      const response = await fetch(`${API_BASE_URL}${API_PATHS.ALERTS.CREATE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiRequest),
      });

      if (!response.ok) {
        throw new Error(`Failed to create alert: ${response.status}`);
      }

      const apiAlert: AlertApiResponse = await response.json();
      const alert: Alert = transformAlertResponse(apiAlert);
      return alert;
    } catch {
      // アラート作成失敗時のエラーメッセージを統一
      throw new Error('Failed to create alert');
    }
  }

  async toggleAlert(id: string): Promise<Alert> {
    // 実API統合: PUT /api/alerts/:id/toggle
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.ALERTS.TOGGLE(id)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle alert: ${response.status}`);
      }

      const apiAlert: AlertApiResponse = await response.json();
      const alert: Alert = transformAlertResponse(apiAlert);
      return alert;
    } catch {
      // アラートトグル失敗時のエラーメッセージを統一
      throw new Error('Failed to toggle alert');
    }
  }

  async deleteAlert(id: string): Promise<void> {
    // 実API統合: DELETE /api/alerts/:id
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.ALERTS.DELETE(id)}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete alert: ${response.status}`);
      }
    } catch {
      // アラート削除失敗時のエラーメッセージを統一
      throw new Error('Failed to delete alert');
    }
  }

  async getLineConfig(): Promise<LineNotificationConfig> {
    // 実API統合: GET /api/notifications/line
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.NOTIFICATIONS.LINE_CONFIG}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch LINE config: ${response.status}`);
      }

      const config: LineNotificationConfig = await response.json();
      return config;
    } catch {
      // LINE設定取得失敗時のエラーメッセージを統一
      throw new Error('Failed to fetch LINE config');
    }
  }

  async updateLineStatus(isConnected: boolean): Promise<LineNotificationConfig> {
    // 実API統合: PUT /api/notifications/line
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.NOTIFICATIONS.LINE_CONFIG}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isConnected }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update LINE status: ${response.status}`);
      }

      const config: LineNotificationConfig = await response.json();
      return config;
    } catch {
      // LINE状態更新失敗時のエラーメッセージを統一
      throw new Error('Failed to update LINE status');
    }
  }
}