"""Thread-safe Matplotlib statistical plot rendering engine.

Uses matplotlib.figure.Figure directly (never global pyplot state) so concurrent
FastAPI requests remain isolated and deterministic.
"""

from collections import OrderedDict
from functools import lru_cache
from io import BytesIO
from threading import Lock
import matplotlib
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")

from app.core.config import CATEGORY_COLORS, THEMES, ThemePalette
from app.models.historical_data import ALL_CATEGORIES, CATEGORY_META, ERA_META
from app.schemas.mortality import (
    ChartFormat,
    ChartTheme,
    MortalityCategory,
    MortalityEvent,
    PlotType,
    ScaleMode,
)
from app.services.analytics import (
    compute_stats_summary,
    filter_and_sort_events,
    format_compact_number,
    format_year,
)

PlottedPoint = tuple[MortalityEvent, float, float, int]


def _format_year_range(start_year: int, end_year: int) -> str:
    if start_year == end_year:
        return format_year(start_year)
    if start_year < 0 and end_year < 0:
        return f"{abs(start_year)}–{abs(end_year)} BCE"
    if start_year >= 0 and end_year >= 0:
        return f"{start_year}–{end_year} CE"
    return f"{format_year(start_year)} – {format_year(end_year)}"


def _style_axes(ax, palette: ThemePalette, grid_axis: str = "y") -> None:
    """Apply cohesive Obsidian Dark or Publication Light styling to an Axes."""
    ax.set_facecolor(palette.axes_bg)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(palette.spine_color)
    ax.spines["bottom"].set_color(palette.spine_color)
    ax.tick_params(colors=palette.text_secondary, labelsize=9)
    ax.xaxis.label.set_color(palette.text_secondary)
    ax.yaxis.label.set_color(palette.text_secondary)
    ax.title.set_color(palette.text_primary)
    if grid_axis in ("x", "y", "both"):
        ax.grid(
            axis=grid_axis,
            color=palette.grid_color,
            linestyle="--",
            linewidth=0.7,
            alpha=0.65,
        )
    ax.set_axisbelow(True)


def _render_empty(fig: Figure, palette: ThemePalette, message: str) -> None:
    ax = fig.add_subplot(111)
    ax.set_facecolor(palette.axes_bg)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        fontsize=11,
        color=palette.text_secondary,
        transform=ax.transAxes,
    )


def _plot_timeline(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
    scale: ScaleMode,
) -> tuple[object, list[PlottedPoint]]:
    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="both")

    ordered = sorted(events, key=lambda e: e.startYear)
    years = [e.startYear for e in ordered]
    deaths = [max(e.deathsMid, 1) for e in ordered]
    colors = [CATEGORY_COLORS[e.category] for e in ordered]

    if scale == "log":
        ax.set_yscale("log")
        ymin = max(1e3, min(deaths) * 0.5)
        ymax = max(deaths) * 2.2
        ax.set_ylim(ymin, ymax)
    else:
        ax.set_ylim(0, max(deaths) * 1.15)

    ax.plot(years, deaths, color=palette.accent_crimson, linewidth=1.6, alpha=0.72, zorder=2)
    baseline = ax.get_ylim()[0] if scale == "log" else 0
    ax.fill_between(years, deaths, baseline, color=palette.accent_crimson, alpha=0.14, zorder=1)

    ax.scatter(
        years,
        deaths,
        c=colors,
        s=85,
        edgecolors=palette.figure_bg,
        linewidths=1.2,
        zorder=4,
    )

    top_events = sorted(ordered, key=lambda e: e.deathsMid, reverse=True)[:4]
    for idx, ev in enumerate(top_events):
        offset_y = 11 if idx % 2 == 0 else -15
        short_name = ev.name if len(ev.name) <= 22 else f"{ev.name[:20]}…"
        ax.annotate(
            f"{short_name} ({format_compact_number(ev.deathsMid)})",
            xy=(ev.startYear, max(ev.deathsMid, 1)),
            xytext=(0, offset_y),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            fontweight="bold",
            color=palette.text_primary,
            bbox={
                "boxstyle": "round,pad=0.22",
                "facecolor": palette.figure_bg,
                "edgecolor": CATEGORY_COLORS[ev.category],
                "alpha": 0.88,
                "linewidth": 0.8,
            },
            zorder=5,
        )

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_year(int(x))))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: format_compact_number(y)))
    ax.set_title(
        f"Chronological Mortality Magnitude ({'Log₁₀' if scale == 'log' else 'Linear'} Scale)",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )
    ax.set_ylabel("Estimated Fatalities (Midpoint)", fontsize=9.5)

    points: list[PlottedPoint] = [
        (ev, float(ev.startYear), float(max(ev.deathsMid, 1)), 9)
        for ev in ordered
    ]
    return ax, points


