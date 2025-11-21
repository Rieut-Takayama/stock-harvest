// Stock Harvest AI - Alerts API Service
import { API_PATHS } from '../../types';
import type { 
  Alert, 
  AlertFormData, 
  LineNotificationConfig
} from '../../types';

const API_BASE_URL = 'http://localhost:8432';

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

      const alerts: Alert[] = await response.json();
      return alerts;
    } catch (error) {
      // Alert fetch error handled
      throw new Error('Failed to fetch alerts');
    }
  }

  async createAlert(formData: AlertFormData): Promise<Alert> {
    // 実API統合: POST /api/alerts
    try {
      const response = await fetch(`${API_BASE_URL}${API_PATHS.ALERTS.CREATE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Failed to create alert: ${response.status}`);
      }

      const alert: Alert = await response.json();
      return alert;
    } catch (error) {
      // Alert creation error handled
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

      const alert: Alert = await response.json();
      return alert;
    } catch (error) {
      // Alert toggle error handled
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
    } catch (error) {
      // Alert deletion error handled
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
    } catch (error) {
      // LINE config fetch error handled
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
    } catch (error) {
      // LINE status update error handled
      throw new Error('Failed to update LINE status');
    }
  }
}