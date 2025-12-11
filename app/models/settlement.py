from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DECIMAL, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Settlement(Base):
    __tablename__ = "settlement"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        "sellerId",
        Integer,
        ForeignKey("sellerProfiles.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    total_sales: Mapped[Decimal] = mapped_column("totalSales", DECIMAL(19, 2))
    commission: Mapped[Decimal] = mapped_column(DECIMAL(19, 2))
    final_payout: Mapped[Decimal] = mapped_column("finalPayout", DECIMAL(19, 2))
    period_start: Mapped[date] = mapped_column("periodStart", Date)
    period_end: Mapped[date] = mapped_column("periodEnd", Date)
    settlement_date: Mapped[date] = mapped_column("settlementDate", Date)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    seller: Mapped["SellerProfile"] = relationship(back_populates="settlements")
    settlement_orders: Mapped[list["SettlementOrder"]] = relationship(
        back_populates="settlement", cascade="all, delete-orphan"
    )


class SettlementOrder(Base):
    __tablename__ = "settlementOrder"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    settlement_id: Mapped[int] = mapped_column(
        "settlementId",
        Integer,
        ForeignKey("settlement.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    order_item_id: Mapped[int] = mapped_column(
        "orderItemId", Integer, ForeignKey("orderItem.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    settlement: Mapped["Settlement"] = relationship(back_populates="settlement_orders")
    order_item: Mapped["OrderItem"] = relationship(back_populates="settlement_orders")
