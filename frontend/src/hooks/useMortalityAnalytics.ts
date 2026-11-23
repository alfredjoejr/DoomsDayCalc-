import { useMemo, useState } from 'react';
import { ALL_CATEGORIES, CATEGORY_META, ERA_META, ORDERED_ERAS } from '../config/theme';
import type {
  FilterState,
  HistoricalEra,
  KpiSummary,
  MortalityCategory,
  MortalityEvent,
  ScaleMode,
  SortField,
} from '../types/mortality';
import { formatYearRange } from '../utils/formatters';

const DEFAULT_FILTERS: FilterState = {
  searchQuery: '',
  selectedCategories: [...ALL_CATEGORIES],
  selectedEra: 'all',
  scaleMode: 'linear',
  sortField: 'deathsMid',
  sortDirection: 'desc',
};

export interface TimelinePoint {
  id: string;
  name: string;
  year: number;
  yearLabel: string;
  deathsMid: number;
  deathsPlot: number;
  category: MortalityCategory;
  color: string;
  worldPopPercent: number;
  region: string;
}

export interface CategoryBreakdownItem {
  category: MortalityCategory;
  label: string;
  shortLabel: string;
  color: string;
  deathsMid: number;
  count: number;
  sharePercent: number;
}

export interface EraChartRow {
  era: HistoricalEra;
  label: string;
  span: string;
  total: number;
  pandemic: number;
  war: number;
  famine: number;
  disaster: number;
  atrocity: number;
  industrial: number;
}

