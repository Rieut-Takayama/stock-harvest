import type { SystemInfo } from '@/types';
import { API_PATHS } from '@/types';
import { logger } from '@/lib/logger';
import { API_BASE_URL } from '@/config/api';

export class SystemService {
  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${path}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} - ${errorText}`);
    }

    return response.json();
  }

  async getSystemInfo(): Promise<SystemInfo> {
    try {
      return await this.request<SystemInfo>(API_PATHS.SYSTEM.INFO);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('System API Error:', { method: 'getSystemInfo', error: errorMessage });
      throw new Error(`[SystemService] ${errorMessage}`);
    }
  }

  async getSystemStatus(): Promise<{ healthy: boolean; checks: Record<string, unknown> }> {
    try {
      return await this.request<{ healthy: boolean; checks: Record<string, unknown> }>(API_PATHS.SYSTEM.STATUS);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('System API Error:', { method: 'getSystemStatus', error: errorMessage });
      throw new Error(`[SystemService] ${errorMessage}`);
    }
  }
}