import { useState, useEffect } from 'react';
import { ContactSupportService } from '@/services/api/contactSupportService';
import { SystemService } from '@/services/api/systemService';
import type { ContactForm, FAQ, SystemInfo } from '@/types';

const contactSupportService = new ContactSupportService();
const systemService = new SystemService();

export const useContactSupport = () => {
  const [faqData, setFaqData] = useState<FAQ[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [submitLoading, setSubmitLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [faqs, sysInfo] = await Promise.all([
        contactSupportService.getFAQList(),
        systemService.getSystemInfo()
      ]);
      
      setFaqData(faqs);
      setSystemInfo(sysInfo);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const submitContactForm = async (formData: ContactForm): Promise<boolean> => {
    try {
      setSubmitLoading(true);
      setError(null);
      
      const response = await contactSupportService.submitContactForm(formData);
      
      if (response.success) {
        return true;
      } else {
        throw new Error(response.message || 'お問い合わせの送信に失敗しました');
      }
    } catch (err) {
      setError(err as Error);
      return false;
    } finally {
      setSubmitLoading(false);
    }
  };

  return {
    faqData,
    systemInfo,
    loading,
    error,
    submitLoading,
    submitContactForm,
    refetch: fetchData
  };
};