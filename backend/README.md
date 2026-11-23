# DoomsDayCalc Backend (FastAPI + Matplotlib Service)

Python statistical aggregation and server-side Matplotlib plot rendering service.

## Directory Layout

```text
backend/
├── requirements.txt
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── api/v1/endpoints.py       # Versioned REST endpoints
│   ├── core/config.py            # Theme palettes, semantic colors, CORS
│   ├── models/historical_data.py # 34-event curated dataset & era/category metadata
│   ├── schemas/mortality.py      # Pydantic v2 schemas
│   └── services/
│       ├── analytics.py          # Filtering, sorting, KPI aggregation
│       └── chart_engine.py       # Thread-safe Matplotlib Figure renderer (LRU cached)
└── tests/
    └── test_api.py               # Pytest verification suite
```

## REST Endpoints

- `GET /api/v1/health` — Engine status & Matplotlib version
- `GET /api/v1/events` — Filterable & sortable historical mortality events (`category`, `era`, `search`, `sort_by`, `order`)
- `GET /api/v1/stats/summary` — Aggregated KPI metrics, category breakdown, and era totals
- `GET /api/v1/charts/matplotlib` — Renders PNG or SVG figures using Matplotlib (`plot_type`, `dpi`, `theme`, `format`, `scale`, `categories`, `era`, `search`)

Supported `plot_type` values:
`timeline`, `category_donut`, `era_stacked`, `log_timeline`, `category_boxplot`, `world_pop_scatter`, `era_heatmap`.

## Running & Testing

```bash
cd backend
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Run tests:

```bash
.\.venv\Scripts\pytest tests -v
```
