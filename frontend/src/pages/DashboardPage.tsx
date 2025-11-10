import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';
import { MainLayout } from '../layouts/MainLayout';
import { useDashboardData } from '../hooks/useDashboardData';
import type { ManualSignalRequest, StockData } from '../types';

export const DashboardPage: React.FC = () => {
  const {
    scanStatus,
    logicStatus,
    loading,
    error,
    isScanning,
    scanProgress,
    executeScan,
    executeManualSignal,
    showChart
  } = useDashboardData();

  const [confirmDialog, setConfirmDialog] = React.useState<{
    open: boolean;
    type: 'stop_loss' | 'take_profit' | null;
    title: string;
    message: string;
  }>({ open: false, type: null, title: '', message: '' });

  // ローディング状態
  if (loading) {
    return (
      <MainLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  // エラー状態
  if (error) {
    return (
      <MainLayout>
        <Alert severity="error" sx={{ m: 3 }}>
          エラーが発生しました: {error.message}
        </Alert>
      </MainLayout>
    );
  }

  const handleScanClick = async () => {
    try {
      await executeScan();
    } catch (err) {
      console.error('スキャン実行エラー:', err);
    }
  };

  const handleManualSignalClick = (type: 'stop_loss' | 'take_profit') => {
    const isStopLoss = type === 'stop_loss';
    setConfirmDialog({
      open: true,
      type,
      title: isStopLoss ? '損切り実行' : '利確実行',
      message: isStopLoss 
        ? '損切りシグナルを送信しますか？' 
        : '利確シグナルを送信しますか？'
    });
  };

  const handleConfirmSignal = async () => {
    if (!confirmDialog.type) return;

    try {
      const request: ManualSignalRequest = {
        type: confirmDialog.type,
        timestamp: new Date().toISOString(),
        reason: 'Manual execution from dashboard'
      };
      
      const result = await executeManualSignal(request);
      alert(result.message);
    } catch (err) {
      console.error('シグナル実行エラー:', err);
      alert('シグナルの実行に失敗しました');
    } finally {
      setConfirmDialog({ open: false, type: null, title: '', message: '' });
    }
  };

  const handleChartClick = (stockCode: string) => {
    showChart(stockCode);
  };

  const formatPrice = (price: number) => {
    return `¥${price.toLocaleString()}`;
  };

  const formatChange = (change: number, changeRate: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change} (${sign}${changeRate}%)`;
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? '#38a169' : '#e53e3e';
  };

  const getLogicStatusText = (status: string) => {
    switch (status) {
      case 'detecting': return '検出中';
      case 'completed': return '完了';
      case 'error': return 'エラー';
      default: return 'unknown';
    }
  };

  return (
    <MainLayout>
      <Box data-testid="dashboard-container" sx={{ maxWidth: '1200px', mx: 'auto', p: 3 }}>
        {/* ヘッダーセクション */}
        <Box sx={{ mb: 4 }}>
          <Typography 
            variant="h4" 
            sx={{ 
              fontSize: '2rem',
              fontWeight: 500,
              color: '#38a169',
              mb: 1
            }}
          >
            ロジックスキャナーダッシュボード
          </Typography>
          <Typography variant="body2" color="text.secondary">
            全銘柄AIスキャンで投資チャンスを発見
          </Typography>
        </Box>

        {/* スキャン実行コントロール */}
        <Box sx={{ display: 'flex', gap: 2, mb: 4, alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={isScanning ? <CircularProgress size={16} color="inherit" /> : <SearchIcon />}
            onClick={handleScanClick}
            disabled={isScanning}
            sx={{
              background: 'linear-gradient(135deg, #38a169 0%, #4caf50 100%)',
              color: 'white',
              px: 3,
              py: 1.5,
              borderRadius: 2,
              fontSize: '1rem',
              fontWeight: 500,
              boxShadow: '0 4px 12px rgba(56, 161, 105, 0.3)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 16px rgba(56, 161, 105, 0.4)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #a0a0a0 0%, #b0b0b0 100%)',
              }
            }}
          >
            {isScanning ? 'スキャン中...' : '今すぐスキャン'}
          </Button>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary', fontSize: '0.875rem' }}>
            {isScanning ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#38a169' }}>
                <CircularProgress size={16} color="inherit" />
                <span>全3,800銘柄をスキャン中... ({scanProgress}%)</span>
              </Box>
            ) : (
              <>
                <TimeIcon sx={{ fontSize: '1rem' }} />
                <span>最終スキャン: {scanStatus?.lastScanAt || '未実行'}</span>
              </>
            )}
          </Box>
        </Box>

        {/* ロジックセクション */}
        <Box sx={{ display: 'grid', gap: 4 }}>
          {logicStatus.map((logic) => (
            <Card key={logic.logicType} sx={{ 
              borderRadius: 3,
              border: '1px solid #e8f5e8',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
            }}>
              <CardContent sx={{ p: 3 }}>
                {/* ロジックヘッダー */}
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  mb: 2.5,
                  pb: 2,
                  borderBottom: '1px solid #e8f5e8'
                }}>
                  <Typography variant="h6" sx={{ fontWeight: 500, color: '#2d3748' }}>
                    ロジック{logic.logicType.charAt(logic.logicType.length - 1).toUpperCase()}: {logic.name}
                  </Typography>
                  <Chip 
                    label={getLogicStatusText(logic.status)}
                    sx={{
                      bgcolor: '#38a169',
                      color: 'white',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      px: 1.5
                    }}
                  />
                </Box>

                {/* 銘柄リスト */}
                <Box sx={{ display: 'grid', gap: 2 }}>
                  {logic.detectedStocks.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 5, color: 'text.secondary' }}>
                      <Typography>検出された銘柄がありません</Typography>
                    </Box>
                  ) : (
                    logic.detectedStocks.map((stock: StockData) => (
                      <Box key={stock.code} sx={{
                        display: 'grid',
                        gridTemplateColumns: '1fr auto auto',
                        gap: 2,
                        p: 2,
                        bgcolor: '#fafafa',
                        borderRadius: 2,
                        border: '1px solid #eeeeee',
                        alignItems: 'center'
                      }}>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Typography sx={{ fontWeight: 500, color: '#2d3748', fontSize: '0.875rem' }}>
                            {stock.code}
                          </Typography>
                          <Typography sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
                            {stock.name}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: 0.25 }}>
                          <Typography sx={{ fontWeight: 500, fontSize: '1rem', color: '#2d3748' }}>
                            {formatPrice(stock.price)}
                          </Typography>
                          <Typography sx={{ 
                            fontSize: '0.75rem',
                            color: getChangeColor(stock.change)
                          }}>
                            {formatChange(stock.change, stock.changeRate)}
                          </Typography>
                        </Box>
                        
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleChartClick(stock.code)}
                          sx={{
                            bgcolor: '#38a169',
                            color: 'white',
                            fontSize: '0.875rem',
                            whiteSpace: 'nowrap',
                            '&:hover': {
                              bgcolor: '#2f855a'
                            }
                          }}
                        >
                          チャート
                        </Button>
                      </Box>
                    ))
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* 手動決済シグナルセクション */}
        <Card sx={{ 
          mt: 4,
          borderRadius: 3,
          border: '1px solid #e8f5e8',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ 
              mb: 2.5,
              pb: 2,
              borderBottom: '1px solid #e8f5e8'
            }}>
              <Typography variant="h6" sx={{ fontWeight: 500, color: '#2d3748', mb: 1 }}>
                手動決済シグナル
              </Typography>
              <Typography variant="body2" color="text.secondary">
                損切り・利確タイミングの実行
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                onClick={() => handleManualSignalClick('stop_loss')}
                sx={{
                  color: '#e53e3e',
                  borderColor: '#e53e3e',
                  bgcolor: 'white',
                  px: 2.5,
                  py: 1.25,
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  '&:hover': {
                    bgcolor: '#e53e3e',
                    color: 'white'
                  }
                }}
              >
                損切り実行
              </Button>
              <Button
                variant="outlined"
                onClick={() => handleManualSignalClick('take_profit')}
                sx={{
                  color: '#38a169',
                  borderColor: '#38a169',
                  bgcolor: 'white',
                  px: 2.5,
                  py: 1.25,
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  '&:hover': {
                    bgcolor: '#38a169',
                    color: 'white'
                  }
                }}
              >
                利確実行
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* 確認ダイアログ */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false, type: null, title: '', message: '' })}
      >
        <DialogTitle>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <Typography>{confirmDialog.message}</Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setConfirmDialog({ open: false, type: null, title: '', message: '' })}
            color="inherit"
          >
            キャンセル
          </Button>
          <Button 
            onClick={handleConfirmSignal} 
            color="primary" 
            variant="contained"
          >
            実行
          </Button>
        </DialogActions>
      </Dialog>
    </MainLayout>
  );
};

export default DashboardPage;