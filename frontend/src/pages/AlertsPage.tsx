import React, { useState } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Switch,
  FormControlLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  CircularProgress,
  Alert as MuiAlert,
  IconButton,
  Snackbar
} from '@mui/material';
import {
  AddAlert,
  Delete,
  CheckCircle
} from '@mui/icons-material';
import { MainLayout } from '../layouts/MainLayout';
import { useAlertsData } from '../hooks/useAlertsData';
import type { AlertFormData, Alert } from '../types';


export const AlertsPage: React.FC = () => {
  const { alerts, lineConfig, loading, error, createAlert, toggleAlert, deleteAlert } = useAlertsData();
  const [formData, setFormData] = useState<AlertFormData>({
    alertType: 'price',
    stockCode: '',
    targetPrice: undefined
  });
  const [showPriceFields, setShowPriceFields] = useState(true);
  const [notification, setNotification] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  const handleAlertTypeChange = (alertType: 'price' | 'logic') => {
    setFormData({ ...formData, alertType });
    setShowPriceFields(alertType === 'price');
  };

  const handleCreateAlert = async () => {
    if (!formData.stockCode) {
      showNotification('銘柄コードを入力してください', 'error');
      return;
    }
    
    if (formData.alertType === 'price' && !formData.targetPrice) {
      showNotification('目標価格を入力してください', 'error');
      return;
    }
    
    try {
      await createAlert(formData);
      showNotification('アラートを作成しました', 'success');
      
      // フォームをリセット
      setFormData({
        alertType: 'price',
        stockCode: '',
        targetPrice: undefined
      });
      setShowPriceFields(true);
    } catch {
      showNotification('アラートの作成に失敗しました', 'error');
    }
  };

  const handleToggleAlert = async (id: string) => {
    try {
      await toggleAlert(id);
    } catch {
      showNotification('アラートの切り替えに失敗しました', 'error');
    }
  };

  const handleDeleteAlert = async (id: string, stockName: string) => {
    if (window.confirm(`「${stockName}」のアラートを削除しますか？`)) {
      try {
        await deleteAlert(id);
        showNotification('アラートを削除しました', 'success');
      } catch {
        showNotification('アラートの削除に失敗しました', 'error');
      }
    }
  };

  const showNotification = (message: string, severity: 'success' | 'error') => {
    setNotification({ open: true, message, severity });
  };

  const formatCondition = (alert: Alert) => {
    if (alert.type === 'price' && alert.condition.targetPrice) {
      return `価格が ¥${alert.condition.targetPrice.toLocaleString('ja-JP')} を上回ったら通知`;
    }
    if (alert.type === 'logic' && alert.condition.logicName) {
      return `発動時にLINE通知`;
    }
    return '条件不明';
  };

  if (loading) {
    return (
      <MainLayout>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <MuiAlert severity="error">{error.message}</MuiAlert>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
        {/* ページタイトル */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{ color: 'primary.main', fontSize: 32, fontWeight: 500 }}>
            アラート設定
          </Typography>
        </Box>

        {/* 新規アラート作成 */}
        <Card sx={{ mb: 3, background: 'white', borderRadius: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: 'primary.main', mb: 2.5, fontSize: 20, fontWeight: 500 }}>
              新規アラート作成
            </Typography>
            
            <form data-testid="alert-form">
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500, color: '#424242' }}>
                アラートタイプ
              </Typography>
              <FormControl fullWidth size="medium">
                <Select
                  value={formData.alertType}
                  onChange={(e) => handleAlertTypeChange(e.target.value as 'price' | 'logic')}
                  sx={{
                    '& .MuiOutlinedInput-input': { p: 1.5 },
                    border: '1px solid #e0e0e0',
                    borderRadius: 1
                  }}
                >
                  <MenuItem value="price">価格到達アラート</MenuItem>
                  <MenuItem value="logic">ロジック発動アラート</MenuItem>
                </Select>
              </FormControl>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500, color: '#424242' }}>
                銘柄コード
              </Typography>
              <TextField
                fullWidth
                placeholder="例: 7203"
                value={formData.stockCode}
                onChange={(e) => setFormData({ ...formData, stockCode: e.target.value })}
                sx={{
                  '& .MuiOutlinedInput-input': { p: 1.5 },
                  '& .MuiOutlinedInput-root': {
                    border: '1px solid #e0e0e0',
                    borderRadius: 1
                  }
                }}
              />
            </Box>
            
            {showPriceFields && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1, fontWeight: 500, color: '#424242' }}>
                  目標価格
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  placeholder="例: 3000"
                  value={formData.targetPrice || ''}
                  onChange={(e) => setFormData({ ...formData, targetPrice: Number(e.target.value) })}
                  sx={{
                    '& .MuiOutlinedInput-input': { p: 1.5 },
                    '& .MuiOutlinedInput-root': {
                      border: '1px solid #e0e0e0',
                      borderRadius: 1
                    }
                  }}
                />
              </Box>
            )}
            
            <Button
              onClick={handleCreateAlert}
              variant="contained"
              startIcon={<AddAlert />}
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                p: '12px 24px',
                fontSize: 16,
                fontWeight: 500,
                backgroundColor: '#1976d2',
                '&:hover': {
                  backgroundColor: '#1565c0'
                }
              }}
            >
              アラート作成
            </Button>
            </form>
          </CardContent>
        </Card>

        {/* 設定済みアラート一覧 */}
        <Card sx={{ mb: 3, background: 'white', borderRadius: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: 'primary.main', mb: 2.5, fontSize: 20, fontWeight: 500 }}>
              設定済みアラート
            </Typography>
            
            {alerts.length === 0 ? (
              <Box sx={{ textAlign: 'center', color: '#666', py: 5 }}>
                <Typography>設定済みのアラートがありません</Typography>
              </Box>
            ) : (
              alerts.map((alert) => (
                <Box key={alert.id} sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  p: 2,
                  background: '#f8f9fa',
                  borderRadius: 1,
                  mb: 1.5,
                  '&:last-child': { mb: 0 }
                }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography sx={{ fontWeight: 500, color: 'primary.main', mb: 0.5 }}>
                      {alert.stockCode} - {alert.stockName}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#666', fontSize: 14 }}>
                      {formatCondition(alert)}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={alert.isActive}
                          onChange={() => handleToggleAlert(alert.id)}
                          sx={{
                            width: 48,
                            height: 24,
                            '& .MuiSwitch-switchBase': {
                              '&.Mui-checked': {
                                color: '#4caf50',
                                '& + .MuiSwitch-track': {
                                  backgroundColor: '#4caf50'
                                }
                              }
                            }
                          }}
                        />
                      }
                      label=""
                    />
                    <IconButton
                      onClick={() => handleDeleteAlert(alert.id, alert.stockName)}
                      sx={{
                        background: 'none',
                        border: 'none',
                        color: '#666',
                        p: 0.5,
                        borderRadius: 1,
                        '&:hover': {
                          backgroundColor: '#f0f0f0',
                          color: '#f44336'
                        }
                      }}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
              ))
            )}
          </CardContent>
        </Card>

        {/* LINE通知設定 */}
        <Card sx={{ mb: 3, background: 'white', borderRadius: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: 'primary.main', mb: 2.5, fontSize: 20, fontWeight: 500 }}>
              LINE通知設定
            </Typography>
            
            <Box sx={{ textAlign: 'center', p: 2.5 }}>
              <CheckCircle sx={{ color: '#00c300', fontSize: 48, mb: 1 }} />
              <Typography sx={{ mb: 0.5, fontWeight: 500 }}>
                {lineConfig?.isConnected ? 'LINE連携済み' : 'LINE未連携'}
              </Typography>
              <Typography variant="body2" sx={{ color: '#666', fontSize: 14 }}>
                {lineConfig?.isConnected ? '通知は自動的にLINEに送信されます' : 'LINE通知を有効にするには連携が必要です'}
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* 通知 */}
        <Snackbar
          open={notification.open}
          autoHideDuration={3000}
          onClose={() => setNotification({ ...notification, open: false })}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MuiAlert 
            severity={notification.severity} 
            onClose={() => setNotification({ ...notification, open: false })}
            sx={{
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
              borderRadius: 1
            }}
          >
            {notification.message}
          </MuiAlert>
        </Snackbar>
      </Box>
    </MainLayout>
  );
};

export default AlertsPage;