def _plot_category_donut(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
) -> None:
    stats = compute_stats_summary(events)
    breakdown = stats.categoryBreakdown
    if not breakdown:
        _render_empty(fig, palette, "No category records match active filters.")
        return

    ax = fig.add_subplot(111)
    ax.set_facecolor(palette.figure_bg)

    values = [item.deathsMid for item in breakdown]
    colors = [item.color for item in breakdown]
    labels = [
        f"{item.shortLabel} ({item.sharePercent:.1f}%)" for item in breakdown
    ]

    wedges, _ = ax.pie(
        values,
        colors=colors,
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.36, "edgecolor": palette.figure_bg, "linewidth": 2.2},
        radius=0.92,
    )

    ax.text(
        0,
        0.07,
        format_compact_number(stats.kpi.totalDeathsMid),
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color=palette.text_primary,
    )
    ax.text(
        0,
        -0.14,
        "TOTAL TOLL",
        ha="center",
        va="center",
        fontsize=8.5,
        color=palette.text_secondary,
    )

    legend = ax.legend(
        wedges,
        labels,
        title="Mortality Cause",
        loc="center left",
        bbox_to_anchor=(0.95, 0.5),
        frameon=False,
        fontsize=8.8,
        labelcolor=palette.text_primary,
    )
    legend.get_title().set_color(palette.text_secondary)
    legend.get_title().set_fontsize(9)

    ax.set_title(
        "Mortality Share by Primary Cause",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=8,
    )


def _plot_era_stacked(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
    scale: ScaleMode,
) -> None:
    stats = compute_stats_summary(events)
    eras = stats.eraBreakdown
    if not eras:
        _render_empty(fig, palette, "No era data matches active filters.")
        return

    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="y")

    short_map = {item["id"]: str(item["short"]) for item in ERA_META}
    x = np.arange(len(eras))
    labels = [short_map.get(row.era, row.label) for row in eras]
    bottoms = np.zeros(len(eras), dtype=float)

    for cat in ALL_CATEGORIES:
        vals = np.array([getattr(row, cat) for row in eras], dtype=float)
        if vals.sum() <= 0:
            continue
        ax.bar(
            x,
            vals,
            bottom=bottoms,
            width=0.58,
            color=CATEGORY_COLORS[cat],
            edgecolor=palette.figure_bg,
            linewidth=0.7,
            label=CATEGORY_META[cat]["shortLabel"],
            zorder=3,
        )
        bottoms += vals

    if scale == "log":
        ax.set_yscale("log")
        ax.set_ylim(max(1e4, np.min(bottoms[bottoms > 0]) * 0.5), np.max(bottoms) * 2.2)
    else:
        ax.set_ylim(0, np.max(bottoms) * 1.16)
        for idx, total in enumerate(bottoms):
            ax.text(
                idx,
                total + np.max(bottoms) * 0.02,
                format_compact_number(total),
                ha="center",
                va="bottom",
                fontsize=8,
                color=palette.text_secondary,
                fontweight="bold",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: format_compact_number(y)))
    ax.legend(
        loc="upper left",
        ncol=3,
        frameon=False,
        fontsize=8.2,
        labelcolor=palette.text_primary,
    )
    ax.set_title(
        "Mortality Distribution Across Historical Eras",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )
    ax.set_ylabel("Cumulative Fatalities", fontsize=9.5)


def _plot_log_timeline_uncertainty(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
) -> tuple[object, list[PlottedPoint]]:
    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="both")

    ordered = sorted(events, key=lambda e: e.startYear)
    points: list[PlottedPoint] = []
    for ev in ordered:
        mid = max(ev.deathsMid, 1)
        low = max(ev.deathsLow, 1)
        high = max(ev.deathsHigh, mid)
        yerr = [[max(mid - low, 0)], [max(high - mid, 0)]]
        ax.errorbar(
            ev.startYear,
            mid,
            yerr=yerr,
            fmt="o",
            color=CATEGORY_COLORS[ev.category],
            ecolor=CATEGORY_COLORS[ev.category],
            elinewidth=1.6,
            capsize=3.5,
            markersize=7,
            markeredgecolor=palette.figure_bg,
            markeredgewidth=1.0,
            alpha=0.92,
            zorder=4,
        )
        points.append((ev, float(ev.startYear), float(mid), 9))

    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_year(int(x))))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: format_compact_number(y)))
    ax.set_title(
        "Logarithmic Mortality Timeline with Scholarly Uncertainty Bounds",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )
    ax.set_ylabel("Fatalities (Low – Mid – High, Log Scale)", fontsize=9.5)
    return ax, points


