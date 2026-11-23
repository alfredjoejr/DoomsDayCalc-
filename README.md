# DoomsDayCalc — Chronicle of Human Mortality

An enterprise statistical intelligence platform for exploring, analyzing, and visualizing major mass-mortality events across recorded human history — from antiquity to the 21st century.

All charts across the platform are **100% server-rendered by Python + Matplotlib** via **FastAPI** and served dynamically as PNG/SVG figures synchronized with the React frontend filters.

---

## Folder Organization

```text
DoomsDayCalc/
├── README.md                     # Project overview & quick start
├── docs/
│   └── architecture.md           # Frontend ↔ FastAPI + Matplotlib architecture blueprint
├── backend/                      # Python FastAPI + Matplotlib statistical service
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py               # FastAPI app, CORS, router mounting
│   │   ├── api/v1/endpoints.py   # /health, /events, /stats/summary, /charts/matplotlib
│   │   ├── core/config.py        # Palette tokens, dark/light themes, CORS settings
│   │   ├── models/historical_data.py
│   │   ├── schemas/mortality.py  # Pydantic v2 contracts
│   │   └── services/
│   │       ├── analytics.py      # Filtering, sorting, KPI aggregation
│   │       └── chart_engine.py   # Thread-safe Matplotlib Figure renderer (7 plot types)
│   └── tests/test_api.py         # Pytest endpoint & PNG/SVG verification suite
└── frontend/                     # React 18 + TypeScript + Vite enterprise web application
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── config/theme.ts       # Semantic color tokens & category/era metadata
        ├── styles/               # CSS custom properties, global reset, component styles
        ├── types/                # TypeScript domain interfaces
        ├── data/                 # Curated 34-event historical mortality fallback dataset
        ├── services/             # Typed FastAPI + Matplotlib URL builder & client
        ├── utils/                # Formatters & CSV export utilities
        ├── hooks/                # Analytics filtering, sorting, and KPI computations
        ├── components/           # Modular UI (ServerPlotFrame, layout, hero, filters, kpi, charts, table)
        └── pages/                # Main dashboard assembly
```

---

## Color System (`Editorial Obsidian & Crimson`)

| Token | Hex | Role |
| :--- | :--- | :--- |
| Deep Obsidian | `#090B10` | Primary application & Matplotlib figure canvas |
| Archival Slate | `#10141D` | Elevated navigation & containers |
| Card Surface | `#151B27` | Analytical cards & Matplotlib axes background |
| Crimson Accent | `#E11D48` | Primary brand accent & focal highlights |
| Pandemic | `#F43F5E` | Crimson Rose |
| Armed Conflict | `#F97316` | Ember Orange |
| Famine | `#EAB308` | Ochre Gold |
| Natural Disaster | `#06B6D4` | Glacial Cyan |
| Mass Atrocity | `#A855F7` | Amethyst Violet |
| Industrial Disaster | `#10B981` | Emerald Mint |

---

## Running the Full Stack

### One-Click Startup (Windows PowerShell)

Run both the FastAPI + Matplotlib backend and Vite frontend together in separate windows and open the dashboard automatically:

```powershell
.\start-dev.ps1
```

If PowerShell blocks local scripts under your execution policy:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

### Manual Startup

#### 1. Start the FastAPI + Matplotlib Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

### 2. Start the React Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — the navbar badge will show `FastAPI + Matplotlib: Live`.
