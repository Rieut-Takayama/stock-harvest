import { useState, useEffect } from 'react';
import { AlertsService } from '../services/api/alertsService';
import type { Alert, AlertFormData, LineNotificationConfig } from '../types';

const alertsService = new AlertsService();

export const useAlertsData = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [lineConfig, setLineConfig] = useState<LineNotificationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const alertsData = await alertsService.getAlerts();
      setAlerts(alertsData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLineConfig = async () => {
    try {
      const config = await alertsService.getLineConfig();
      setLineConfig(config);
    } catch {
      // LINE設定の取得エラーは無視し、初期値nullのまま継続
      console.warn('LINE設定取得に失敗しましたが、アプリの動作には影響しません');
    }
  };

  useEffect(() => {
    fetchAlerts();
    fetchLineConfig();
  }, []);

  const createAlert = async (formData: AlertFormData) => {
    try {
      await alertsService.createAlert(formData);
      await fetchAlerts(); // リフレッシュ
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  const toggleAlert = async (id: string) => {
    try {
      await alertsService.toggleAlert(id);
      await fetchAlerts(); // リフレッシュ
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  const deleteAlert = async (id: string) => {
    try {
      await alertsService.deleteAlert(id);
      await fetchAlerts(); // リフレッシュ
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  const updateLineStatus = async (isConnected: boolean) => {
    try {
      const config = await alertsService.updateLineStatus(isConnected);
      setLineConfig(config);
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  return {
    alerts,
    lineConfig,
    loading,
    error,
    createAlert,
    toggleAlert,
    deleteAlert,
    updateLineStatus,
    refetch: fetchAlerts
  };
};