def _plot_category_boxplot(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
) -> tuple[object | None, list[PlottedPoint]]:
    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="x")

    groups: list[list[MortalityEvent]] = []
    labels: list[str] = []
    colors: list[str] = []

    for cat in reversed(ALL_CATEGORIES):
        cat_events = [ev for ev in events if ev.category == cat]
        if cat_events:
            groups.append(cat_events)
            labels.append(CATEGORY_META[cat]["shortLabel"])
            colors.append(CATEGORY_COLORS[cat])

    if not groups:
        _render_empty(fig, palette, "No data available for category spread.")
        return None, []

    numeric_groups = [[max(ev.deathsMid, 1) for ev in g] for g in groups]
    bp = ax.boxplot(
        numeric_groups,
        orientation="horizontal",
        patch_artist=True,
        widths=0.52,
        showfliers=False,
        medianprops={"color": palette.text_primary, "linewidth": 1.8},
        whiskerprops={"color": palette.text_secondary, "linewidth": 1.1},
        capprops={"color": palette.text_secondary, "linewidth": 1.1},
    )

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.35)
        patch.set_edgecolor(color)
        patch.set_linewidth(1.5)

    points: list[PlottedPoint] = []
    for idx, (cat_events, color) in enumerate(zip(groups, colors), start=1):
        jitter = np.linspace(-0.14, 0.14, len(cat_events)) if len(cat_events) > 1 else [0.0]
        vals = [max(ev.deathsMid, 1) for ev in cat_events]
        ys = [idx + float(j) for j in jitter]
        ax.scatter(
            vals,
            ys,
            color=color,
            s=42,
            edgecolors=palette.figure_bg,
            linewidths=0.9,
            zorder=5,
        )
        for ev, x_val, y_val in zip(cat_events, vals, ys):
            points.append((ev, float(x_val), float(y_val), 8))

    ax.set_xscale("log")
    ax.set_yticks(range(1, len(labels) + 1))
    ax.set_yticklabels(labels, fontsize=9.5, color=palette.text_primary)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_compact_number(x)))
    ax.set_title(
        "Fatality Distribution & Spread by Cause Category (Log Scale)",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )
    ax.set_xlabel("Estimated Fatalities (Midpoint)", fontsize=9.5)
    return ax, points


def _plot_world_pop_scatter(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
) -> tuple[object, list[PlottedPoint]]:
    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="both")

    years = [e.startYear for e in events]
    pops = [e.worldPopPercent for e in events]
    max_d = max((e.deathsMid for e in events), default=1)
    sizes = [max(45.0, (e.deathsMid / max_d) * 520.0) for e in events]
    colors = [CATEGORY_COLORS[e.category] for e in events]

    ax.scatter(
        years,
        pops,
        s=sizes,
        c=colors,
        alpha=0.82,
        edgecolors=palette.figure_bg,
        linewidths=1.2,
        zorder=4,
    )

    top_pop = sorted(events, key=lambda e: e.worldPopPercent, reverse=True)[:4]
    for ev in top_pop:
        ax.annotate(
            f"{ev.name} ({ev.worldPopPercent:.1f}%)",
            xy=(ev.startYear, ev.worldPopPercent),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color=palette.text_primary,
            fontweight="bold",
        )

    ax.set_ylim(0, max(pops, default=1) * 1.18)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_year(int(x))))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1f}%"))
    ax.set_title(
        "Demographic Shock: Share of Global Population Lost",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )
    ax.set_ylabel("% of Contemporary World Population", fontsize=9.5)

    points: list[PlottedPoint] = [
        (ev, float(ev.startYear), float(ev.worldPopPercent), max(8, int(np.sqrt(sz / np.pi))))
        for ev, sz in zip(events, sizes)
    ]
    return ax, points


