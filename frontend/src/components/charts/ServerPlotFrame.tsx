import { useEffect, useState } from 'react';
import { RefreshCw, ServerOff } from 'lucide-react';
import { CATEGORY_META } from '../../config/theme';
import {
  buildMatplotlibChartUrl,
  fetchInteractiveMatplotlibChart,
} from '../../services/mortalityApi';
import type {
  ChartFormat,
  ChartHotspot,
  FilterState,
  MatplotlibPlotType,
} from '../../types/mortality';
import { formatCompactNumber } from '../../utils/formatters';

interface ServerPlotFrameProps {
  plotType: MatplotlibPlotType;
  filters: FilterState;
  alt: string;
  dpi?: 150 | 300;
  theme?: 'obsidian_dark' | 'publication_light';
  format?: ChartFormat;
  minHeight?: number;
  retryNonce?: number;
  onRetryApi?: () => void;
  interactive?: boolean;
  onSelectEventId?: (eventId: string) => void;
}

export function ServerPlotFrame({
  plotType,
  filters,
  alt,
  dpi = 150,
  theme = 'obsidian_dark',
  format = 'png',
  minHeight = 290,
  retryNonce = 0,
  onRetryApi,
  interactive = false,
  onSelectEventId,
}: ServerPlotFrameProps) {
  const baseUrl = buildMatplotlibChartUrl({
    plotType,
    dpi,
    theme,
    format,
    filters,
  });
  const imageSrc = retryNonce > 0 ? `${baseUrl}&_r=${retryNonce}` : baseUrl;

  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [interactiveSrc, setInteractiveSrc] = useState<string>('');
  const [hotspots, setHotspots] = useState<ChartHotspot[]>([]);
  const [hoveredSpot, setHoveredSpot] = useState<ChartHotspot | null>(null);

  useEffect(() => {
    setIsLoading(true);
    setHasError(false);
    setHoveredSpot(null);

    if (!interactive) {
      return;
    }

    const controller = new AbortController();
    fetchInteractiveMatplotlibChart(
      { plotType, dpi, theme, format, filters },
      controller.signal,
    )
      .then((payload) => {
        setInteractiveSrc(payload.imageDataUrl);
        setHotspots(payload.hotspots);
        setIsLoading(false);
        setHasError(false);
      })
      .catch((err) => {
        if ((err as Error).name === 'AbortError') return;
        setIsLoading(false);
        setHasError(true);
      });

    return () => controller.abort();
  }, [interactive, plotType, dpi, theme, format, filters, retryNonce]);

  const activeSrc = interactive ? interactiveSrc : imageSrc;

  return (
    <div
      className={`server-plot-frame ${theme === 'publication_light' ? 'light' : 'dark'}`}
      style={{ minHeight }}
    >
      {hasError ? (
        <div className="server-plot-offline">
          <ServerOff size={24} color="#fcd34d" />
          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
            FastAPI Matplotlib Engine Offline
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', maxWidth: 420 }}>
            Run <span className="font-mono">.\start-dev.ps1</span> or start the backend to render charts.
          </p>
          {onRetryApi && (
            <button type="button" className="secondary-btn" onClick={onRetryApi}>
              <RefreshCw size={14} />
              Retry
            </button>
          )}
        </div>
      ) : (
        <>
          {isLoading && (
            <div className="server-plot-loading">
              <span className="font-mono" style={{ fontSize: '0.78rem' }}>
                Rendering figure…
              </span>
            </div>
          )}

          {activeSrc && (
            <div className="server-plot-stage">
              <img
                src={activeSrc}
                alt={alt}
                className="server-plot-img"
                style={{ opacity: isLoading ? 0.35 : 1 }}
                onLoad={() => {
                  if (!interactive) {
                    setIsLoading(false);
                    setHasError(false);
                  }
                }}
                onError={() => {
                  if (!interactive) {
                    setIsLoading(false);
                    setHasError(true);
                  }
                }}
              />

              {interactive && !isLoading && hotspots.length > 0 && (
                <div className="plot-hotspot-layer" aria-label="Interactive chart points">
                  {hotspots.map((spot) => {
                    const hitSize = Math.max(18, spot.radiusPx * 2 + 4);
                    const isHovered = hoveredSpot?.eventId === spot.eventId;
                    return (
                      <button
                        key={spot.eventId}
                        type="button"
                        className={`plot-hotspot ${isHovered ? 'hovered' : ''}`}
                        style={{
                          left: `${spot.xPct}%`,
                          top: `${spot.yPct}%`,
                          width: hitSize,
                          height: hitSize,
                          borderColor: spot.color,
                        }}
                        aria-label={`${spot.name} (${spot.yearLabel}): ${formatCompactNumber(spot.deathsMid)} fatalities`}
                        onMouseEnter={() => setHoveredSpot(spot)}
                        onMouseLeave={() =>
                          setHoveredSpot((prev) =>
                            prev?.eventId === spot.eventId ? null : prev,
                          )
                        }
                        onFocus={() => setHoveredSpot(spot)}
                        onBlur={() =>
                          setHoveredSpot((prev) =>
                            prev?.eventId === spot.eventId ? null : prev,
                          )
                        }
                        onClick={() => onSelectEventId?.(spot.eventId)}
                      />
                    );
                  })}
                </div>
              )}

              {hoveredSpot && (
                <div
                  className="plot-tooltip"
                  style={{
                    left: `${Math.min(Math.max(hoveredSpot.xPct, 16), 84)}%`,
                    top: `${hoveredSpot.yPct < 28 ? hoveredSpot.yPct + 5 : hoveredSpot.yPct - 4}%`,
                    transform:
                      hoveredSpot.yPct < 28
                        ? 'translate(-50%, 0)'
                        : 'translate(-50%, -100%)',
                  }}
                >
                  <div className="plot-tooltip-title">{hoveredSpot.name}</div>
                  <div className="plot-tooltip-meta">
                    {hoveredSpot.yearLabel} • {hoveredSpot.region}
                  </div>
                  <div className="plot-tooltip-row">
                    <span style={{ color: hoveredSpot.color }}>
                      {CATEGORY_META[hoveredSpot.category].shortLabel}
                    </span>
                    <strong className="tabular-nums">
                      {formatCompactNumber(hoveredSpot.deathsMid)}
                    </strong>
                  </div>
                  <div className="plot-tooltip-hint">
                    {hoveredSpot.worldPopPercent.toFixed(2)}% world pop. • Click to inspect
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
