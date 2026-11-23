import type { HistoricalEra, MortalityCategory } from '../types/mortality';

export interface CategoryMeta {
  id: MortalityCategory;
  label: string;
  shortLabel: string;
  color: string;
  softBg: string;
  description: string;
}

export const CATEGORY_META: Record<MortalityCategory, CategoryMeta> = {
  pandemic: {
    id: 'pandemic',
    label: 'Pandemic & Plague',
    shortLabel: 'Pandemic',
    color: '#F43F5E',
    softBg: 'rgba(244, 63, 94, 0.14)',
    description: 'Infectious disease outbreaks across continents',
  },
  war: {
    id: 'war',
    label: 'Armed Conflict',
    shortLabel: 'War & Conquest',
    color: '#F97316',
    softBg: 'rgba(249, 115, 22, 0.14)',
    description: 'Interstate wars, civil conflicts, and conquests',
  },
  famine: {
    id: 'famine',
    label: 'Famine & Starvation',
    shortLabel: 'Famine',
    color: '#EAB308',
    softBg: 'rgba(234, 179, 8, 0.14)',
    description: 'Crop failures, sieges, and systemic food crises',
  },
  disaster: {
    id: 'disaster',
    label: 'Natural Disaster',
    shortLabel: 'Disaster',
    color: '#06B6D4',
    softBg: 'rgba(6, 182, 212, 0.14)',
    description: 'Earthquakes, floods, tsunamis, and volcanic events',
  },
  atrocity: {
    id: 'atrocity',
    label: 'Mass Atrocity',
    shortLabel: 'Atrocity',
    color: '#A855F7',
    softBg: 'rgba(168, 85, 247, 0.14)',
    description: 'Genocides, state purges, and forced displacements',
  },
  industrial: {
    id: 'industrial',
    label: 'Industrial & Tech',
    shortLabel: 'Industrial',
    color: '#10B981',
    softBg: 'rgba(16, 185, 129, 0.14)',
    description: 'Chemical, nuclear, and infrastructural catastrophes',
  },
};

export const ALL_CATEGORIES: MortalityCategory[] = [
  'pandemic',
  'war',
  'famine',
  'disaster',
  'atrocity',
  'industrial',
];

export interface EraMeta {
  id: HistoricalEra;
  label: string;
  span: string;
  order: number;
}

export const ERA_META: Record<HistoricalEra, EraMeta> = {
  ancient: { id: 'ancient', label: 'Ancient Antiquity', span: 'Pre-1 CE', order: 1 },
  classical: { id: 'classical', label: 'Classical Era', span: '1 – 500 CE', order: 2 },
  medieval: { id: 'medieval', label: 'Medieval Era', span: '501 – 1500 CE', order: 3 },
  early_modern: { id: 'early_modern', label: 'Early Modern', span: '1501 – 1800', order: 4 },
  industrial_age: { id: 'industrial_age', label: 'Industrial Age', span: '1801 – 1900', order: 5 },
  modern_20c: { id: 'modern_20c', label: '20th Century', span: '1901 – 1999', order: 6 },
  contemporary_21c: { id: 'contemporary_21c', label: '21st Century', span: '2000 – Present', order: 7 },
};

export const ORDERED_ERAS: EraMeta[] = Object.values(ERA_META).sort((a, b) => a.order - b.order);
