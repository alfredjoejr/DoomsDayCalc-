import { useEffect } from 'react';
import { X } from 'lucide-react';
import { CATEGORY_META, ERA_META } from '../../config/theme';
import type { MortalityEvent } from '../../types/mortality';
import { formatFullNumber, formatYearRange } from '../../utils/formatters';

interface EventDetailModalProps {
  event: MortalityEvent | null;
  onClose: () => void;
}

export function EventDetailModal({ event, onClose }: EventDetailModalProps) {
  useEffect(() => {
    if (!event) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [event, onClose]);

  if (!event) return null;

  const catMeta = CATEGORY_META[event.category];

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-event-title"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-card">
        <div className="modal-header">
          <div>
            <span
              className="category-badge"
              style={{
                color: catMeta.color,
                backgroundColor: catMeta.softBg,
                borderColor: `${catMeta.color}44`,
                marginBottom: 10,
              }}
            >
              <span className="pill-swatch" style={{ backgroundColor: catMeta.color }} />
              {catMeta.label} • {ERA_META[event.era].label}
            </span>
            <h2
              id="modal-event-title"
              className="font-display"
              style={{ fontSize: '1.55rem', fontWeight: 700 }}
            >
              {event.name}
            </h2>
            <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              {formatYearRange(event.startYear, event.endYear)} • {event.region}
            </div>
          </div>

          <button
            type="button"
            className="icon-close-btn"
            onClick={onClose}
            aria-label="Close event dossier"
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-stats-row">
          <div className="modal-stat-box">
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Midpoint Estimate
            </div>
            <div
              className="font-display tabular-nums"
              style={{ fontSize: '1.35rem', fontWeight: 700, color: catMeta.color }}
            >
              {formatFullNumber(event.deathsMid)}
            </div>
          </div>

          <div className="modal-stat-box">
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Uncertainty Range
            </div>
            <div className="font-mono tabular-nums" style={{ fontSize: '0.85rem', marginTop: 4 }}>
              {formatFullNumber(event.deathsLow)} – {formatFullNumber(event.deathsHigh)}
            </div>
          </div>

          <div className="modal-stat-box">
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              World Population Share
            </div>
            <div
              className="font-display tabular-nums"
              style={{ fontSize: '1.35rem', fontWeight: 700 }}
            >
              {event.worldPopPercent.toFixed(2)}%
            </div>
          </div>
        </div>

        <div>
          <h3 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
            Historical Context
          </h3>
          <p style={{ color: 'var(--text-primary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
            {event.summary} {event.historicalContext}
          </p>
        </div>

        <div>
          <h3 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Primary Mortality Drivers
          </h3>
          <div className="tag-list">
            {event.primaryCauses.map((cause) => (
              <span key={cause} className="cause-tag">
                {cause}
              </span>
            ))}
          </div>
        </div>

        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: 12,
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
          }}
        >
          <strong>Sources &amp; Scholarship:</strong> {event.sourceNote}
        </div>
      </div>
    </div>
  );
}
