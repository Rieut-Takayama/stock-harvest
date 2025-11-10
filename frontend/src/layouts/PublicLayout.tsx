import { Box, AppBar, Toolbar, Typography, Container, Paper } from '@mui/material';
import type { ReactNode } from 'react';

interface PublicLayoutProps {
  children: ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
}

export const PublicLayout = ({ children, maxWidth = 'sm' }: PublicLayoutProps) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #f0fff4 0%, #e6fffa 50%, #f7fafc 100%)',
      }}
    >
      {/* ヘッダー */}
      <AppBar 
        position="static" 
        elevation={0} 
        sx={{ 
          background: 'transparent',
          borderBottom: '1px solid rgba(56, 161, 105, 0.1)',
        }}
      >
        <Toolbar>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'primary.main',
              fontWeight: 600,
            }}
          >
            Stock Harvest AI
          </Typography>
        </Toolbar>
      </AppBar>

      {/* メインコンテンツ(中央揃え) */}
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Container maxWidth={maxWidth}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 4, 
              borderRadius: 3,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(56, 161, 105, 0.1)',
            }}
          >
            {children}
          </Paper>
        </Container>
      </Box>
    </Box>
  );
};