"""PostgreSQL repository queries for mortality events."""

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.db_models import MortalityEventORM
from app.schemas.mortality import (
    MortalityCategory,
    MortalityEvent,
    SortDirection,
    SortField,
)


def _to_schema(row: MortalityEventORM) -> MortalityEvent:
    return MortalityEvent(
        id=row.id,
        name=row.name,
        startYear=row.start_year,
        endYear=row.end_year,
        era=row.era_id,  # type: ignore[arg-type]
        category=row.category_id,  # type: ignore[arg-type]
        region=row.region,
        deathsLow=row.deaths_low,
        deathsMid=row.deaths_mid,
        deathsHigh=row.deaths_high,
        worldPopPercent=row.world_pop_percent,
        summary=row.summary,
        historicalContext=row.historical_context,
        primaryCauses=list(row.primary_causes),
        sourceNote=row.source_note,
    )


def count_events_in_db(db: Session) -> int:
    """Return total cataloged events stored in PostgreSQL."""
    return int(db.scalar(select(func.count(MortalityEventORM.id))) or 0)


def fetch_events_from_db(
    db: Session,
    search: str | None = None,
    era: str | None = None,
    categories: tuple[MortalityCategory, ...] | None = None,
    sort_by: SortField = "deathsMid",
    order: SortDirection = "desc",
) -> list[MortalityEvent]:
    """Query, filter, and sort mortality events directly from PostgreSQL."""
    if categories is not None and len(categories) == 0:
        return []

    stmt = select(MortalityEventORM)

    if categories is not None:
        stmt = stmt.where(MortalityEventORM.category_id.in_(categories))

    if era and era != "all":
        stmt = stmt.where(MortalityEventORM.era_id == era)

    if search and search.strip():
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                MortalityEventORM.name.ilike(pattern),
                MortalityEventORM.region.ilike(pattern),
                MortalityEventORM.summary.ilike(pattern),
            )
        )

    sort_column_map = {
        "name": MortalityEventORM.name,
        "startYear": MortalityEventORM.start_year,
        "worldPopPercent": MortalityEventORM.world_pop_percent,
        "deathsMid": MortalityEventORM.deaths_mid,
    }
    sort_col = sort_column_map.get(sort_by, MortalityEventORM.deaths_mid)
    stmt = stmt.order_by(asc(sort_col) if order == "asc" else desc(sort_col))

    rows = db.scalars(stmt).all()
    return [_to_schema(row) for row in rows]