export function useMortalityAnalytics(events: MortalityEvent[]) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  const categoryCounts = useMemo(() => {
    const counts: Record<MortalityCategory, number> = {
      pandemic: 0,
      war: 0,
      famine: 0,
      disaster: 0,
      atrocity: 0,
      industrial: 0,
    };
    for (const ev of events) {
      counts[ev.category] += 1;
    }
    return counts;
  }, [events]);

  const filteredEvents = useMemo(() => {
    const query = filters.searchQuery.trim().toLowerCase();
    const activeCats = new Set(filters.selectedCategories);

    const matching = events.filter((ev) => {
      if (!activeCats.has(ev.category)) return false;
      if (filters.selectedEra !== 'all' && ev.era !== filters.selectedEra) return false;
      if (query) {
        const hay = `${ev.name} ${ev.region} ${ev.summary} ${ev.primaryCauses.join(' ')}`.toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });

    const dir = filters.sortDirection === 'asc' ? 1 : -1;
    return [...matching].sort((a, b) => {
      switch (filters.sortField) {
        case 'name':
          return a.name.localeCompare(b.name) * dir;
        case 'startYear':
          return (a.startYear - b.startYear) * dir;
        case 'worldPopPercent':
          return (a.worldPopPercent - b.worldPopPercent) * dir;
        case 'deathsMid':
        default:
          return (a.deathsMid - b.deathsMid) * dir;
      }
    });
  }, [events, filters]);

  const kpiSummary = useMemo<KpiSummary>(() => {
    if (filteredEvents.length === 0) {
      return {
        totalDeathsMid: 0,
        totalDeathsLow: 0,
        totalDeathsHigh: 0,
        deadliestEvent: null,
        highestImpactEra: null,
        filteredCount: 0,
        totalCatalogCount: events.length,
        avgWorldPopPercent: 0,
      };
    }

    let totalDeathsMid = 0;
    let totalDeathsLow = 0;
    let totalDeathsHigh = 0;
    let popSum = 0;
    let deadliestEvent = filteredEvents[0];

    const eraTotals: Partial<Record<HistoricalEra, number>> = {};

    for (const ev of filteredEvents) {
      totalDeathsMid += ev.deathsMid;
      totalDeathsLow += ev.deathsLow;
      totalDeathsHigh += ev.deathsHigh;
      popSum += ev.worldPopPercent;
      if (ev.deathsMid > deadliestEvent.deathsMid) {
        deadliestEvent = ev;
      }
      eraTotals[ev.era] = (eraTotals[ev.era] ?? 0) + ev.deathsMid;
    }

    let topEraId: HistoricalEra = filteredEvents[0].era;
    let topEraDeaths = 0;
    for (const [eraKey, val] of Object.entries(eraTotals) as [HistoricalEra, number][]) {
      if (val > topEraDeaths) {
        topEraDeaths = val;
        topEraId = eraKey;
      }
    }

    return {
      totalDeathsMid,
      totalDeathsLow,
      totalDeathsHigh,
      deadliestEvent,
      highestImpactEra: {
        era: topEraId,
        label: ERA_META[topEraId].label,
        totalDeaths: topEraDeaths,
        sharePercent: totalDeathsMid > 0 ? (topEraDeaths / totalDeathsMid) * 100 : 0,
      },
      filteredCount: filteredEvents.length,
      totalCatalogCount: events.length,
      avgWorldPopPercent: popSum / filteredEvents.length,
    };
  }, [filteredEvents, events.length]);

  const timelineSeries = useMemo<TimelinePoint[]>(() => {
    return [...filteredEvents]
      .sort((a, b) => a.startYear - b.startYear)
      .map((ev) => ({
        id: ev.id,
        name: ev.name,
        year: ev.startYear,
        yearLabel: formatYearRange(ev.startYear, ev.endYear),
        deathsMid: ev.deathsMid,
        deathsPlot:
          filters.scaleMode === 'log'
            ? Number(Math.log10(Math.max(ev.deathsMid, 1)).toFixed(2))
            : ev.deathsMid,
        category: ev.category,
        color: CATEGORY_META[ev.category].color,
        worldPopPercent: ev.worldPopPercent,
        region: ev.region,
      }));
  }, [filteredEvents, filters.scaleMode]);

  const categoryBreakdown = useMemo<CategoryBreakdownItem[]>(() => {
    const totals: Record<MortalityCategory, { deaths: number; count: number }> = {
      pandemic: { deaths: 0, count: 0 },
      war: { deaths: 0, count: 0 },
      famine: { deaths: 0, count: 0 },
      disaster: { deaths: 0, count: 0 },
      atrocity: { deaths: 0, count: 0 },
      industrial: { deaths: 0, count: 0 },
    };

    let grandTotal = 0;
    for (const ev of filteredEvents) {
      totals[ev.category].deaths += ev.deathsMid;
      totals[ev.category].count += 1;
      grandTotal += ev.deathsMid;
    }

    return ALL_CATEGORIES.map((cat) => ({
      category: cat,
      label: CATEGORY_META[cat].label,
      shortLabel: CATEGORY_META[cat].shortLabel,
      color: CATEGORY_META[cat].color,
      deathsMid: totals[cat].deaths,
      count: totals[cat].count,
      sharePercent: grandTotal > 0 ? (totals[cat].deaths / grandTotal) * 100 : 0,
    }))
      .filter((item) => item.count > 0)
      .sort((a, b) => b.deathsMid - a.deathsMid);
  }, [filteredEvents]);

  const eraSeries = useMemo<EraChartRow[]>(() => {
    const map = new Map<HistoricalEra, EraChartRow>();
    for (const eraMeta of ORDERED_ERAS) {
      map.set(eraMeta.id, {
        era: eraMeta.id,
        label: eraMeta.label,
        span: eraMeta.span,
        total: 0,
        pandemic: 0,
        war: 0,
        famine: 0,
        disaster: 0,
        atrocity: 0,
        industrial: 0,
      });
    }

    for (const ev of filteredEvents) {
      const row = map.get(ev.era);
      if (row) {
        row[ev.category] += ev.deathsMid;
        row.total += ev.deathsMid;
      }
    }

    return Array.from(map.values()).filter((row) => row.total > 0);
  }, [filteredEvents]);

  const setSearchQuery = (searchQuery: string) =>
    setFilters((prev) => ({ ...prev, searchQuery }));

  const toggleCategory = (cat: MortalityCategory) =>
    setFilters((prev) => {
      const exists = prev.selectedCategories.includes(cat);
      if (exists && prev.selectedCategories.length === 1) {
        // Clicking the sole active category restores all categories for effortless UX
        return { ...prev, selectedCategories: [...ALL_CATEGORIES] };
      }
      const next = exists
        ? prev.selectedCategories.filter((c) => c !== cat)
        : [...prev.selectedCategories, cat];
      return { ...prev, selectedCategories: next };
    });

  const isolateCategory = (cat: MortalityCategory) =>
    setFilters((prev) => {
      const alreadyIsolated =
        prev.selectedCategories.length === 1 && prev.selectedCategories[0] === cat;
      return {
        ...prev,
        selectedCategories: alreadyIsolated ? [...ALL_CATEGORIES] : [cat],
      };
    });

  const setSelectedEra = (selectedEra: HistoricalEra | 'all') =>
    setFilters((prev) => ({ ...prev, selectedEra }));

  const setScaleMode = (scaleMode: ScaleMode) =>
    setFilters((prev) => ({ ...prev, scaleMode }));

  const toggleSort = (field: SortField) =>
    setFilters((prev) => {
      if (prev.sortField === field) {
        return {
          ...prev,
          sortDirection: prev.sortDirection === 'desc' ? 'asc' : 'desc',
        };
      }
      return {
        ...prev,
        sortField: field,
        sortDirection: field === 'name' ? 'asc' : 'desc',
      };
    });

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  return {
    filters,
    categoryCounts,
    filteredEvents,
    kpiSummary,
    timelineSeries,
    categoryBreakdown,
    eraSeries,
    setSearchQuery,
    toggleCategory,
    isolateCategory,
    setSelectedEra,
    setScaleMode,
    toggleSort,
    resetFilters,
  };
}
