import { useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Alert,
  Divider
} from '@mui/material';
import {
  Send,
  ExpandMore,
  Help,
  BugReport,
  Settings,
  Info,
  CheckCircle
} from '@mui/icons-material';
import { MainLayout } from '../layouts/MainLayout';

// FAQ データ
const faqData = [
  {
    id: '1',
    category: 'スキャン機能',
    question: 'AIスキャンはどのくらいの頻度で実行すべきですか？',
    answer: '市場開場中は5分に1回、開場前後は30分に1回の実行を推奨します。ただし、Yahoo Finance APIの制限を考慮し、過度な実行は避けてください。',
    tags: ['スキャン', 'API制限']
  },
  {
    id: '2',
    category: 'ロジック',
    question: 'ロジックAとロジックBの違いは何ですか？',
    answer: 'ロジックA（ストップ高張り付き）は急激な値上がりを検出し、ロジックB（赤字→黒字転換）は業績改善による株価上昇を検出します。',
    tags: ['ロジックA', 'ロジックB']
  },
  {
    id: '3',
    category: 'アラート',
    question: 'LINE通知が届かない場合の対処法は？',
    answer: 'LINE Notifyのトークンが正しく設定されているか確認してください。また、LINEアプリの通知設定も確認してください。',
    tags: ['LINE通知', 'トラブル']
  },
  {
    id: '4',
    category: 'システム',
    question: 'データの取得遅延はなぜ発生しますか？',
    answer: '無料のYahoo Finance APIを使用しているため、20分程度の遅延が発生します。リアルタイムデータには有料APIが必要です。',
    tags: ['データ遅延', 'API']
  }
];

// システム情報
const systemInfo = {
  version: '1.0.0',
  status: 'healthy',
  lastScanAt: '2025-11-07 23:45:32',
  activeAlerts: 15,
  totalUsers: 1,
  databaseStatus: 'connected'
};

export const ContactPage = () => {
  const [contactForm, setContactForm] = useState({
    type: 'technical',
    subject: '',
    content: '',
    email: '',
    priority: 'medium'
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // ここで実際のフォーム送信処理を行う
    // Contact form submitted
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'down': return 'error';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'スキャン機能': return <Settings />;
      case 'ロジック': return <Info />;
      case 'アラート': return <BugReport />;
      case 'システム': return <Help />;
      default: return <Help />;
    }
  };

  return (
    <MainLayout>
      <Box sx={{ p: 0 }}>
        {/* ヘッダー */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
            問合せサポート
          </Typography>
          <Typography variant="body1" color="text.secondary">
            よくある質問とお問い合わせフォーム
          </Typography>
        </Box>

        {submitted && (
          <Alert severity="success" sx={{ mb: 4 }}>
            <Typography>
              お問い合わせを受け付けました。48時間以内にご回答いたします。
            </Typography>
          </Alert>
        )}

        <Grid container spacing={4}>
          {/* FAQ セクション */}
          <Grid size={{ xs: 12, md: 8 }}>
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  <Help sx={{ verticalAlign: 'middle', mr: 1 }} />
                  よくある質問 (FAQ)
                </Typography>

                {faqData.map((faq) => (
                  <Accordion key={faq.id} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        {getCategoryIcon(faq.category)}
                        <Box sx={{ ml: 1, flexGrow: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {faq.question}
                          </Typography>
                          <Box sx={{ mt: 0.5 }}>
                            <Chip 
                              label={faq.category} 
                              size="small" 
                              color="primary" 
                              sx={{ mr: 1, fontSize: '0.75rem' }} 
                            />
                            {faq.tags.map((tag, index) => (
                              <Chip 
                                key={index}
                                label={tag} 
                                size="small" 
                                variant="outlined" 
                                sx={{ mr: 0.5, fontSize: '0.75rem' }} 
                              />
                            ))}
                          </Box>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary">
                        {faq.answer}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </CardContent>
            </Card>

            {/* お問い合わせフォーム */}
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  <Send sx={{ verticalAlign: 'middle', mr: 1 }} />
                  お問い合わせフォーム
                </Typography>

                <Box component="form" onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    <Grid size={{ xs: 12, sm: 6 }}>
                      <FormControl fullWidth>
                        <InputLabel>お問い合わせ種別</InputLabel>
                        <Select
                          value={contactForm.type}
                          label="お問い合わせ種別"
                          onChange={(e) => setContactForm({...contactForm, type: e.target.value})}
                        >
                          <MenuItem value="technical">技術的問題</MenuItem>
                          <MenuItem value="feature">機能要望</MenuItem>
                          <MenuItem value="bug">不具合報告</MenuItem>
                          <MenuItem value="other">その他</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid size={{ xs: 12, sm: 6 }}>
                      <FormControl fullWidth>
                        <InputLabel>優先度</InputLabel>
                        <Select
                          value={contactForm.priority}
                          label="優先度"
                          onChange={(e) => setContactForm({...contactForm, priority: e.target.value})}
                        >
                          <MenuItem value="low">低</MenuItem>
                          <MenuItem value="medium">中</MenuItem>
                          <MenuItem value="high">高</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid size={{ xs: 12 }}>
                      <TextField
                        fullWidth
                        label="件名"
                        value={contactForm.subject}
                        onChange={(e) => setContactForm({...contactForm, subject: e.target.value})}
                        required
                      />
                    </Grid>

                    <Grid size={{ xs: 12 }}>
                      <TextField
                        fullWidth
                        label="メールアドレス"
                        type="email"
                        value={contactForm.email}
                        onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                        required
                      />
                    </Grid>

                    <Grid size={{ xs: 12 }}>
                      <TextField
                        fullWidth
                        label="お問い合わせ内容"
                        multiline
                        rows={6}
                        value={contactForm.content}
                        onChange={(e) => setContactForm({...contactForm, content: e.target.value})}
                        placeholder="詳細な内容をご記入ください。エラーメッセージがある場合は併せてお知らせください。"
                        required
                      />
                    </Grid>

                    <Grid size={{ xs: 12 }}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        startIcon={<Send />}
                        sx={{
                          background: 'linear-gradient(45deg, #38a169, #4caf50)',
                          '&:hover': {
                            background: 'linear-gradient(45deg, #2f855a, #43a047)',
                          },
                        }}
                      >
                        送信
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* システム情報 */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                  <Info sx={{ verticalAlign: 'middle', mr: 1 }} />
                  システム情報
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      バージョン
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                      {systemInfo.version}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      システム状態
                    </Typography>
                    <Chip 
                      label={systemInfo.status === 'healthy' ? '正常' : '異常'}
                      color={getStatusColor(systemInfo.status)}
                      size="small"
                      icon={systemInfo.status === 'healthy' ? <CheckCircle /> : undefined}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      最終スキャン
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {systemInfo.lastScanAt}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      有効アラート
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {systemInfo.activeAlerts}件
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      データベース
                    </Typography>
                    <Chip 
                      label={systemInfo.databaseStatus === 'connected' ? '接続中' : '未接続'}
                      color={systemInfo.databaseStatus === 'connected' ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                </Box>

                <Divider sx={{ my: 3 }} />

                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                  お困りのことがございましたら、
                  <br />
                  お気軽にお問い合わせください。
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </MainLayout>
  );
};