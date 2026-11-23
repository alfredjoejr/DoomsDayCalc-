import type { MortalityEvent } from '../types/mortality';

export function formatCompactNumber(value: number): string {
  if (!Number.isFinite(value)) return '0';
  const abs = Math.abs(value);
  if (abs >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `${(value / 1_000_000).toFixed(abs >= 10_000_000 ? 1 : 2)}M`;
  if (abs >= 1_000) return `${(value / 1_000).toFixed(abs >= 100_000 ? 0 : 1)}K`;
  return value.toLocaleString('en-US');
}

export function formatFullNumber(value: number): string {
  return Math.round(value).toLocaleString('en-US');
}

export function formatYear(year: number): string {
  if (year < 0) return `${Math.abs(year)} BCE`;
  return `${year} CE`;
}

export function formatYearRange(startYear: number, endYear: number): string {
  if (startYear === endYear) return formatYear(startYear);
  if (startYear < 0 && endYear < 0) {
    return `${Math.abs(startYear)}–${Math.abs(endYear)} BCE`;
  }
  if (startYear >= 0 && endYear >= 0) {
    return `${startYear}–${endYear} CE`;
  }
  return `${formatYear(startYear)} – ${formatYear(endYear)}`;
}

export function exportEventsToCsv(events: MortalityEvent[]): void {
  const headers = [
    'ID',
    'Name',
    'StartYear',
    'EndYear',
    'Era',
    'Category',
    'Region',
    'DeathsLow',
    'DeathsMid',
    'DeathsHigh',
    'WorldPopPercent',
    'Summary',
  ];

  const escapeCell = (raw: string | number): string => {
    const str = String(raw);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const rows = events.map((ev) =>
    [
      ev.id,
      ev.name,
      ev.startYear,
      ev.endYear,
      ev.era,
      ev.category,
      ev.region,
      ev.deathsLow,
      ev.deathsMid,
      ev.deathsHigh,
      ev.worldPopPercent,
      ev.summary,
    ]
      .map(escapeCell)
      .join(','),
  );

  const csvContent = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `doomsdaycalc-mortality-events-${events.length}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
