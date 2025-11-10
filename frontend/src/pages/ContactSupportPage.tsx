import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import {
  ContactSupport,
  HelpOutline,
  Email,
  Send,
  Info,
  CheckCircle
} from '@mui/icons-material';
import { MainLayout } from '@/layouts/MainLayout';
import { FAQItem } from '@/components/FAQItem';
import { useContactSupport } from '@/hooks/useContactSupport';
import type { ContactForm } from '@/types';

export const ContactSupportPage: React.FC = () => {
  const { faqData, systemInfo, loading, error, submitLoading, submitContactForm } = useContactSupport();
  
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  
  // フォーム状態
  const [formData, setFormData] = useState<ContactForm>({
    type: 'technical' as const,
    subject: '',
    content: '',
    email: '',
    priority: 'medium'
  });

  const handleFAQChange = (faqId: string) => (isExpanded: boolean) => {
    setExpandedFAQ(isExpanded ? faqId : null);
  };

  const handleFormChange = (field: keyof ContactForm) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | { target: { value: string } }) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    const success = await submitContactForm(formData);
    
    if (success) {
      setFormData({
        type: 'technical' as const,
        subject: '',
        content: '',
        email: '',
        priority: 'medium'
      });
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 5000);
    }
  };

  const isFormValid = formData.type && formData.subject && formData.content && formData.email;

  if (loading) {
    return (
      <MainLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message}
        </Alert>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Box sx={{ maxWidth: 1000, mx: 'auto' }}>
        {/* ページタイトル */}
        <Box textAlign="center" mb={4}>
          <Typography variant="h4" component="h1" fontWeight={500} color="text.primary">
            <ContactSupport sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
            問合せサポート
          </Typography>
        </Box>

        {/* 成功メッセージ */}
        {showSuccessMessage && (
          <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircle />}>
            お問い合わせを送信しました。回答まで1-2営業日お待ちください。
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* FAQセクション */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ mb: 3 }}>
              <Box p={2} borderBottom="1px solid #e2e8f0">
                <Typography variant="h6" fontWeight={500}>
                  <HelpOutline sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
                  よくある質問
                </Typography>
              </Box>
              <Box>
                {faqData.map((faq) => (
                  <FAQItem
                    key={faq.id}
                    faq={faq}
                    expanded={expandedFAQ === faq.id}
                    onChange={handleFAQChange(faq.id)}
                  />
                ))}
              </Box>
            </Paper>

            {/* システム情報 */}
            {systemInfo && (
              <Paper>
                <Box p={2} borderBottom="1px solid #e2e8f0">
                  <Typography variant="h6" fontWeight={500}>
                    <Info sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
                    システム情報
                  </Typography>
                </Box>
                <Box p={2}>
                  <Box display="flex" justifyContent="space-between" py={1} borderBottom="1px solid #e2e8f0">
                    <Typography variant="body2" fontWeight={500} color="text.secondary">
                      バージョン
                    </Typography>
                    <Typography variant="body2" color="text.primary">
                      {systemInfo.version}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" py={1} borderBottom="1px solid #e2e8f0">
                    <Typography variant="body2" fontWeight={500} color="text.secondary">
                      最終更新
                    </Typography>
                    <Typography variant="body2" color="text.primary">
                      {systemInfo.lastUpdated}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center" py={1}>
                    <Typography variant="body2" fontWeight={500} color="text.secondary">
                      稼働状況
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: systemInfo.status === 'healthy' ? 'success.main' : 'error.main'
                        }}
                      />
                      <Typography variant="body2" color="text.primary">
                        {systemInfo.statusDisplay}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Paper>
            )}
          </Grid>

          {/* お問い合わせフォーム */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper>
              <Box p={2} borderBottom="1px solid #e2e8f0">
                <Typography variant="h6" fontWeight={500}>
                  <Email sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
                  お問い合わせ
                </Typography>
              </Box>
              
              <Box component="form" onSubmit={handleSubmit} p={2}>
                <FormControl fullWidth margin="normal" required>
                  <InputLabel>問合せ種別</InputLabel>
                  <Select
                    value={formData.type}
                    onChange={handleFormChange('type')}
                    label="問合せ種別"
                  >
                    <MenuItem value="technical">技術的な問題</MenuItem>
                    <MenuItem value="feature">機能要望</MenuItem>
                    <MenuItem value="bug">不具合報告</MenuItem>
                    <MenuItem value="other">その他</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  margin="normal"
                  label="件名"
                  placeholder="問合せの件名"
                  value={formData.subject}
                  onChange={handleFormChange('subject')}
                  required
                />

                <TextField
                  fullWidth
                  margin="normal"
                  label="内容"
                  placeholder="詳細な内容をご記入ください"
                  multiline
                  rows={4}
                  value={formData.content}
                  onChange={handleFormChange('content')}
                  required
                />

                <TextField
                  fullWidth
                  margin="normal"
                  label="連絡先メール"
                  type="email"
                  placeholder="回答先のメールアドレス"
                  value={formData.email}
                  onChange={handleFormChange('email')}
                  required
                />

                <Box mt={3}>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={!isFormValid || submitLoading}
                    startIcon={submitLoading ? <CircularProgress size={20} /> : <Send />}
                    fullWidth
                  >
                    {submitLoading ? '送信中...' : '送信する'}
                  </Button>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </MainLayout>
  );
};

export default ContactSupportPage;