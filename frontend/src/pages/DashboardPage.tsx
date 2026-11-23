import { useState } from 'react';
import { CategoryBreakdownChart } from '../components/charts/CategoryBreakdownChart';
import { DeepDiveChart } from '../components/charts/DeepDiveChart';
import { EraComparisonChart } from '../components/charts/EraComparisonChart';
import { TimelineChart } from '../components/charts/TimelineChart';
import { FilterBar } from '../components/filters/FilterBar';
import { EventDetailModal } from '../components/table/EventDetailModal';
import { EventsTable } from '../components/table/EventsTable';
import { ALL_CATEGORIES } from '../config/theme';
import { useMortalityAnalytics } from '../hooks/useMortalityAnalytics';
import type { MortalityCategory, MortalityEvent } from '../types/mortality';
import { formatCompactNumber } from '../utils/formatters';

interface DashboardPageProps {
  events: MortalityEvent[];
  retryNonce: number;
  onRetryApi: () => void;
}

export function DashboardPage({
  events,
  retryNonce,
  onRetryApi,
}: DashboardPageProps) {
  const {
    filters,
    filteredEvents,
    kpiSummary,
    isolateCategory,
    setSelectedEra,
    setScaleMode,
    resetFilters,
  } = useMortalityAnalytics(events);

  const [selectedEvent, setSelectedEvent] = useState<MortalityEvent | null>(null);

  const handleSelectEventId = (eventId: string) => {
    const found = events.find((ev) => ev.id === eventId);
    if (found) setSelectedEvent(found);
  };

  const handleCategoryChange = (cat: MortalityCategory | 'all') => {
    if (cat === 'all') {
      if (filters.selectedCategories.length < ALL_CATEGORIES.length) {
        resetFilters();
      }
      return;
    }
    if (
      filters.selectedCategories.length === 1 &&
      filters.selectedCategories[0] === cat
    ) {
      return;
    }
    isolateCategory(cat);
  };

  return (
    <main className="main-content">
      <div className="container" style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
        <section className="page-intro">
          <div>
            <h1 className="page-title">Chronicle of Human Mortality</h1>
            <p className="page-subtitle">
              Major mass-mortality events across recorded history (430 BCE – Present)
            </p>
          </div>

          <div className="inline-stats">
            <div className="inline-stat">
              <span className="inline-stat-label">Total Fatalities</span>
              <span className="inline-stat-value tabular-nums">
                {formatCompactNumber(kpiSummary.totalDeathsMid)}
              </span>
            </div>
            <div className="inline-stat">
              <span className="inline-stat-label">Deadliest Event</span>
              <span className="inline-stat-value">
                {kpiSummary.deadliestEvent ? kpiSummary.deadliestEvent.name : '—'}
              </span>
            </div>
            <div className="inline-stat">
              <span className="inline-stat-label">Events</span>
              <span className="inline-stat-value tabular-nums">
                {kpiSummary.filteredCount} / {kpiSummary.totalCatalogCount}
              </span>
            </div>
          </div>
        </section>

        <FilterBar
          filters={filters}
          onCategoryChange={handleCategoryChange}
          onEraChange={setSelectedEra}
          onScaleChange={setScaleMode}
        />

        <TimelineChart
          filters={filters}
          eventCount={filteredEvents.length}
          retryNonce={retryNonce}
          onRetryApi={onRetryApi}
          onSelectEventId={handleSelectEventId}
        />

        <div className="charts-two-col-equal">
          <CategoryBreakdownChart
            filters={filters}
            retryNonce={retryNonce}
            onRetryApi={onRetryApi}
          />
          <EraComparisonChart
            filters={filters}
            retryNonce={retryNonce}
            onRetryApi={onRetryApi}
          />
        </div>

        <DeepDiveChart
          filters={filters}
          retryNonce={retryNonce}
          onRetryApi={onRetryApi}
          onSelectEventId={handleSelectEventId}
        />

        <EventsTable
          events={filteredEvents}
          onSelectEvent={setSelectedEvent}
        />
      </div>

      <EventDetailModal
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />
    </main>
  );
}