def _plot_era_heatmap(
    fig: Figure,
    events: list[MortalityEvent],
    palette: ThemePalette,
) -> None:
    ax = fig.add_subplot(111)
    _style_axes(ax, palette, grid_axis="none")

    era_ids = [item["id"] for item in ERA_META]
    era_labels = [str(item["short"]) for item in ERA_META]
    cat_labels = [CATEGORY_META[c]["shortLabel"] for c in ALL_CATEGORIES]

    matrix = np.zeros((len(ALL_CATEGORIES), len(era_ids)), dtype=float)
    for ev in events:
        r = ALL_CATEGORIES.index(ev.category)
        c = era_ids.index(ev.era)
        matrix[r, c] += ev.deathsMid

    positive = matrix[matrix > 0]
    if len(positive) == 0:
        _render_empty(fig, palette, "No intensity matrix values match active filters.")
        return

    cmap = LinearSegmentedColormap.from_list(
        "obsidian_crimson",
        [palette.axes_bg, "#4C0519", "#9F1239", "#E11D48", "#F97316", "#FACC15"],
    )
    masked = np.ma.masked_where(matrix <= 0, matrix)
    norm = LogNorm(vmin=max(1e3, float(positive.min())), vmax=float(positive.max()))

    im = ax.imshow(masked, cmap=cmap, norm=norm, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.04)
    cbar.ax.tick_params(colors=palette.text_secondary, labelsize=8)
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: format_compact_number(y)))

    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            val = matrix[r, c]
            if val > 0:
                ax.text(
                    c,
                    r,
                    format_compact_number(val),
                    ha="center",
                    va="center",
                    fontsize=7.8,
                    fontweight="bold",
                    color="#FFFFFF",
                )
            else:
                ax.text(
                    c,
                    r,
                    "·",
                    ha="center",
                    va="center",
                    fontsize=10,
                    color=palette.text_secondary,
                    alpha=0.45,
                )

    ax.set_xticks(range(len(era_labels)))
    ax.set_xticklabels(era_labels, fontsize=8.8)
    ax.set_yticks(range(len(cat_labels)))
    ax.set_yticklabels(cat_labels, fontsize=9)
    ax.set_title(
        "Era × Cause Mortality Intensity Matrix (Log Color Scale)",
        fontsize=12,
        fontweight="bold",
        color=palette.text_primary,
        loc="left",
        pad=12,
    )


_PLOT_CACHE_MAX = 128
_PLOT_CACHE: OrderedDict[tuple, bytes] = OrderedDict()
_INTERACTIVE_CACHE: OrderedDict[tuple, tuple[bytes, list[dict]]] = OrderedDict()
_PLOT_CACHE_LOCK = Lock()


def _render_figure_with_hotspots(
    plot_type: PlotType,
    dpi: int,
    theme: ChartTheme,
    fmt: ChartFormat,
    scale: ScaleMode,
    events: list[MortalityEvent],
) -> tuple[bytes, list[dict]]:
    """Render a Matplotlib figure and compute normalized percentage hotspot coordinates."""
    palette = THEMES[theme]
    figsize = (7.2, 4.6) if plot_type == "category_donut" else (9.6, 4.5)
    fig = Figure(figsize=figsize, dpi=dpi, facecolor=palette.figure_bg)
    FigureCanvasAgg(fig)

    target_ax = None
    plotted_points: list[PlottedPoint] = []

    if not events:
        _render_empty(fig, palette, "No historical events match your active filters.")
    elif plot_type == "timeline":
        target_ax, plotted_points = _plot_timeline(fig, events, palette, scale)
    elif plot_type == "category_donut":
        _plot_category_donut(fig, events, palette)
    elif plot_type == "era_stacked":
        _plot_era_stacked(fig, events, palette, scale)
    elif plot_type == "log_timeline":
        target_ax, plotted_points = _plot_log_timeline_uncertainty(fig, events, palette)
    elif plot_type == "category_boxplot":
        target_ax, plotted_points = _plot_category_boxplot(fig, events, palette)
    elif plot_type == "world_pop_scatter":
        target_ax, plotted_points = _plot_world_pop_scatter(fig, events, palette)
    elif plot_type == "era_heatmap":
        _plot_era_heatmap(fig, events, palette)

    fig.tight_layout(pad=1.4)
    fig.canvas.draw()

    hotspots: list[dict] = []
    if target_ax is not None and plotted_points:
        data_to_disp = target_ax.transData
        disp_to_fig = fig.transFigure.inverted()
        for ev, x_val, y_val, radius_px in plotted_points:
            disp_pt = data_to_disp.transform((x_val, y_val))
            fig_pt = disp_to_fig.transform(disp_pt)
            x_pct = round(max(0.0, min(100.0, float(fig_pt[0]) * 100.0)), 3)
            y_pct = round(max(0.0, min(100.0, (1.0 - float(fig_pt[1])) * 100.0)), 3)
            hotspots.append(
                {
                    "eventId": ev.id,
                    "name": ev.name,
                    "yearLabel": _format_year_range(ev.startYear, ev.endYear),
                    "category": ev.category,
                    "color": CATEGORY_COLORS[ev.category],
                    "deathsMid": ev.deathsMid,
                    "worldPopPercent": ev.worldPopPercent,
                    "region": ev.region,
                    "xPct": x_pct,
                    "yPct": y_pct,
                    "radiusPx": radius_px,
                }
            )

    buf = BytesIO()
    fig.savefig(
        buf,
        format=fmt,
        dpi=dpi,
        facecolor=palette.figure_bg,
        edgecolor="none",
    )
    buf.seek(0)
    return buf.getvalue(), hotspots


