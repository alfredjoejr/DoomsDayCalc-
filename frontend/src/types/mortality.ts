export type MortalityCategory =
  | 'pandemic'
  | 'war'
  | 'famine'
  | 'disaster'
  | 'atrocity'
  | 'industrial';

export type HistoricalEra =
  | 'ancient'
  | 'classical'
  | 'medieval'
  | 'early_modern'
  | 'industrial_age'
  | 'modern_20c'
  | 'contemporary_21c';

export interface MortalityEvent {
  id: string;
  name: string;
  startYear: number; // Negative values denote BCE
  endYear: number;
  era: HistoricalEra;
  category: MortalityCategory;
  region: string;
  deathsLow: number;
  deathsMid: number;
  deathsHigh: number;
  worldPopPercent: number;
  summary: string;
  historicalContext: string;
  primaryCauses: string[];
  sourceNote: string;
}

export type ScaleMode = 'linear' | 'log';

export type SortField = 'deathsMid' | 'startYear' | 'worldPopPercent' | 'name';

export type SortDirection = 'asc' | 'desc';

export interface FilterState {
  searchQuery: string;
  selectedCategories: MortalityCategory[];
  selectedEra: HistoricalEra | 'all';
  scaleMode: ScaleMode;
  sortField: SortField;
  sortDirection: SortDirection;
}

export interface KpiSummary {
  totalDeathsMid: number;
  totalDeathsLow: number;
  totalDeathsHigh: number;
  deadliestEvent: MortalityEvent | null;
  highestImpactEra: {
    era: HistoricalEra;
    label: string;
    totalDeaths: number;
    sharePercent: number;
  } | null;
  filteredCount: number;
  totalCatalogCount: number;
  avgWorldPopPercent: number;
}

export type MatplotlibPlotType =
  | 'timeline'
  | 'category_donut'
  | 'era_stacked'
  | 'log_timeline'
  | 'category_boxplot'
  | 'world_pop_scatter'
  | 'era_heatmap';

export type ChartFormat = 'png' | 'svg';

export interface MatplotlibPlotConfig {
  plotType: MatplotlibPlotType;
  dpi: 150 | 300;
  theme: 'obsidian_dark' | 'publication_light';
  format: ChartFormat;
}

export interface ChartHotspot {
  eventId: string;
  name: string;
  yearLabel: string;
  category: MortalityCategory;
  color: string;
  deathsMid: number;
  worldPopPercent: number;
  region: string;
  xPct: number;
  yPct: number;
  radiusPx: number;
}

export interface InteractiveChartPayload {
  imageDataUrl: string;
  plotType: MatplotlibPlotType;
  hotspots: ChartHotspot[];
}

export type DashboardTab = 'overview' | 'analytics' | 'ledger';
