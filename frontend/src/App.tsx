import { useCallback, useEffect, useState } from 'react';
import { Footer } from './components/layout/Footer';
import { Navbar } from './components/layout/Navbar';
import { HISTORICAL_EVENTS } from './data/historicalEvents';
import { DashboardPage } from './pages/DashboardPage';
import { checkBackendHealth, fetchMortalityEvents } from './services/mortalityApi';
import type { MortalityEvent } from './types/mortality';

export default function App() {
  const [events, setEvents] = useState<MortalityEvent[]>(HISTORICAL_EVENTS);
  const [apiSource, setApiSource] = useState<'fastapi' | 'mock'>('mock');
  const [dbConnected, setDbConnected] = useState(false);
  const [retryNonce, setRetryNonce] = useState(0);

  const syncBackend = useCallback(async () => {
    const [health, data] = await Promise.all([
      checkBackendHealth(),
      fetchMortalityEvents(),
    ]);
    setEvents(data.events);
    setApiSource(health.online && data.source === 'fastapi' ? 'fastapi' : 'mock');
    setDbConnected(Boolean(health.online && health.dbConnected));
  }, []);

  useEffect(() => {
    void syncBackend();
  }, [syncBackend]);

  const handleRetryApi = useCallback(() => {
    setRetryNonce((n) => n + 1);
    void syncBackend();
  }, [syncBackend]);

  return (
    <div className="app-shell">
      <Navbar
        apiSource={apiSource}
        dbConnected={dbConnected}
        onRetryApi={handleRetryApi}
      />
      <DashboardPage
        events={events}
        retryNonce={retryNonce}
        onRetryApi={handleRetryApi}
      />
      <Footer />
    </div>
  );
}
