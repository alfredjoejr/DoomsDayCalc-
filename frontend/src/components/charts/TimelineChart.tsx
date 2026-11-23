import type { FilterState } from '../../types/mortality';
import { ServerPlotFrame } from './ServerPlotFrame';

interface TimelineChartProps {
  filters: FilterState;
  eventCount: number;
  retryNonce: number;
  onRetryApi: () => void;
  onSelectEventId: (eventId: string) => void;
}

export function TimelineChart({
  filters,
  eventCount,
  retryNonce,
  onRetryApi,
  onSelectEventId,
}: TimelineChartProps) {
  return (
    <section className="panel-card" aria-label="Historical Mortality Timeline">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Chronological Mortality Magnitude</h2>
          <p className="panel-subtitle">
            {filters.scaleMode === 'log'
              ? 'Matplotlib Log₁₀ timeline • Click any circle for full context'
              : 'Matplotlib linear timeline • Click any circle for full context'}
          </p>
        </div>
        <span className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Matplotlib • {eventCount} events
        </span>
      </div>

      <ServerPlotFrame
        plotType="timeline"
        filters={filters}
        alt="Chronological Mortality Magnitude rendered by Matplotlib"
        minHeight={310}
        retryNonce={retryNonce}
        onRetryApi={onRetryApi}
        interactive
        onSelectEventId={onSelectEventId}
      />
    </section>
  );
}
