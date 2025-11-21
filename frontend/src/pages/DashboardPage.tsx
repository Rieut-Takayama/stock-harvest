import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { useDashboardData } from '../hooks/useDashboardData';
import { ScanStatusCard } from '../components/dashboard/ScanStatusCard';
import { LogicResults } from '../components/dashboard/LogicResults';
import { TopStocks } from '../components/dashboard/TopStocks';
import { SystemStatus } from '../components/dashboard/SystemStatus';
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
      // Scan execution error in dashboard
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
          mb: { xs: 3, sm: 4 }, 
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: 4,
          p: { xs: 2, sm: 3, md: 4 },
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
        <ScanStatusCard
          scanStatus={scanStatus}
          isScanning={isScanning}
          scanProgress={scanProgress}
          onScanClick={handleScanClick}
        />

        {/* ロジックセクション - 2列グリッド */}
        <LogicResults logicStatus={logicStatus} />

        {/* 統計サマリー - ネオモーフィズム */}
        <SystemStatus />

        {/* 検出結果セクション */}
        <TopStocks />
      </Box>
    </Box>
  );
};

export default DashboardPage;