"""Pytest suite verifying FastAPI endpoints, Aiven PostgreSQL queries, and Matplotlib plots."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402

client = TestClient(app)

ALL_PLOT_TYPES = [
    "timeline",
    "category_donut",
    "era_stacked",
    "log_timeline",
    "category_boxplot",
    "world_pop_scatter",
    "era_heatmap",
]


def test_health_endpoint_postgresql():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "postgresql"
    assert body["dbConnected"] is True
    assert body["eventCount"] == 34


def test_events_filtering_and_sorting():
    all_res = client.get("/api/v1/events")
    assert all_res.status_code == 200
    assert len(all_res.json()) == 34

    pandemic_res = client.get("/api/v1/events", params={"categories": "pandemic", "era": "medieval"})
    assert pandemic_res.status_code == 200
    events = pandemic_res.json()
    assert len(events) == 2
    assert events[0]["id"] == "black-death"


def test_stats_summary_endpoint():
    res = client.get("/api/v1/stats/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["kpi"]["filteredCount"] == 34
    assert data["kpi"]["deadliestEvent"]["id"] == "black-death"
    assert len(data["categoryBreakdown"]) == 6
    assert len(data["eraBreakdown"]) == 7


def test_matplotlib_png_rendering_all_plot_types():
    png_magic = b"\x89PNG\r\n\x1a\n"
    for plot_type in ALL_PLOT_TYPES:
        res = client.get(
            "/api/v1/charts/matplotlib",
            params={
                "plot_type": plot_type,
                "dpi": 150,
                "theme": "obsidian_dark",
                "format": "png",
                "scale": "log" if plot_type == "timeline" else "linear",
            },
        )
        assert res.status_code == 200, f"Failed on {plot_type}"
        assert res.headers["content-type"] == "image/png"
        assert res.headers.get("x-render-engine") == "Matplotlib"
        assert res.headers.get("x-data-source") == "PostgreSQL"
        assert res.content.startswith(png_magic), f"Invalid PNG output for {plot_type}"


def test_matplotlib_svg_and_light_theme_and_empty_filter():
    svg_res = client.get(
        "/api/v1/charts/matplotlib",
        params={
            "plot_type": "world_pop_scatter",
            "theme": "publication_light",
            "format": "svg",
            "dpi": 300,
        },
    )
    assert svg_res.status_code == 200
    assert svg_res.headers["content-type"] == "image/svg+xml"
    assert b"<svg" in svg_res.content

    empty_res = client.get(
        "/api/v1/charts/matplotlib",
        params={"plot_type": "era_stacked", "search": "nonexistent-xyz-query"},
    )
    assert empty_res.status_code == 200
    assert empty_res.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_matplotlib_interactive_hotspots():
    for plot_type in ("timeline", "world_pop_scatter", "log_timeline", "category_boxplot"):
        res = client.get(
            "/api/v1/charts/matplotlib/interactive",
            params={
                "plot_type": plot_type,
                "dpi": 150,
                "theme": "obsidian_dark",
                "format": "png",
                "scale": "linear",
            },
        )
        assert res.status_code == 200, f"Interactive failed for {plot_type}"
        payload = res.json()
        assert payload["imageDataUrl"].startswith("data:image/png;base64,")
        hotspots = payload["hotspots"]
        assert len(hotspots) == 34
        ids = {h["eventId"] for h in hotspots}
        assert "black-death" in ids
        for h in hotspots:
            assert 0.0 <= h["xPct"] <= 100.0
            assert 0.0 <= h["yPct"] <= 100.0
