import React from 'react';
import {
  Box,
  Card,
  Typography
} from '@mui/material';

interface StatCard {
  icon: string;
  value: string | number;
  label: string;
  valueColor?: string;
}

interface SystemStatusProps {
  stats?: StatCard[];
}

export const SystemStatus: React.FC<SystemStatusProps> = ({
  stats = [
    { icon: '📊', value: 3, label: 'アクティブロジック' },
    { icon: '📈', value: 2, label: '今日発見した' },
    { icon: '🎯', value: '+18.5%', label: '平均リターン', valueColor: '#059669' }
  ]
}) => {
  return (
    <Box sx={{ 
      display: 'grid', 
      gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, 
      gap: { xs: 2, sm: 3 }, 
      mb: { xs: 3, sm: 4 },
      maxWidth: { xs: '100%', sm: '700px' },
      mx: 'auto',
      px: { xs: 1, sm: 0 }
    }}>
      {stats.map((stat, index) => (
        <Card key={index} sx={{ 
          borderRadius: { xs: 2, sm: 3 }, 
          background: 'rgba(255, 255, 255, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          textAlign: 'center', 
          p: { xs: 2, sm: 2.5, md: 3 },
          transition: 'all 0.3s ease',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            transform: 'translateY(-5px)',
            boxShadow: '0 15px 45px rgba(0, 0, 0, 0.2)',
            background: 'rgba(255, 255, 255, 1)'
          }
        }}>
          <Typography variant="h4" sx={{ 
            mb: 1, 
            fontSize: { xs: '1.5rem', sm: '1.8rem', md: '2rem' } 
          }}>
            {stat.icon}
          </Typography>
          <Typography variant="h4" sx={{ 
            fontWeight: 800, 
            color: stat.valueColor || '#1a202c', 
            fontSize: { xs: '1.8rem', sm: '2rem', md: '2.25rem' } 
          }}>
            {stat.value}
          </Typography>
          <Typography variant="body2" sx={{ 
            color: '#4a5568', 
            fontWeight: 500, 
            fontSize: { xs: '0.75rem', sm: '0.875rem' } 
          }}>
            {stat.label}
          </Typography>
        </Card>
      ))}
    </Box>
  );
};

export default SystemStatus;