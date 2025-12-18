import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { naturalLightTheme } from './theme';
import { SimpleDashboardPage } from './pages/SimpleDashboardPage';
import { AlertsPage } from './pages/AlertsPage';
import { ContactPage } from './pages/ContactPage';

function App() {
  return (
    <ThemeProvider theme={naturalLightTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<SimpleDashboardPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;