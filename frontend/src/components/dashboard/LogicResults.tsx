import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Typography
} from '@mui/material';
import type { LogicDetectionStatus } from '../../types';

interface LogicResultsProps {
  logicStatus: LogicDetectionStatus[];
}

export const LogicResults: React.FC<LogicResultsProps> = ({
  logicStatus
}) => {
  return (
    <Box sx={{ 
      display: 'grid', 
      gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
      gap: { xs: 2, sm: 3 }, 
      mb: { xs: 3, sm: 4 },
      px: { xs: 0, sm: 0 }
    }}>
      {logicStatus.map((logic, index) => (
        <Card key={logic.logicType} sx={{ 
          borderRadius: { xs: 3, sm: 4 },
          border: 'none',
          background: index === 0 
            ? 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)'
            : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)',
          color: 'white',
          minHeight: { xs: '200px', sm: '220px', md: '240px' },
          position: 'relative',
          overflow: 'hidden',
          transform: 'perspective(1000px) rotateX(0deg)',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: { xs: 'translateY(-5px)', md: 'perspective(1000px) rotateX(-5deg) translateY(-10px)' },
            boxShadow: '0 25px 80px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2)',
          }
        }}>
          {/* ロケットアイコン背景 */}
          <Box sx={{
            position: 'absolute',
            top: { xs: 15, sm: 20 },
            right: { xs: 15, sm: 20 },
            fontSize: { xs: '2.5rem', sm: '3rem' },
            opacity: 0.3
          }}>
            🚀
          </Box>
          
          <CardContent sx={{ 
            p: { xs: 2.5, sm: 3 }, 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column' 
          }}>
            {/* ロジックヘッダー */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="h5" sx={{ 
                fontWeight: 800, 
                mb: 1, 
                color: '#ffffff',
                textShadow: '0 2px 8px rgba(0, 0, 0, 0.5)',
                fontSize: { xs: '1.25rem', sm: '1.4rem', md: '1.5rem' }
              }}>
                ロジック{logic.logicType.charAt(logic.logicType.length - 1).toUpperCase()}
              </Typography>
              <Typography variant="h6" sx={{ 
                color: '#ffffff', 
                lineHeight: 1.4,
                fontWeight: 600,
                textShadow: '0 1px 4px rgba(0, 0, 0, 0.4)',
                fontSize: { xs: '0.9rem', sm: '1rem' },
                mb: 1
              }}>
                {logic.name}
              </Typography>
              <Typography variant="body2" sx={{ 
                color: '#ffffff', 
                fontSize: { xs: '0.75rem', sm: '0.8rem' },
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
                size="small"
                sx={{
                  bgcolor: 'rgba(0, 0, 0, 0.3)',
                  color: '#ffffff',
                  fontSize: { xs: '0.7rem', sm: '0.75rem' },
                  fontWeight: 700,
                  border: '1px solid rgba(255, 255, 255, 0.4)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)',
                  height: { xs: '20px', sm: '24px' }
                }}
              />
              <Typography variant="body2" sx={{ 
                fontSize: { xs: '0.7rem', sm: '0.75rem' }, 
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
  );
};

export default LogicResults;