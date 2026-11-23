import { ALL_CATEGORIES, CATEGORY_META, ORDERED_ERAS } from '../../config/theme';
import type {
  FilterState,
  HistoricalEra,
  MortalityCategory,
  ScaleMode,
} from '../../types/mortality';

interface FilterBarProps {
  filters: FilterState;
  onCategoryChange: (cat: MortalityCategory | 'all') => void;
  onEraChange: (era: HistoricalEra | 'all') => void;
  onScaleChange: (mode: ScaleMode) => void;
}

export function FilterBar({
  filters,
  onCategoryChange,
  onEraChange,
  onScaleChange,
}: FilterBarProps) {
  const selectedCategory: MortalityCategory | 'all' =
    filters.selectedCategories.length === 1 ? filters.selectedCategories[0] : 'all';

  return (
    <section className="minimal-filter-bar" aria-label="Dataset Filters">
      <select
        className="select-control"
        value={selectedCategory}
        onChange={(e) =>
          onCategoryChange(e.target.value as MortalityCategory | 'all')
        }
        aria-label="Filter by cause"
      >
        <option value="all">All Causes</option>
        {ALL_CATEGORIES.map((catId) => (
          <option key={catId} value={catId}>
            {CATEGORY_META[catId].label}
          </option>
        ))}
      </select>

      <select
        className="select-control"
        value={filters.selectedEra}
        onChange={(e) => onEraChange(e.target.value as HistoricalEra | 'all')}
        aria-label="Filter by historical era"
      >
        <option value="all">All Historical Eras</option>
        {ORDERED_ERAS.map((era) => (
          <option key={era.id} value={era.id}>
            {era.label} ({era.span})
          </option>
        ))}
      </select>

      <div className="scale-toggle" role="group" aria-label="Scale mode">
        <button
          type="button"
          className={`scale-btn ${filters.scaleMode === 'linear' ? 'active' : ''}`}
          onClick={() => onScaleChange('linear')}
        >
          Linear
        </button>
        <button
          type="button"
          className={`scale-btn ${filters.scaleMode === 'log' ? 'active' : ''}`}
          onClick={() => onScaleChange('log')}
        >
          Log₁₀
        </button>
      </div>
    </section>
  );
}
