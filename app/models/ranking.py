from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Ranking(Base):
    __tablename__ = "ranking"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(
        "bookId",
        Integer,
        ForeignKey("book.id", ondelete="RESTRICT", onupdate="RESTRICT"),
    )
    ranking_type: Mapped[str] = mapped_column(
        "rankingType",
        Enum("purchaseCount", "averageRating", name="ranking_type"),
    )
    rank: Mapped[int] = mapped_column(Integer)
    purchase_count: Mapped[int] = mapped_column("purchaseCount", Integer, default=0)
    age_group: Mapped[str] = mapped_column("ageGroup", String(10), default="ALL")
    average_rating: Mapped[Decimal] = mapped_column(
        "averageRating", DECIMAL(4, 2), default=0
    )
    gender: Mapped[str] = mapped_column(String(10), default="ALL")
    region: Mapped[str] = mapped_column(String(255), default="ALL")
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "rankingType",
            "gender",
            "region",
            "ageGroup",
            "bookId",
            name="uqRankingBook",
        ),
        UniqueConstraint(
            "rankingType", "gender", "region", "ageGroup", "rank", name="uqRankingRank"
        ),
    )

    # Relationships
    book: Mapped["Book"] = relationship(back_populates="rankings")
