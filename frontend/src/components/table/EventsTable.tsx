import { useEffect, useState } from 'react';
import { CATEGORY_META, ERA_META } from '../../config/theme';
import type { MortalityEvent } from '../../types/mortality';
import { formatCompactNumber, formatYearRange } from '../../utils/formatters';

interface EventsTableProps {
  events: MortalityEvent[];
  onSelectEvent: (event: MortalityEvent) => void;
}

const PAGE_SIZE = 10;

export function EventsTable({ events, onSelectEvent }: EventsTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    setCurrentPage(1);
  }, [events]);

  const totalPages = Math.max(1, Math.ceil(events.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * PAGE_SIZE;
  const visibleEvents = isExpanded
    ? events
    : events.slice(startIndex, startIndex + PAGE_SIZE);

  const rangeStart = events.length === 0 ? 0 : isExpanded ? 1 : startIndex + 1;
  const rangeEnd = isExpanded
    ? events.length
    : Math.min(startIndex + PAGE_SIZE, events.length);

  return (
    <section className="panel-card" aria-label="Historical Mortality Ledger">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Historical Ledger</h2>
          <p className="panel-subtitle">
            Showing {rangeStart}–{rangeEnd} of {events.length} records • Click any row for context
          </p>
        </div>

        {events.length > PAGE_SIZE && (
          <button
            type="button"
            className="secondary-btn"
            onClick={() => setIsExpanded((prev) => !prev)}
          >
            {isExpanded ? 'Collapse to 10 / page' : `Expand all (${events.length})`}
          </button>
        )}
      </div>

      {events.length === 0 ? (
        <div className="empty-state">No historical events match your active filters.</div>
      ) : (
        <>
          <div className="table-scroll">
            <table className="events-table">
              <thead>
                <tr>
                  <th>Event</th>
                  <th>Period</th>
                  <th>Cause</th>
                  <th style={{ textAlign: 'right' }}>Est. Fatalities</th>
                </tr>
              </thead>
              <tbody>
                {visibleEvents.map((ev) => {
                  const catMeta = CATEGORY_META[ev.category];
                  return (
                    <tr
                      key={ev.id}
                      onClick={() => onSelectEvent(ev)}
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onSelectEvent(ev);
                        }
                      }}
                    >
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {ev.name}
                        </div>
                        <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                          {ev.region}
                        </div>
                      </td>
                      <td>
                        <div className="tabular-nums font-mono" style={{ fontSize: '0.8rem' }}>
                          {formatYearRange(ev.startYear, ev.endYear)}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {ERA_META[ev.era].label}
                        </div>
                      </td>
                      <td>
                        <span
                          className="category-badge"
                          style={{
                            color: catMeta.color,
                            backgroundColor: catMeta.softBg,
                            borderColor: `${catMeta.color}44`,
                          }}
                        >
                          <span
                            className="pill-swatch"
                            style={{ backgroundColor: catMeta.color }}
                          />
                          {catMeta.shortLabel}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="tabular-nums" style={{ fontWeight: 600 }}>
                          {formatCompactNumber(ev.deathsMid)}
                        </div>
                        <div
                          className="tabular-nums font-mono"
                          style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}
                        >
                          {ev.worldPopPercent.toFixed(2)}% world pop.
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {!isExpanded && totalPages > 1 && (
            <nav className="ledger-pagination" aria-label="Ledger pagination">
              <span className="pagination-meta tabular-nums">
                Page {safePage} of {totalPages}
              </span>
              <div className="page-controls">
                <button
                  type="button"
                  className="page-btn"
                  disabled={safePage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                >
                  Prev
                </button>
                {Array.from({ length: totalPages }, (_, idx) => idx + 1).map(
                  (pageNum) => (
                    <button
                      key={pageNum}
                      type="button"
                      className={`page-btn tabular-nums ${pageNum === safePage ? 'active' : ''}`}
                      onClick={() => setCurrentPage(pageNum)}
                      aria-current={pageNum === safePage ? 'page' : undefined}
                    >
                      {pageNum}
                    </button>
                  ),
                )}
                <button
                  type="button"
                  className="page-btn"
                  disabled={safePage >= totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                >
                  Next
                </button>
              </div>
            </nav>
          )}
        </>
      )}
    </section>
  );
}
