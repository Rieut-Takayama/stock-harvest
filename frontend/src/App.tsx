import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { naturalLightTheme } from './theme';
import { SimpleDashboardPage } from './pages/SimpleDashboardPage';

function App() {
  return (
    <ThemeProvider theme={naturalLightTheme}>
      <CssBaseline />
      <SimpleDashboardPage />
    </ThemeProvider>
  );
}

export default App;