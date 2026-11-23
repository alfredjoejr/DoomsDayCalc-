"""FastAPI v1 REST endpoints backed by Aiven PostgreSQL and Matplotlib."""

import base64
import matplotlib
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.mortality import (
    ChartFormat,
    ChartHotspot,
    ChartTheme,
    HealthResponse,
    InteractiveChartResponse,
    MortalityEvent,
    PlotType,
    ScaleMode,
    SortDirection,
    SortField,
    StatsSummaryResponse,
)
from app.services.analytics import compute_stats_summary, parse_categories
from app.services.chart_engine import (
    render_interactive_matplotlib_chart,
    render_matplotlib_chart_from_events,
)
from app.services.repository import count_events_in_db, fetch_events_from_db

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Confirm FastAPI, PostgreSQL connection, and Matplotlib engine availability."""
    try:
        total_events = count_events_in_db(db)
        db_connected = True
    except Exception:
        total_events = 0
        db_connected = False

    return HealthResponse(
        status="ok",
        engine="FastAPI + Matplotlib + PostgreSQL",
        matplotlibVersion=matplotlib.__version__,
        database="postgresql",
        dbConnected=db_connected,
        eventCount=total_events,
    )


@router.get("/events", response_model=list[MortalityEvent], tags=["Mortality Data"])
def list_events(
    search: str | None = Query(default=None, description="Search event name, region, or summary"),
    era: str | None = Query(default=None, description="Historical era ID or 'all'"),
    categories: str | None = Query(
        default=None, description="Comma-separated mortality categories"
    ),
    sort_by: SortField = Query(default="deathsMid"),
    order: SortDirection = Query(default="desc"),
    db: Session = Depends(get_db),
) -> list[MortalityEvent]:
    """Return filtered and sorted historical mortality records from PostgreSQL."""
    parsed_cats = parse_categories(categories)
    return fetch_events_from_db(
        db=db,
        search=search,
        era=era,
        categories=parsed_cats,
        sort_by=sort_by,
        order=order,
    )


@router.get("/stats/summary", response_model=StatsSummaryResponse, tags=["Analytics"])
def get_stats_summary(
    search: str | None = Query(default=None),
    era: str | None = Query(default=None),
    categories: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> StatsSummaryResponse:
    """Compute KPI totals, category shares, and era totals from PostgreSQL records."""
    parsed_cats = parse_categories(categories)
    filtered = fetch_events_from_db(
        db=db,
        search=search,
        era=era,
        categories=parsed_cats,
    )
    total_catalog = count_events_in_db(db)
    return compute_stats_summary(filtered, total_catalog_count=total_catalog)


@router.get("/charts/matplotlib", tags=["Matplotlib Engine"])
def get_matplotlib_chart(
    plot_type: PlotType = Query(default="timeline"),
    dpi: int = Query(default=150, ge=100, le=300),
    theme: ChartTheme = Query(default="obsidian_dark"),
    format: ChartFormat = Query(default="png"),
    scale: ScaleMode = Query(default="linear"),
    era: str = Query(default="all"),
    categories: str | None = Query(default=None),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
) -> Response:
    """Render a server-side Matplotlib statistical plot from PostgreSQL records."""
    parsed_cats = parse_categories(categories)
    db_events = fetch_events_from_db(
        db=db,
        search=search.strip() or None,
        era=era or "all",
        categories=parsed_cats,
        sort_by="startYear",
        order="asc",
    )
    image_bytes = render_matplotlib_chart_from_events(
        plot_type=plot_type,
        dpi=dpi,
        theme=theme,
        fmt=format,
        scale=scale,
        era=era or "all",
        categories_tuple=parsed_cats,
        search=search.strip(),
        events=tuple(db_events),
    )
    media_type = "image/svg+xml" if format == "svg" else "image/png"
    return Response(
        content=image_bytes,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=300",
            "X-Render-Engine": "Matplotlib",
            "X-Data-Source": "PostgreSQL",
        },
    )


@router.get(
    "/charts/matplotlib/interactive",
    response_model=InteractiveChartResponse,
    tags=["Matplotlib Engine"],
)
def get_interactive_matplotlib_chart(
    plot_type: PlotType = Query(default="timeline"),
    dpi: int = Query(default=150, ge=100, le=300),
    theme: ChartTheme = Query(default="obsidian_dark"),
    format: ChartFormat = Query(default="png"),
    scale: ScaleMode = Query(default="linear"),
    era: str = Query(default="all"),
    categories: str | None = Query(default=None),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
) -> InteractiveChartResponse:
    """Render a Matplotlib chart alongside normalized circle hotspot coordinates."""
    parsed_cats = parse_categories(categories)
    db_events = fetch_events_from_db(
        db=db,
        search=search.strip() or None,
        era=era or "all",
        categories=parsed_cats,
        sort_by="startYear",
        order="asc",
    )
    image_bytes, hotspots = render_interactive_matplotlib_chart(
        plot_type=plot_type,
        dpi=dpi,
        theme=theme,
        fmt=format,
        scale=scale,
        era=era or "all",
        categories_tuple=parsed_cats,
        search=search.strip(),
        events=tuple(db_events),
    )
    mime = "image/svg+xml" if format == "svg" else "image/png"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return InteractiveChartResponse(
        imageDataUrl=f"data:{mime};base64,{encoded}",
        plotType=plot_type,
        hotspots=[ChartHotspot(**h) for h in hotspots],
    )
