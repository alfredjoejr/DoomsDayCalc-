"""Pydantic v2 request and response contracts matching the frontend schema."""

from typing import Literal
from pydantic import BaseModel, Field

MortalityCategory = Literal[
    "pandemic",
    "war",
    "famine",
    "disaster",
    "atrocity",
    "industrial",
]

HistoricalEra = Literal[
    "ancient",
    "classical",
    "medieval",
    "early_modern",
    "industrial_age",
    "modern_20c",
    "contemporary_21c",
]

PlotType = Literal[
    "timeline",
    "category_donut",
    "era_stacked",
    "log_timeline",
    "category_boxplot",
    "world_pop_scatter",
    "era_heatmap",
]

ScaleMode = Literal["linear", "log"]
ChartTheme = Literal["obsidian_dark", "publication_light"]
ChartFormat = Literal["png", "svg"]
SortField = Literal["deathsMid", "startYear", "worldPopPercent", "name"]
SortDirection = Literal["asc", "desc"]


class MortalityEvent(BaseModel):
    id: str
    name: str
    startYear: int
    endYear: int
    era: HistoricalEra
    category: MortalityCategory
    region: str
    deathsLow: int = Field(..., ge=0)
    deathsMid: int = Field(..., ge=0)
    deathsHigh: int = Field(..., ge=0)
    worldPopPercent: float = Field(..., ge=0)
    summary: str
    historicalContext: str
    primaryCauses: list[str]
    sourceNote: str


class CategoryBreakdownItem(BaseModel):
    category: MortalityCategory
    label: str
    shortLabel: str
    color: str
    deathsMid: int
    count: int
    sharePercent: float


class EraSummaryItem(BaseModel):
    era: HistoricalEra
    label: str
    span: str
    total: int
    pandemic: int = 0
    war: int = 0
    famine: int = 0
    disaster: int = 0
    atrocity: int = 0
    industrial: int = 0


class HighestImpactEra(BaseModel):
    era: HistoricalEra
    label: str
    totalDeaths: int
    sharePercent: float


class KpiSummaryResponse(BaseModel):
    totalDeathsMid: int
    totalDeathsLow: int
    totalDeathsHigh: int
    deadliestEvent: MortalityEvent | None = None
    highestImpactEra: HighestImpactEra | None = None
    filteredCount: int
    totalCatalogCount: int
    avgWorldPopPercent: float


class StatsSummaryResponse(BaseModel):
    kpi: KpiSummaryResponse
    categoryBreakdown: list[CategoryBreakdownItem]
    eraBreakdown: list[EraSummaryItem]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    engine: str
    matplotlibVersion: str
    database: str
    dbConnected: bool
    eventCount: int


class ChartHotspot(BaseModel):
    eventId: str
    name: str
    yearLabel: str
    category: MortalityCategory
    color: str
    deathsMid: int
    worldPopPercent: float
    region: str
    xPct: float
    yPct: float
    radiusPx: int


class InteractiveChartResponse(BaseModel):
    imageDataUrl: str
    plotType: PlotType
    hotspots: list[ChartHotspot]
