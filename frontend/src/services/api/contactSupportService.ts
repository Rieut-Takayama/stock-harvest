import type { ContactForm, FAQ, ApiResponse } from '@/types';
import { API_PATHS } from '@/types';
import { logger } from '@/lib/logger';
import { API_BASE_URL } from '@/config/api';

export class ContactSupportService {
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

  async getFAQList(): Promise<FAQ[]> {
    try {
      return await this.request<FAQ[]>(API_PATHS.CONTACT.FAQ);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('ContactSupport API Error:', { method: 'getFAQList', error: errorMessage });
      throw new Error(`[ContactSupportService] ${errorMessage}`);
    }
  }

  async submitContactForm(formData: ContactForm): Promise<ApiResponse<{ id: string }>> {
    try {
      return await this.request<ApiResponse<{ id: string }>>(API_PATHS.CONTACT.SUBMIT, {
        method: 'POST',
        body: JSON.stringify(formData),
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logger.error('ContactSupport API Error:', { method: 'submitContactForm', error: errorMessage });
      throw new Error(`[ContactSupportService] ${errorMessage}`);
    }
  }
}