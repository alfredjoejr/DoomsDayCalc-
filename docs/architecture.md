# System Architecture Blueprint

**DoomsDayCalc** uses a **100% server-side Matplotlib visualization pipeline** orchestrated by **FastAPI** and presented in a responsive **React + TypeScript** enterprise dashboard.

## High-Level Data & Rendering Flow

```text
┌─────────────────────────────┐         REST / JSON & PNG/SVG         ┌──────────────────────────────────┐
│   React + TypeScript UI     │ ────────────────────────────────────▶ │   FastAPI Application (v1)       │
│   (frontend/)               │ ◀──────────────────────────────────── │   (backend/app/)                 │
│                             │                                       │                                  │
│  • Filter & Era Controls    │   GET /api/v1/events                  │  • Pydantic v2 Validation        │
│  • ServerPlotFrame (<img>)  │   GET /api/v1/stats/summary           │  • Statistical Aggregation       │
│  • Matplotlib Studio       │   GET /api/v1/charts/matplotlib       │  • Thread-Safe Matplotlib Figure │
│  • Interactive Ledger/Modal │                                       │  • LRU Plot Byte Cache (128)     │
└─────────────────────────────┘                                       └──────────────────────────────────┘
```

## Server-Side Matplotlib Engine (`backend/app/services/chart_engine.py`)

- Uses `matplotlib.figure.Figure` with the `Agg` backend (never global `pyplot` state) for thread safety under concurrent FastAPI requests.
- Cached via `@lru_cache(maxsize=128)` keyed on `(plot_type, dpi, theme, format, scale, era, categories, search)`.
- Supports **7 distinct plot types**:
  - Overview & Interactive Views: `timeline`, `category_donut`, `era_stacked`
  - Analytics Studio Views: `log_timeline`, `category_boxplot`, `world_pop_scatter`, `era_heatmap`
- Supports both `obsidian_dark` (`#090B10` / `#151B27`) and `publication_light` (`#F8FAFC` / `#FFFFFF`) themes, `100–300` DPI, and raster `PNG` or vector `SVG` export.
