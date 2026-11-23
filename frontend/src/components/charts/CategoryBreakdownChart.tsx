import type { FilterState } from '../../types/mortality';
import { ServerPlotFrame } from './ServerPlotFrame';

interface CategoryBreakdownChartProps {
  filters: FilterState;
  retryNonce: number;
  onRetryApi: () => void;
}

export function CategoryBreakdownChart({
  filters,
  retryNonce,
  onRetryApi,
}: CategoryBreakdownChartProps) {
  return (
    <section className="panel-card" aria-label="Mortality Share by Category">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Share by Cause</h2>
          <p className="panel-subtitle">Proportional toll across mortality categories</p>
        </div>
      </div>

      <ServerPlotFrame
        plotType="category_donut"
        filters={filters}
        alt="Mortality Cause Breakdown Donut rendered by Matplotlib"
        minHeight={280}
        retryNonce={retryNonce}
        onRetryApi={onRetryApi}
      />
    </section>
  );
}
