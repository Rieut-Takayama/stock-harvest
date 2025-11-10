import { AppBar, Toolbar, Typography, IconButton, Avatar, Menu, MenuItem, Box } from '@mui/material';
import { Menu as MenuIcon, AccountCircle, Notifications } from '@mui/icons-material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header = ({ onMenuClick }: HeaderProps) => {
  // 認証なし個人利用版 - ダミーユーザー
  const user = { name: '個人利用者', avatar: null };
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // 認証なしなのでダッシュボードに留まる
    handleUserMenuClose();
  };

  return (
    <AppBar
      position="fixed"
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: 'linear-gradient(90deg, #38a169 0%, #4caf50 100%)',
        boxShadow: '0 2px 10px rgba(56, 161, 105, 0.2)',
      }}
    >
      <Toolbar>
        {/* モバイルメニューボタン */}
        {onMenuClick && (
          <IconButton
            color="inherit"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
        )}

        {/* ロゴ */}
        <Typography 
          variant="h6" 
          noWrap 
          sx={{ 
            flexGrow: 1,
            fontWeight: 700,
            color: 'white',
          }}
        >
          Stock Harvest AI
        </Typography>

        {/* 通知アイコン */}
        <IconButton color="inherit" sx={{ mr: 1 }}>
          <Notifications />
        </IconButton>

        {/* ユーザーメニュー */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography 
            variant="body2" 
            sx={{ 
              mr: 2, 
              display: { xs: 'none', md: 'block' },
              color: 'white',
            }}
          >
            {user?.name || 'ゲスト'}
          </Typography>
          
          <IconButton color="inherit" onClick={handleUserMenuClick}>
            {user?.avatar ? (
              <Avatar src={user.avatar} sx={{ width: 32, height: 32 }} />
            ) : (
              <AccountCircle />
            )}
          </IconButton>
        </Box>

        {/* ユーザーメニュー */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleUserMenuClose}
          sx={{ mt: '45px' }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={() => { navigate('/profile'); handleUserMenuClose(); }}>
            プロフィール
          </MenuItem>
          <MenuItem onClick={() => { navigate('/settings'); handleUserMenuClose(); }}>
            設定
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            ログアウト
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};