import React from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Typography
} from '@mui/material';
import {
  Search as SearchIcon,
  AccessTime as TimeIcon
} from '@mui/icons-material';
import type { ScanStatus } from '../../types';

interface ScanStatusCardProps {
  scanStatus: ScanStatus | null;
  isScanning: boolean;
  scanProgress: number;
  onScanClick: () => void;
}

export const ScanStatusCard: React.FC<ScanStatusCardProps> = ({
  scanStatus,
  isScanning,
  scanProgress,
  onScanClick
}) => {
  return (
    <>
      {/* スキャン実行コントロール */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 3 }, 
        mb: { xs: 3, sm: 4 }, 
        alignItems: { xs: 'stretch', sm: 'center' },
        justifyContent: 'center',
        px: { xs: 1, sm: 0 }
      }}>
        <Button
          variant="contained"
          startIcon={isScanning ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
          onClick={onScanClick}
          disabled={isScanning}
          sx={{
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            color: 'white',
            px: { xs: 3, sm: 4 },
            py: { xs: 1.5, sm: 2 },
            borderRadius: '50px',
            fontSize: { xs: '0.95rem', sm: '1.1rem' },
            fontWeight: 600,
            boxShadow: '0 8px 32px rgba(37, 99, 235, 0.4)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            textTransform: 'none',
            minHeight: { xs: '48px', sm: '56px' },
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

      {/* スキャン時刻表示 */}
      <Typography variant="body2" sx={{ 
        textAlign: 'center', 
        color: '#ffffff', 
        mb: { xs: 3, sm: 4 },
        fontSize: { xs: '0.8rem', sm: '0.9rem' },
        fontWeight: 500,
        letterSpacing: '0.5px',
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '20px',
        px: { xs: 2.5, sm: 3 },
        py: 1,
        display: 'inline-block',
        mx: 'auto'
      }}>
        ⏰ 最終スキャン: 19:44:15
      </Typography>
    </>
  );
};

export default ScanStatusCard;