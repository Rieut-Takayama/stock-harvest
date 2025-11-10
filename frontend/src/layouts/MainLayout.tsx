import { Box, Drawer, Toolbar } from '@mui/material';
import { useState } from 'react';
import type { ReactNode } from 'react';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';

interface MainLayoutProps {
  children: ReactNode;
}

const DRAWER_WIDTH = 240;

export const MainLayout = ({ children }: MainLayoutProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* ヘッダー */}
      <Header onMenuClick={handleDrawerToggle} />

      {/* サイドバー(レスポンシブDrawer) */}
      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        {/* モバイル用Drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              width: DRAWER_WIDTH,
              background: 'linear-gradient(180deg, #f0fff4 0%, #e6fffa 100%)',
              borderRight: '1px solid rgba(56, 161, 105, 0.1)',
            },
          }}
        >
          <Sidebar />
        </Drawer>

        {/* デスクトップ用Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              width: DRAWER_WIDTH,
              background: 'linear-gradient(180deg, #f0fff4 0%, #e6fffa 100%)',
              borderRight: '1px solid rgba(56, 161, 105, 0.1)',
            },
          }}
          open
        >
          <Sidebar />
        </Drawer>
      </Box>

      {/* メインコンテンツ */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          background: 'linear-gradient(135deg, #f9fafb 0%, #f0fff4 100%)',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};