import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Search as SearchIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';
import { useDashboardData } from '../hooks/useDashboardData';
export const DashboardPage: React.FC = () => {
  const {
    scanStatus,
    logicStatus,
    loading,
    error,
    isScanning,
    scanProgress,
    executeScan
  } = useDashboardData();

  // ローディング状態
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // エラー状態
  if (error) {
    return (
      <Box minHeight="100vh" p={3}>
        <Alert severity="error">
          エラーが発生しました: {error.message}
        </Alert>
      </Box>
    );
  }

  const handleScanClick = async () => {
    try {
      await executeScan();
    } catch (err) {
      console.error('スキャン実行エラー:', err);
    }
  };


  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #1a202c 0%, #2d3748 50%, #4a5568 100%)',
      p: { xs: 2, sm: 3, md: 4, lg: 6 },
      display: 'flex',
      justifyContent: 'center'
    }}>
      <Box data-testid="dashboard-container" sx={{ 
        width: '100%', 
        maxWidth: '1200px'
      }}>
        {/* ヘッダーセクション - ガラスモーフィズム */}
        <Box sx={{ 
          mb: 4, 
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 4,
          p: 4,
          border: '1px solid rgba(255, 255, 255, 0.3)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)'
        }}>
          <Typography 
            variant="h3" 
            sx={{ 
              fontSize: { xs: '1.75rem', sm: '2rem', md: '2.5rem' },
              fontWeight: 700,
              color: '#1a202c',
              mb: 2
            }}
          >
            🚀 Stock Harvest AI
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#4a5568', 
              fontSize: { xs: '1rem', sm: '1.1rem' },
              fontWeight: 500,
              letterSpacing: '0.5px'
            }}
          >
            次世代AIが発見する隠れた投資機会
          </Typography>
        </Box>

        {/* スキャン実行コントロール */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', sm: 'row' },
          gap: 2, 
          mb: 4, 
          alignItems: { xs: 'stretch', sm: 'center' },
          justifyContent: 'center'
        }}>
          <Button
            variant="contained"
            startIcon={isScanning ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
            onClick={handleScanClick}
            disabled={isScanning}
            sx={{
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              color: 'white',
              px: 4,
              py: 2,
              borderRadius: '50px',
              fontSize: '1.1rem',
              fontWeight: 600,
              boxShadow: '0 8px 32px rgba(37, 99, 235, 0.4)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              textTransform: 'none',
              '&:hover': {
                transform: 'translateY(-3px) scale(1.02)',
                boxShadow: '0 12px 40px rgba(37, 99, 235, 0.6)',
                background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
              },
              '&:disabled': {
                background: 'linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)',
                transform: 'none',
              },
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            {isScanning ? (
              <>
                <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                AIスキャン実行中...
              </>
            ) : (
              <>
                <SearchIcon sx={{ mr: 1 }} />
                🎯 今すぐAIスキャン開始
              </>
            )}
          </Button>
          
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            color: '#ffffff', 
            fontSize: '0.875rem',
            background: 'rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(10px)',
            borderRadius: '20px',
            px: 3,
            py: 1.5,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            fontWeight: 500
          }}>
            {isScanning ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#10b981' }}>
                <CircularProgress size={16} sx={{ color: '#10b981' }} />
                <span style={{ fontWeight: 600 }}>全3,800銘柄をAIスキャン中... ({scanProgress}%)</span>
              </Box>
            ) : (
              <>
                <TimeIcon sx={{ fontSize: '1rem', color: '#ffffff' }} />
                <span style={{ fontWeight: 600 }}>最終スキャン: {scanStatus?.lastScanAt || '未実行'}</span>
              </>
            )}
          </Box>
        </Box>

        {/* ロジックセクション - 2列グリッド */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 4 }}>
          {logicStatus.map((logic, index) => (
            <Card key={logic.logicType} sx={{ 
              borderRadius: 4,
              border: 'none',
              background: index === 0 
                ? 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)'
                : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)',
              color: 'white',
              minHeight: '240px',
              position: 'relative',
              overflow: 'hidden',
              transform: 'perspective(1000px) rotateX(0deg)',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                transform: 'perspective(1000px) rotateX(-5deg) translateY(-10px)',
                boxShadow: '0 25px 80px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2)',
              }
            }}>
              {/* ロケットアイコン背景 */}
              <Box sx={{
                position: 'absolute',
                top: 20,
                right: 20,
                fontSize: '3rem',
                opacity: 0.3
              }}>
                🚀
              </Box>
              
              <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* ロジックヘッダー */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h5" sx={{ 
                    fontWeight: 800, 
                    mb: 1, 
                    color: '#ffffff',
                    textShadow: '0 2px 8px rgba(0, 0, 0, 0.5)',
                    fontSize: '1.5rem'
                  }}>
                    ロジック{logic.logicType.charAt(logic.logicType.length - 1).toUpperCase()}
                  </Typography>
                  <Typography variant="h6" sx={{ 
                    color: '#ffffff', 
                    lineHeight: 1.4,
                    fontWeight: 600,
                    textShadow: '0 1px 4px rgba(0, 0, 0, 0.4)',
                    fontSize: '1rem',
                    mb: 1
                  }}>
                    {logic.name}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: '#ffffff', 
                    fontSize: '0.8rem',
                    fontWeight: 400,
                    textShadow: '0 1px 4px rgba(0, 0, 0, 0.4)'
                  }}>
                    優良企業を機械学習で発見するロジック
                  </Typography>
                </Box>
                
                {/* ステータス */}
                <Box sx={{ mt: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip 
                    label="分析中..."
                    sx={{
                      bgcolor: 'rgba(0, 0, 0, 0.3)',
                      color: '#ffffff',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      border: '1px solid rgba(255, 255, 255, 0.4)',
                      textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)'
                    }}
                  />
                  <Typography variant="body2" sx={{ 
                    fontSize: '0.75rem', 
                    color: '#ffffff',
                    fontWeight: 600,
                    textShadow: '0 1px 4px rgba(0, 0, 0, 0.4)'
                  }}>
                    対象銘柄 3,800社
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* 統計サマリー - ネオモーフィズム */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, 
          gap: { xs: 2, sm: 3 }, 
          mb: 4,
          maxWidth: '700px',
          mx: 'auto'
        }}>
          <Card sx={{ 
            borderRadius: 3, 
            background: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            textAlign: 'center', 
            p: 3,
            transition: 'all 0.3s ease',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              transform: 'translateY(-5px)',
              boxShadow: '0 15px 45px rgba(0, 0, 0, 0.2)',
              background: 'rgba(255, 255, 255, 1)'
            }
          }}>
            <Typography variant="h4" sx={{ mb: 1, fontSize: '2rem' }}>📊</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#1a202c' }}>3</Typography>
            <Typography variant="body2" sx={{ color: '#4a5568', fontWeight: 500 }}>アクティブロジック</Typography>
          </Card>
          
          <Card sx={{ 
            borderRadius: 3, 
            background: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            textAlign: 'center', 
            p: 3,
            transition: 'all 0.3s ease',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              transform: 'translateY(-5px)',
              boxShadow: '0 15px 45px rgba(0, 0, 0, 0.2)',
              background: 'rgba(255, 255, 255, 1)'
            }
          }}>
            <Typography variant="h4" sx={{ mb: 1, fontSize: '2rem' }}>📈</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#1a202c' }}>2</Typography>
            <Typography variant="body2" sx={{ color: '#4a5568', fontWeight: 500 }}>今日発見した</Typography>
          </Card>
          
          <Card sx={{ 
            borderRadius: 3, 
            background: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            textAlign: 'center', 
            p: 3,
            transition: 'all 0.3s ease',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              transform: 'translateY(-5px)',
              boxShadow: '0 15px 45px rgba(0, 0, 0, 0.2)',
              background: 'rgba(255, 255, 255, 1)'
            }
          }}>
            <Typography variant="h4" sx={{ mb: 1, fontSize: '2rem' }}>🎯</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#059669' }}>+18.5%</Typography>
            <Typography variant="body2" sx={{ color: '#4a5568', fontWeight: 500 }}>平均リターン</Typography>
          </Card>
        </Box>

        <Typography variant="body2" sx={{ 
          textAlign: 'center', 
          color: '#ffffff', 
          mb: 4,
          fontSize: '0.9rem',
          fontWeight: 500,
          letterSpacing: '0.5px',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '20px',
          px: 3,
          py: 1,
          display: 'inline-block',
          mx: 'auto'
        }}>
          ⏰ 最終スキャン: 19:44:15
        </Typography>

        {/* 検出結果セクション */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ 
            mb: 3, 
            fontWeight: 800, 
            color: '#ffffff', 
            textAlign: 'center',
            textShadow: '0 3px 8px rgba(0,0,0,0.6)',
            fontSize: { xs: '1.4rem', sm: '1.6rem' },
            background: 'rgba(0, 0, 0, 0.4)',
            borderRadius: '30px',
            px: 4,
            py: 2,
            display: 'inline-block',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            🎯 AI検出: ストップ高候補銘柄
          </Typography>
          
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, 
            gap: { xs: 2, sm: 3 },
            maxWidth: '800px',
            mx: 'auto'
          }}>
            {[
              { code: '4819', name: 'デジタルガレージ', status: '分析中' },
              { code: '2158', name: 'フロンテッジ', status: '分析中' },
              { code: '4477', name: 'BASE', status: '分析中' }
            ].map((stock) => (
              <Card key={stock.code} sx={{ 
                borderRadius: 3, 
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                p: 3,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
                  background: 'rgba(255, 255, 255, 1)',
                }
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {stock.code}
                  </Typography>
                  <Chip 
                    label={stock.status}
                    size="small"
                    sx={{ 
                      fontSize: '0.7rem', 
                      bgcolor: '#2563eb', 
                      color: '#ffffff',
                      fontWeight: 600,
                      border: '1px solid rgba(255, 255, 255, 0.2)'
                    }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {stock.name}
                </Typography>
                <Button
                  size="small"
                  variant="contained"
                  fullWidth
                  sx={{ 
                    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    color: 'white',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    borderRadius: '20px',
                    textTransform: 'none',
                    boxShadow: '0 4px 16px rgba(37, 99, 235, 0.3)',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 24px rgba(37, 99, 235, 0.5)',
                      background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)'
                    }
                  }}
                >
                  🔍 詳細分析
                </Button>
              </Card>
            ))}
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;