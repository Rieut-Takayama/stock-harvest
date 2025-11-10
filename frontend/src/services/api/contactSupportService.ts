import type { ContactForm, FAQ, ApiResponse } from '@/types';
import { API_PATHS } from '@/types';

const API_BASE_URL = 'http://localhost:8432';

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
    return this.request<FAQ[]>(API_PATHS.CONTACT.FAQ);
  }

  async submitContactForm(formData: ContactForm): Promise<ApiResponse<{ id: string }>> {
    return this.request<ApiResponse<{ id: string }>>(API_PATHS.CONTACT.SUBMIT, {
      method: 'POST',
      body: JSON.stringify(formData),
    });
  }
}