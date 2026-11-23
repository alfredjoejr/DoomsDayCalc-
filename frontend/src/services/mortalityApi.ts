import { HISTORICAL_EVENTS } from '../data/historicalEvents';
import type {
  ChartFormat,
  FilterState,
  InteractiveChartPayload,
  MatplotlibPlotConfig,
  MatplotlibPlotType,
  MortalityEvent,
} from '../types/mortality';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface EventsResponse {
  events: MortalityEvent[];
  source: 'fastapi' | 'mock';
}

export interface BackendHealth {
  online: boolean;
  engine?: string;
  matplotlibVersion?: string;
  database?: string;
  dbConnected?: boolean;
  eventCount?: number;
}

/**
 * Checks FastAPI + PostgreSQL + Matplotlib backend health.
 */
export async function checkBackendHealth(): Promise<BackendHealth> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    if (!res.ok) return { online: false };
    const body = (await res.json()) as {
      status: string;
      engine: string;
      matplotlibVersion: string;
      database: string;
      dbConnected: boolean;
      eventCount: number;
    };
    return {
      online: body.status === 'ok',
      engine: body.engine,
      matplotlibVersion: body.matplotlibVersion,
      database: body.database,
      dbConnected: body.dbConnected,
      eventCount: body.eventCount,
    };
  } catch {
    return { online: false };
  }
}

/**
 * Fetches mortality events from FastAPI + PostgreSQL when available,
 * gracefully falling back to the curated local dataset if offline.
 */
export async function fetchMortalityEvents(): Promise<EventsResponse> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(`${API_BASE_URL}/events`, { signal: controller.signal });
    clearTimeout(timeout);

    if (res.ok) {
      const payload = (await res.json()) as MortalityEvent[];
      if (Array.isArray(payload) && payload.length > 0) {
        return { events: payload, source: 'fastapi' };
      }
    }
  } catch {
    // Fallback when FastAPI server is offline
  }
  return { events: HISTORICAL_EVENTS, source: 'mock' };
}

export interface ChartUrlOptions {
  plotType: MatplotlibPlotType;
  dpi?: 150 | 300;
  theme?: 'obsidian_dark' | 'publication_light';
  format?: ChartFormat;
  filters: FilterState;
}

function buildChartQueryParams({
  plotType,
  dpi = 150,
  theme = 'obsidian_dark',
  format = 'png',
  filters,
}: ChartUrlOptions): URLSearchParams {
  const params = new URLSearchParams();
  params.set('plot_type', plotType);
  params.set('dpi', String(dpi));
  params.set('theme', theme);
  params.set('format', format);
  params.set('scale', filters.scaleMode);

  if (filters.selectedEra !== 'all') {
    params.set('era', filters.selectedEra);
  }
  if (filters.selectedCategories.length === 0) {
    params.set('categories', 'none');
  } else if (filters.selectedCategories.length < 6) {
    params.set('categories', filters.selectedCategories.join(','));
  }
  if (filters.searchQuery.trim()) {
    params.set('search', filters.searchQuery.trim());
  }

  return params;
}

/**
 * Builds the FastAPI Matplotlib chart image URL synced with all active dashboard filters.
 */
export function buildMatplotlibChartUrl(options: ChartUrlOptions): string {
  const params = buildChartQueryParams(options);
  return `${API_BASE_URL}/charts/matplotlib?${params.toString()}`;
}

/**
 * Fetches a Matplotlib chart together with normalized clickable circle hotspots.
 */
export async function fetchInteractiveMatplotlibChart(
  options: ChartUrlOptions,
  signal?: AbortSignal,
): Promise<InteractiveChartPayload> {
  const params = buildChartQueryParams(options);
  const res = await fetch(
    `${API_BASE_URL}/charts/matplotlib/interactive?${params.toString()}`,
    { signal },
  );
  if (!res.ok) {
    throw new Error(`Interactive chart request failed (${res.status})`);
  }
  return (await res.json()) as InteractiveChartPayload;
}

export function buildMatplotlibEndpointUrl(
  config: MatplotlibPlotConfig,
  filters: FilterState,
): string {
  return buildMatplotlibChartUrl({
    plotType: config.plotType,
    dpi: config.dpi,
    theme: config.theme,
    format: config.format,
    filters,
  });
}
