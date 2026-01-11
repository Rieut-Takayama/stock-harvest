import { 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  Toolbar,
  Typography,
  Box,
  Chip
} from '@mui/material';
import {
  Dashboard,
  AdminPanelSettings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  // 認証なし個人利用版 - ダミーユーザー
  const user = { name: '個人利用者', role: 'user' };

  // 要件定義準拠のメニュー構成
  const userMenuItems = [
    {
      text: '検索結果',
      icon: <Dashboard />,
      path: '/',
      roles: ['user', 'admin'],
      description: 'ストップ高張り付き銘柄'
    },
  ];

  const adminMenuItems = [
    {
      text: 'システム設定',
      icon: <AdminPanelSettings />,
      path: '/admin',
      roles: ['admin'],
      description: 'バッチ処理・条件調整'
    },
  ];

  const hasAccess = (roles: string[]) => roles.includes(user?.role || 'guest');

  return (
    <div>
      <Toolbar />
      
      {/* ユーザー情報 */}
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 600 }}>
          {user?.name || 'ゲスト'}
        </Typography>
        <Chip 
          label={user?.role === 'admin' ? '管理者' : 'ユーザー'} 
          size="small" 
          color={user?.role === 'admin' ? 'secondary' : 'primary'}
          sx={{ mt: 0.5 }}
        />
      </Box>

      <Divider sx={{ mx: 2, borderColor: 'rgba(56, 161, 105, 0.2)' }} />

      {/* メインメニュー */}
      <List sx={{ px: 1 }}>
        {userMenuItems
          .filter(item => hasAccess(item.roles))
          .map((item) => (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  mx: 1,
                  '&.Mui-selected': {
                    background: 'linear-gradient(135deg, #38a169, #4caf50)',
                    color: 'white',
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                    '&:hover': {
                      background: 'linear-gradient(135deg, #2f855a, #43a047)',
                    },
                  },
                  '&:hover': {
                    background: 'rgba(56, 161, 105, 0.1)',
                  },
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  secondary={item.description}
                  primaryTypographyProps={{
                    fontWeight: location.pathname === item.path ? 600 : 400,
                  }}
                  secondaryTypographyProps={{
                    fontSize: '0.75rem',
                    sx: { opacity: 0.7 },
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
      </List>

      {/* 管理者メニュー */}
      {user?.role === 'admin' && (
        <>
          <Divider sx={{ mx: 2, my: 1, borderColor: 'rgba(56, 161, 105, 0.2)' }} />
          
          <Typography 
            variant="overline" 
            sx={{ 
              px: 3, 
              color: 'text.secondary', 
              fontWeight: 600,
              display: 'block',
              mb: 1
            }}
          >
            管理機能
          </Typography>
          
          <List sx={{ px: 1 }}>
            {adminMenuItems.map((item) => (
              <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => navigate(item.path)}
                  sx={{
                    borderRadius: 2,
                    mx: 1,
                    '&.Mui-selected': {
                      background: 'linear-gradient(135deg, #f56565, #fc8181)',
                      color: 'white',
                      '& .MuiListItemIcon-root': {
                        color: 'white',
                      },
                      '&:hover': {
                        background: 'linear-gradient(135deg, #e53e3e, #f56565)',
                      },
                    },
                    '&:hover': {
                      background: 'rgba(245, 101, 101, 0.1)',
                    },
                  }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText 
                    primary={item.text}
                    secondary={item.description}
                    primaryTypographyProps={{
                      fontWeight: location.pathname === item.path ? 600 : 400,
                    }}
                    secondaryTypographyProps={{
                      fontSize: '0.75rem',
                      sx: { opacity: 0.7 },
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </>
      )}

      {/* フッター */}
      <Box sx={{ position: 'absolute', bottom: 16, left: 16, right: 16 }}>
        <Typography 
          variant="caption" 
          sx={{ 
            display: 'block', 
            textAlign: 'center', 
            color: 'text.secondary',
            opacity: 0.6
          }}
        >
          v1.0.0 | Stock Harvest AI
        </Typography>
      </Box>
    </div>
  );
};