import React from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Grid
} from '@mui/material';
import { useDashboardData } from '../hooks/useDashboardData';
import { ScanStatusCard } from '../components/dashboard/ScanStatusCard';
import { LogicResults } from '../components/dashboard/LogicResults';
import { TopStocks } from '../components/dashboard/TopStocks';
import { SystemStatus } from '../components/dashboard/SystemStatus';
import { ScoreEvaluationSection } from '../components/dashboard/ScoreEvaluationSection';
import { MainLayout } from '../layouts/MainLayout';
import { logger } from '../lib/logger';
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

  // 手動スコア評価用のサンプル銘柄データ（実際にはscanStatusから取得）
  const sampleStockForEvaluation = {
    code: '1234',
    name: 'テクノロジー株式会社'
  };

  // ローディング状態
  if (loading) {
    return (
      <MainLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  // エラー状態
  if (error) {
    return (
      <MainLayout>
        <Alert severity="error">
          エラーが発生しました: {error.message}
        </Alert>
      </MainLayout>
    );
  }

  const handleScanClick = async () => {
    try {
      logger.debug('Starting scan execution from dashboard');
      await executeScan();
      logger.info('Scan execution completed successfully');
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Scan execution failed', { error: error.message });
    }
  };

  // スコア評価保存後のコールバック
  const handleEvaluationSaved = () => {
    logger.info('Score evaluation saved, refreshing dashboard data');
    // 必要に応じてダッシュボードデータをリフレッシュ
  };


  return (
    <MainLayout>
      <Box data-testid="dashboard-container" sx={{ maxWidth: '1200px', mx: 'auto' }}>
        {/* ヘッダーセクション */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography 
            variant="h3" 
            sx={{ 
              fontSize: { xs: '1.75rem', sm: '2rem', md: '2.5rem' },
              fontWeight: 700,
              color: '#2d3748',
              mb: 2
            }}
          >
            🚀 ロジックスキャナーダッシュボード
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
            AI駆動の株式スキャニング & 手動スコア評価
          </Typography>
        </Box>

        {/* ダッシュボードグリッド */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* スキャン実行コントロール */}
          <Grid size={{ xs: 12, md: 6 }}>
            <ScanStatusCard
              scanStatus={scanStatus}
              isScanning={isScanning}
              scanProgress={scanProgress}
              onScanClick={handleScanClick}
            />
          </Grid>

          {/* システム状態 */}
          <Grid size={{ xs: 12, md: 6 }}>
            <SystemStatus />
          </Grid>
        </Grid>

        {/* ロジック結果表示 */}
        <LogicResults logicStatus={logicStatus} />

        {/* 検出結果セクション with 手動スコア評価 */}
        <Box sx={{ mt: 3 }}>
          <TopStocks>
            {/* 手動スコア評価セクションを TopStocks 内に統合 */}
            <ScoreEvaluationSection
              stockCode={sampleStockForEvaluation.code}
              stockName={sampleStockForEvaluation.name}
              logicType="logic_a"
              onEvaluationSaved={handleEvaluationSaved}
            />
          </TopStocks>
        </Box>
      </Box>
    </MainLayout>
  );
};

export default DashboardPage;