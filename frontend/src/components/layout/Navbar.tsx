import { Activity, RefreshCw } from 'lucide-react';

interface NavbarProps {
  apiSource: 'fastapi' | 'mock';
  dbConnected: boolean;
  onRetryApi: () => void;
}

export function Navbar({ apiSource, dbConnected, onRetryApi }: NavbarProps) {
  const isLive = apiSource === 'fastapi';
  const label = isLive
    ? dbConnected
      ? 'Live • PostgreSQL'
      : 'Live'
    : 'Backend Offline';

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <div className="brand-group">
          <div className="brand-mark" aria-hidden="true">
            <Activity size={18} />
          </div>
          <span className="brand-title">DoomsDayCalc</span>
        </div>

        <button
          type="button"
          onClick={onRetryApi}
          className={`engine-status-pill ${!isLive ? 'mock' : ''}`}
          title="FastAPI + Aiven PostgreSQL + Matplotlib status"
        >
          <span className="status-dot" />
          {label}
          {!isLive && <RefreshCw size={12} />}
        </button>
      </div>
    </header>
  );
}
