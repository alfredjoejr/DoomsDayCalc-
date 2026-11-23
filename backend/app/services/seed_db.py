"""Create PostgreSQL tables and idempotently seed historical mortality data."""

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import Base, SessionLocal, engine
from app.models.db_models import (
    HistoricalEraORM,
    MortalityCategoryORM,
    MortalityEventORM,
)
from app.models.historical_data import CATEGORY_META, ERA_META, HISTORICAL_EVENTS


def init_and_seed_db(force_upsert: bool = True) -> dict[str, int]:
    """Create tables if absent and upsert eras, categories, and events into PostgreSQL."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        existing_count = session.scalar(select(func.count(MortalityEventORM.id))) or 0

        if force_upsert or existing_count == 0:
            era_rows = [
                {
                    "id": str(item["id"]),
                    "label": str(item["label"]),
                    "short_label": str(item["short"]),
                    "span": str(item["span"]),
                    "sort_order": int(item["order"]),
                }
                for item in ERA_META
            ]
            era_stmt = pg_insert(HistoricalEraORM).values(era_rows)
            era_stmt = era_stmt.on_conflict_do_update(
                index_elements=[HistoricalEraORM.id],
                set_={
                    "label": era_stmt.excluded.label,
                    "short_label": era_stmt.excluded.short_label,
                    "span": era_stmt.excluded.span,
                    "sort_order": era_stmt.excluded.sort_order,
                },
            )
            session.execute(era_stmt)

            cat_rows = [
                {
                    "id": cat_id,
                    "label": meta["label"],
                    "short_label": meta["shortLabel"],
                    "color": meta["color"],
                }
                for cat_id, meta in CATEGORY_META.items()
            ]
            cat_stmt = pg_insert(MortalityCategoryORM).values(cat_rows)
            cat_stmt = cat_stmt.on_conflict_do_update(
                index_elements=[MortalityCategoryORM.id],
                set_={
                    "label": cat_stmt.excluded.label,
                    "short_label": cat_stmt.excluded.short_label,
                    "color": cat_stmt.excluded.color,
                },
            )
            session.execute(cat_stmt)

            event_rows = [
                {
                    "id": ev.id,
                    "name": ev.name,
                    "start_year": ev.startYear,
                    "end_year": ev.endYear,
                    "era_id": ev.era,
                    "category_id": ev.category,
                    "region": ev.region,
                    "deaths_low": ev.deathsLow,
                    "deaths_mid": ev.deathsMid,
                    "deaths_high": ev.deathsHigh,
                    "world_pop_percent": ev.worldPopPercent,
                    "summary": ev.summary,
                    "historical_context": ev.historicalContext,
                    "primary_causes": ev.primaryCauses,
                    "source_note": ev.sourceNote,
                }
                for ev in HISTORICAL_EVENTS
            ]
            ev_stmt = pg_insert(MortalityEventORM).values(event_rows)
            ev_stmt = ev_stmt.on_conflict_do_update(
                index_elements=[MortalityEventORM.id],
                set_={
                    "name": ev_stmt.excluded.name,
                    "start_year": ev_stmt.excluded.start_year,
                    "end_year": ev_stmt.excluded.end_year,
                    "era_id": ev_stmt.excluded.era_id,
                    "category_id": ev_stmt.excluded.category_id,
                    "region": ev_stmt.excluded.region,
                    "deaths_low": ev_stmt.excluded.deaths_low,
                    "deaths_mid": ev_stmt.excluded.deaths_mid,
                    "deaths_high": ev_stmt.excluded.deaths_high,
                    "world_pop_percent": ev_stmt.excluded.world_pop_percent,
                    "summary": ev_stmt.excluded.summary,
                    "historical_context": ev_stmt.excluded.historical_context,
                    "primary_causes": ev_stmt.excluded.primary_causes,
                    "source_note": ev_stmt.excluded.source_note,
                },
            )
            session.execute(ev_stmt)
            session.commit()

        era_count = session.scalar(select(func.count(HistoricalEraORM.id))) or 0
        category_count = session.scalar(select(func.count(MortalityCategoryORM.id))) or 0
        event_count = session.scalar(select(func.count(MortalityEventORM.id))) or 0

    return {
        "eras": int(era_count),
        "categories": int(category_count),
        "events": int(event_count),
    }


if __name__ == "__main__":
    counts = init_and_seed_db(force_upsert=True)
    print(
        f"PostgreSQL schema initialized and seeded: "
        f"{counts['eras']} eras, {counts['categories']} categories, {counts['events']} events."
    )
