"""Statistical filtering, sorting, KPI aggregation, and formatting helpers."""

from app.models.historical_data import (
    ALL_CATEGORIES,
    CATEGORY_META,
    ERA_BY_ID,
    ERA_META,
    HISTORICAL_EVENTS,
)
from app.schemas.mortality import (
    CategoryBreakdownItem,
    EraSummaryItem,
    HighestImpactEra,
    HistoricalEra,
    KpiSummaryResponse,
    MortalityCategory,
    MortalityEvent,
    SortDirection,
    SortField,
    StatsSummaryResponse,
)


def format_compact_number(value: float) -> str:
    """Format large fatality counts concisely (e.g., 75.0M, 450K)."""
    abs_val = abs(value)
    if abs_val >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_val >= 1_000_000:
        decimals = 1 if abs_val >= 10_000_000 else 2
        return f"{value / 1_000_000:.{decimals}f}M"
    if abs_val >= 1_000:
        decimals = 0 if abs_val >= 100_000 else 1
        return f"{value / 1_000:.{decimals}f}K"
    return f"{int(round(value)):,}"


def format_year(year: int) -> str:
    """Format integer year with BCE/CE suffix."""
    if year < 0:
        return f"{abs(year)} BCE"
    return f"{year} CE"


def parse_categories(raw: str | None) -> tuple[MortalityCategory, ...]:
    """Parse comma-separated category filter string, preserving canonical order."""
    if not raw or not raw.strip():
        return ALL_CATEGORIES
    requested = {part.strip().lower() for part in raw.split(",") if part.strip()}
    valid = tuple(cat for cat in ALL_CATEGORIES if cat in requested)
    return valid


def filter_and_sort_events(
    events: list[MortalityEvent] | None = None,
    search: str | None = None,
    era: str | None = None,
    categories: tuple[MortalityCategory, ...] | None = None,
    sort_by: SortField = "deathsMid",
    order: SortDirection = "desc",
) -> list[MortalityEvent]:
    """Filter and sort historical mortality events."""
    source = events if events is not None else HISTORICAL_EVENTS
    active_cats = set(categories) if categories is not None else set(ALL_CATEGORIES)
    era_filter = None if (not era or era == "all") else era
    query = (search or "").strip().lower()

    filtered: list[MortalityEvent] = []
    for ev in source:
        if ev.category not in active_cats:
            continue
        if era_filter and ev.era != era_filter:
            continue
        if query:
            haystack = (
                f"{ev.name} {ev.region} {ev.summary} {' '.join(ev.primaryCauses)}"
            ).lower()
            if query not in haystack:
                continue
        filtered.append(ev)

    reverse = order == "desc"
    if sort_by == "name":
        filtered.sort(key=lambda e: e.name.lower(), reverse=reverse)
    elif sort_by == "startYear":
        filtered.sort(key=lambda e: e.startYear, reverse=reverse)
    elif sort_by == "worldPopPercent":
        filtered.sort(key=lambda e: e.worldPopPercent, reverse=reverse)
    else:
        filtered.sort(key=lambda e: e.deathsMid, reverse=reverse)

    return filtered


def compute_stats_summary(
    filtered_events: list[MortalityEvent],
    total_catalog_count: int | None = None,
) -> StatsSummaryResponse:
    """Compute KPI summary, category shares, and era stacked totals."""
    catalog_total = (
        total_catalog_count
        if total_catalog_count is not None
        else len(HISTORICAL_EVENTS)
    )

    if not filtered_events:
        return StatsSummaryResponse(
            kpi=KpiSummaryResponse(
                totalDeathsMid=0,
                totalDeathsLow=0,
                totalDeathsHigh=0,
                deadliestEvent=None,
                highestImpactEra=None,
                filteredCount=0,
                totalCatalogCount=catalog_total,
                avgWorldPopPercent=0.0,
            ),
            categoryBreakdown=[],
            eraBreakdown=[],
        )

    total_mid = sum(ev.deathsMid for ev in filtered_events)
    total_low = sum(ev.deathsLow for ev in filtered_events)
    total_high = sum(ev.deathsHigh for ev in filtered_events)
    avg_pop = sum(ev.worldPopPercent for ev in filtered_events) / len(filtered_events)
    deadliest = max(filtered_events, key=lambda ev: ev.deathsMid)

    cat_totals: dict[MortalityCategory, dict[str, int]] = {
        cat: {"deaths": 0, "count": 0} for cat in ALL_CATEGORIES
    }
    era_totals: dict[HistoricalEra, dict[str, int]] = {
        item["id"]: {  # type: ignore[misc]
            "total": 0,
            "pandemic": 0,
            "war": 0,
            "famine": 0,
            "disaster": 0,
            "atrocity": 0,
            "industrial": 0,
        }
        for item in ERA_META
    }

    for ev in filtered_events:
        cat_totals[ev.category]["deaths"] += ev.deathsMid
        cat_totals[ev.category]["count"] += 1
        era_totals[ev.era]["total"] += ev.deathsMid
        era_totals[ev.era][ev.category] += ev.deathsMid

    top_era_id = max(era_totals.keys(), key=lambda eid: era_totals[eid]["total"])
    top_era_deaths = era_totals[top_era_id]["total"]
    top_era_meta = ERA_BY_ID[top_era_id]

    category_breakdown = [
        CategoryBreakdownItem(
            category=cat,
            label=CATEGORY_META[cat]["label"],
            shortLabel=CATEGORY_META[cat]["shortLabel"],
            color=CATEGORY_META[cat]["color"],
            deathsMid=cat_totals[cat]["deaths"],
            count=cat_totals[cat]["count"],
            sharePercent=(
                (cat_totals[cat]["deaths"] / total_mid) * 100.0 if total_mid > 0 else 0.0
            ),
        )
        for cat in ALL_CATEGORIES
        if cat_totals[cat]["count"] > 0
    ]
    category_breakdown.sort(key=lambda item: item.deathsMid, reverse=True)

    era_breakdown = [
        EraSummaryItem(
            era=item["id"],  # type: ignore[arg-type]
            label=str(item["label"]),
            span=str(item["span"]),
            **era_totals[item["id"]],  # type: ignore[index]
        )
        for item in ERA_META
        if era_totals[item["id"]]["total"] > 0  # type: ignore[index]
    ]

    return StatsSummaryResponse(
        kpi=KpiSummaryResponse(
            totalDeathsMid=total_mid,
            totalDeathsLow=total_low,
            totalDeathsHigh=total_high,
            deadliestEvent=deadliest,
            highestImpactEra=HighestImpactEra(
                era=top_era_id,
                label=str(top_era_meta["label"]),
                totalDeaths=top_era_deaths,
                sharePercent=(top_era_deaths / total_mid) * 100.0 if total_mid > 0 else 0.0,
            ),
            filteredCount=len(filtered_events),
            totalCatalogCount=catalog_total,
            avgWorldPopPercent=round(avg_pop, 4),
        ),
        categoryBreakdown=category_breakdown,
        eraBreakdown=era_breakdown,
    )
