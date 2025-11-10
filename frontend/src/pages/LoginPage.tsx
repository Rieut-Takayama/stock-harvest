import { useState } from 'react';
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  FormControlLabel, 
  Checkbox, 
  Alert,
  Divider
} from '@mui/material';
import { PublicLayout } from '../layouts/PublicLayout';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, useLocation } from 'react-router-dom';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password, rememberMe });
      navigate(from, { replace: true });
    } catch {
      setError('ログインに失敗しました。メールアドレスとパスワードを確認してください。');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (userType: 'user' | 'admin') => {
    if (userType === 'user') {
      setEmail('demo@example.com');
      setPassword('demo123');
    } else {
      setEmail('admin@example.com');
      setPassword('admin123');
    }
  };

  return (
    <PublicLayout maxWidth="sm">
      <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
        <Typography 
          variant="h4" 
          component="h1" 
          textAlign="center" 
          sx={{ 
            mb: 3, 
            color: 'primary.main',
            fontWeight: 700
          }}
        >
          ログイン
        </Typography>

        <Typography 
          variant="body2" 
          textAlign="center" 
          color="text.secondary" 
          sx={{ mb: 4 }}
        >
          Stock Harvest AI にようこそ
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          label="メールアドレス"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          margin="normal"
          required
          autoComplete="email"
          autoFocus
        />

        <TextField
          fullWidth
          label="パスワード"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          margin="normal"
          required
          autoComplete="current-password"
        />

        <FormControlLabel
          control={
            <Checkbox
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              color="primary"
            />
          }
          label="ログイン状態を保持する"
          sx={{ mt: 2, mb: 3 }}
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          size="large"
          disabled={loading}
          sx={{ 
            mb: 3, 
            py: 1.5,
            background: 'linear-gradient(45deg, #38a169, #4caf50)',
            '&:hover': {
              background: 'linear-gradient(45deg, #2f855a, #43a047)',
            },
          }}
        >
          {loading ? 'ログイン中...' : 'ログイン'}
        </Button>

        <Divider sx={{ mb: 3 }}>または</Divider>

        {/* デモアカウント */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'text.secondary' }}>
            デモアカウント
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
            <Button
              variant="outlined"
              onClick={() => handleDemoLogin('user')}
              sx={{ 
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  backgroundColor: 'primary.light',
                },
              }}
            >
              <Box sx={{ textAlign: 'left' }}>
                <Typography variant="subtitle2">一般ユーザー</Typography>
                <Typography variant="caption" display="block">
                  demo@example.com / demo123
                </Typography>
              </Box>
            </Button>

            <Button
              variant="outlined"
              onClick={() => handleDemoLogin('admin')}
              sx={{ 
                borderColor: 'secondary.main',
                color: 'secondary.main',
                '&:hover': {
                  borderColor: 'secondary.dark',
                  backgroundColor: 'secondary.light',
                },
              }}
            >
              <Box sx={{ textAlign: 'left' }}>
                <Typography variant="subtitle2">管理者</Typography>
                <Typography variant="caption" display="block">
                  admin@example.com / admin123
                </Typography>
              </Box>
            </Button>
          </Box>
        </Box>
      </Box>
    </PublicLayout>
  );
};