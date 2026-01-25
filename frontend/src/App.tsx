import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { naturalLightTheme } from './theme';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { AdminPage } from './pages/AdminPage';
import { ContactSupportPage } from './pages/ContactSupportPage';
import { AlertsPage } from './pages/AlertsPage';

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
            <Route path="/" element={<DashboardPage />} />

            {/* P-002: システム設定・管理ページ */}
            <Route path="/admin" element={<AdminPage />} />

            {/* P-003: お問い合わせサポートページ */}
            <Route path="/contact-support" element={<ContactSupportPage />} />

            {/* P-004: アラート設定ページ */}
            <Route path="/alerts" element={<AlertsPage />} />
          </Routes>
        </MainLayout>
      </Router>
    </ThemeProvider>
  );
}

export default App;