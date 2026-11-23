"""SQLAlchemy ORM tables for historical eras, mortality categories, and events."""

from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HistoricalEraORM(Base):
    __tablename__ = "historical_eras"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    short_label: Mapped[str] = mapped_column(String(32), nullable=False)
    span: Mapped[str] = mapped_column(String(32), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    events: Mapped[list["MortalityEventORM"]] = relationship(back_populates="era_rel")


class MortalityCategoryORM(Base):
    __tablename__ = "mortality_categories"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    short_label: Mapped[str] = mapped_column(String(32), nullable=False)
    color: Mapped[str] = mapped_column(String(16), nullable=False)

    events: Mapped[list["MortalityEventORM"]] = relationship(back_populates="category_rel")


class MortalityEventORM(Base):
    __tablename__ = "mortality_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    end_year: Mapped[int] = mapped_column(Integer, nullable=False)
    era_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("historical_eras.id"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("mortality_categories.id"), nullable=False, index=True
    )
    region: Mapped[str] = mapped_column(String(180), nullable=False)
    deaths_low: Mapped[int] = mapped_column(BigInteger, nullable=False)
    deaths_mid: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    deaths_high: Mapped[int] = mapped_column(BigInteger, nullable=False)
    world_pop_percent: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    historical_context: Mapped[str] = mapped_column(Text, nullable=False)
    primary_causes: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    source_note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    era_rel: Mapped[HistoricalEraORM] = relationship(back_populates="events")
    category_rel: Mapped[MortalityCategoryORM] = relationship(back_populates="events")

    __table_args__ = (
        Index("ix_mortality_events_era_cat", "era_id", "category_id"),
    )
