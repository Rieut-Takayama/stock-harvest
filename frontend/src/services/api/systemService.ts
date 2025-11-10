import type { SystemInfo } from '@/types';
import { API_PATHS } from '@/types';

const API_BASE_URL = 'http://localhost:8432';

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
    return this.request<SystemInfo>(API_PATHS.SYSTEM.INFO);
  }

  async getSystemStatus(): Promise<{ healthy: boolean; checks: Record<string, unknown> }> {
    return this.request<{ healthy: boolean; checks: Record<string, unknown> }>(API_PATHS.SYSTEM.STATUS);
  }
}