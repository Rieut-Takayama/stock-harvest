import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { naturalLightTheme } from './theme';
import { MainLayout } from './layouts/MainLayout';
import { SimpleDashboardPage } from './pages/SimpleDashboardPage';
import { AdminPage } from './pages/AdminPage';

/**
 * Stock Harvest AI - メインアプリケーション
 *
 * 要件定義準拠:
 * - 認証なし（公開ツール）
 * - P-001: ストップ高張り付き検索結果ページ (/)
 * - P-002: システム設定・管理ページ (/admin)
 */
function App() {
  return (
    <ThemeProvider theme={naturalLightTheme}>
      <CssBaseline />
      <Router>
        <MainLayout>
          <Routes>
            {/* P-001: ストップ高張り付き検索結果ページ */}
            <Route path="/" element={<SimpleDashboardPage />} />

            {/* P-002: システム設定・管理ページ */}
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </MainLayout>
      </Router>
    </ThemeProvider>
  );
}

export default App;