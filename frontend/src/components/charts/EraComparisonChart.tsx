import type { FilterState } from '../../types/mortality';
import { ServerPlotFrame } from './ServerPlotFrame';

interface EraComparisonChartProps {
  filters: FilterState;
  retryNonce: number;
  onRetryApi: () => void;
}

export function EraComparisonChart({
  filters,
  retryNonce,
  onRetryApi,
}: EraComparisonChartProps) {
  return (
    <section className="panel-card" aria-label="Era Comparison Stacked Chart">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Mortality Distribution Across Historical Eras</h2>
          <p className="panel-subtitle">
            Server-rendered Matplotlib stacked bar chart by era and cause category
          </p>
        </div>
      </div>

      <ServerPlotFrame
        plotType="era_stacked"
        filters={filters}
        alt="Mortality Distribution Across Historical Eras rendered by Matplotlib"
        minHeight={320}
        retryNonce={retryNonce}
        onRetryApi={onRetryApi}
      />
    </section>
  );
}
