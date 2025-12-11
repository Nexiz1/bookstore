from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, Enum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SaleInform(Base):
    __tablename__ = "saleInform"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    sale_name: Mapped[str] = mapped_column("saleName", String(20))
    seller_id: Mapped[int] = mapped_column(
        "sellerId",
        Integer,
        ForeignKey("sellerProfiles.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    discount_rate: Mapped[Decimal] = mapped_column("discoutRate", DECIMAL(5, 2))
    started_at: Mapped[datetime] = mapped_column("startedAt", DateTime)
    ended_at: Mapped[datetime] = mapped_column("endedAt", DateTime)
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "INACTIVE", name="sale_status"),
        default="INACTIVE",
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    seller: Mapped["SellerProfile"] = relationship(back_populates="sales")
    sale_books: Mapped[list["SaleBookList"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan"
    )