def render_matplotlib_chart_from_events(
    plot_type: PlotType,
    dpi: int,
    theme: ChartTheme,
    fmt: ChartFormat,
    scale: ScaleMode,
    era: str,
    categories_tuple: tuple[MortalityCategory, ...],
    search: str,
    events: tuple[MortalityEvent, ...],
) -> bytes:
    """Render and cache a publication-grade Matplotlib chart from PostgreSQL events."""
    fingerprint = tuple((ev.id, ev.deathsMid, ev.worldPopPercent) for ev in events)
    cache_key = (
        plot_type,
        dpi,
        theme,
        fmt,
        scale,
        era,
        categories_tuple,
        search,
        fingerprint,
    )

    with _PLOT_CACHE_LOCK:
        cached = _PLOT_CACHE.get(cache_key)
        if cached is not None:
            _PLOT_CACHE.move_to_end(cache_key)
            return cached

    rendered, _ = _render_figure_with_hotspots(
        plot_type=plot_type,
        dpi=dpi,
        theme=theme,
        fmt=fmt,
        scale=scale,
        events=list(events),
    )

    with _PLOT_CACHE_LOCK:
        _PLOT_CACHE[cache_key] = rendered
        if len(_PLOT_CACHE) > _PLOT_CACHE_MAX:
            _PLOT_CACHE.popitem(last=False)

    return rendered


def render_interactive_matplotlib_chart(
    plot_type: PlotType,
    dpi: int,
    theme: ChartTheme,
    fmt: ChartFormat,
    scale: ScaleMode,
    era: str,
    categories_tuple: tuple[MortalityCategory, ...],
    search: str,
    events: tuple[MortalityEvent, ...],
) -> tuple[bytes, list[dict]]:
    """Render and cache a Matplotlib chart alongside clickable circle hotspots."""
    fingerprint = tuple((ev.id, ev.deathsMid, ev.worldPopPercent) for ev in events)
    cache_key = (
        plot_type,
        dpi,
        theme,
        fmt,
        scale,
        era,
        categories_tuple,
        search,
        fingerprint,
    )

    with _PLOT_CACHE_LOCK:
        cached = _INTERACTIVE_CACHE.get(cache_key)
        if cached is not None:
            _INTERACTIVE_CACHE.move_to_end(cache_key)
            return cached

    rendered, hotspots = _render_figure_with_hotspots(
        plot_type=plot_type,
        dpi=dpi,
        theme=theme,
        fmt=fmt,
        scale=scale,
        events=list(events),
    )

    with _PLOT_CACHE_LOCK:
        _INTERACTIVE_CACHE[cache_key] = (rendered, hotspots)
        if len(_INTERACTIVE_CACHE) > _PLOT_CACHE_MAX:
            _INTERACTIVE_CACHE.popitem(last=False)

    return rendered, hotspots


@lru_cache(maxsize=128)
def render_matplotlib_chart(
    plot_type: PlotType,
    dpi: int,
    theme: ChartTheme,
    fmt: ChartFormat,
    scale: ScaleMode,
    era: str,
    categories_tuple: tuple[MortalityCategory, ...],
    search: str,
) -> bytes:
    """Render and cache a Matplotlib chart using in-memory fallback data."""
    events = filter_and_sort_events(
        search=search or None,
        era=era,
        categories=categories_tuple,
        sort_by="startYear",
        order="asc",
    )
    rendered, _ = _render_figure_with_hotspots(
        plot_type=plot_type,
        dpi=dpi,
        theme=theme,
        fmt=fmt,
        scale=scale,
        events=events,
    )
    return rendered
