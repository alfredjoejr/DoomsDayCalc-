import { useState } from 'react';
import type { FilterState, MatplotlibPlotType } from '../../types/mortality';
import { ServerPlotFrame } from './ServerPlotFrame';

interface DeepDiveChartProps {
  filters: FilterState;
  retryNonce: number;
  onRetryApi: () => void;
  onSelectEventId: (eventId: string) => void;
}

type DeepDivePlot = Extract<
  MatplotlibPlotType,
  'world_pop_scatter' | 'log_timeline' | 'category_boxplot' | 'era_heatmap'
>;

const PLOT_OPTIONS: Array<{ id: DeepDivePlot; label: string }> = [
  { id: 'world_pop_scatter', label: 'World Population Impact (%)' },
  { id: 'log_timeline', label: 'Uncertainty Bounds (Log)' },
  { id: 'category_boxplot', label: 'Category Spread (Boxplot)' },
  { id: 'era_heatmap', label: 'Era × Cause Heatmap' },
];

export function DeepDiveChart({
  filters,
  retryNonce,
  onRetryApi,
  onSelectEventId,
}: DeepDiveChartProps) {
  const [plotType, setPlotType] = useState<DeepDivePlot>('world_pop_scatter');
  const isInteractive = plotType !== 'era_heatmap';

  return (
    <section className="panel-card" aria-label="Statistical Deep Dive">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Statistical Deep Dive</h2>
          <p className="panel-subtitle">
            {isInteractive
              ? 'Distribution, uncertainty bounds, and demographic shock • Click any circle to inspect'
              : 'Era × Cause fatality intensity matrix across history'}
          </p>
        </div>

        <select
          className="select-control"
          value={plotType}
          onChange={(e) => setPlotType(e.target.value as DeepDivePlot)}
          aria-label="Select analytical plot"
        >
          {PLOT_OPTIONS.map((opt) => (
            <option key={opt.id} value={opt.id}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <ServerPlotFrame
        plotType={plotType}
        filters={filters}
        alt={`Matplotlib ${plotType} statistical chart`}
        minHeight={330}
        retryNonce={retryNonce}
        onRetryApi={onRetryApi}
        interactive={isInteractive}
        onSelectEventId={onSelectEventId}
      />
    </section>
  );
}
