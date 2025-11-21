import React from 'react';
import {
  Box,
  Button,
  Card,
  Chip,
  Typography
} from '@mui/material';

interface StockItem {
  code: string;
  name: string;
  status: string;
}

interface TopStocksProps {
  stocks?: StockItem[];
}

export const TopStocks: React.FC<TopStocksProps> = ({
  stocks = [
    { code: '4819', name: 'デジタルガレージ', status: '分析中' },
    { code: '2158', name: 'フロンテッジ', status: '分析中' },
    { code: '4477', name: 'BASE', status: '分析中' }
  ]
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" sx={{ 
        mb: { xs: 2, sm: 3 }, 
        fontWeight: 800, 
        color: '#ffffff', 
        textAlign: 'center',
        textShadow: '0 3px 8px rgba(0,0,0,0.6)',
        fontSize: { xs: '1.2rem', sm: '1.4rem', md: '1.6rem' },
        background: 'rgba(0, 0, 0, 0.4)',
        borderRadius: '30px',
        px: { xs: 3, sm: 4 },
        py: { xs: 1.5, sm: 2 },
        display: 'inline-block',
        border: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        🎯 AI検出: ストップ高候補銘柄
      </Typography>
      
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, 
        gap: { xs: 2, sm: 3 },
        maxWidth: { xs: '100%', sm: '800px' },
        mx: 'auto',
        px: { xs: 1, sm: 0 }
      }}>
        {stocks.map((stock) => (
          <Card key={stock.code} sx={{ 
            borderRadius: { xs: 2, sm: 3 }, 
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            p: { xs: 2.5, sm: 3 },
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': { 
              transform: { xs: 'translateY(-4px)', sm: 'translateY(-8px)' },
              boxShadow: '0 16px 48px rgba(0, 0, 0, 0.2)',
              background: 'rgba(255, 255, 255, 1)',
            }
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ 
                fontWeight: 600,
                fontSize: { xs: '0.8rem', sm: '0.875rem' }
              }}>
                {stock.code}
              </Typography>
              <Chip 
                label={stock.status}
                size="small"
                sx={{ 
                  fontSize: { xs: '0.65rem', sm: '0.7rem' }, 
                  bgcolor: '#2563eb', 
                  color: '#ffffff',
                  fontWeight: 600,
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  height: { xs: '20px', sm: '24px' }
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ 
              mb: 2,
              fontSize: { xs: '0.8rem', sm: '0.875rem' }
            }}>
              {stock.name}
            </Typography>
            <Button
              size="small"
              variant="contained"
              fullWidth
              sx={{ 
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                color: 'white',
                fontSize: { xs: '0.7rem', sm: '0.75rem' },
                fontWeight: 600,
                borderRadius: '20px',
                textTransform: 'none',
                boxShadow: '0 4px 16px rgba(37, 99, 235, 0.3)',
                py: { xs: 0.5, sm: 1 },
                minHeight: { xs: '32px', sm: '36px' },
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
  );
};

export default TopStocks;