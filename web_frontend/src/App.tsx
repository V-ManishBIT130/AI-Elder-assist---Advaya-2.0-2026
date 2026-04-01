import { Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './components/AppShell';
import AlertsPage from './pages/AlertsPage';
import CallLogsPage from './pages/CallLogsPage';
import HealthTrendsPage from './pages/HealthTrendsPage';
import MedicationsPage from './pages/MedicationsPage';
import OverviewPage from './pages/OverviewPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/overview" replace />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/health-trends" element={<HealthTrendsPage />} />
        <Route path="/medications" element={<MedicationsPage />} />
        <Route path="/call-logs" element={<CallLogsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/overview" replace />} />
    </Routes>
  );
}

export default App;
