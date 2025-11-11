import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { naturalLightTheme } from './theme';
import { DashboardPage } from './pages/DashboardPage';

function App() {
  return (
    <ThemeProvider theme={naturalLightTheme}>
      <CssBaseline />
      <DashboardPage />
    </ThemeProvider>
  );
}

export default App;