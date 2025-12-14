from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DECIMAL,
    ForeignKey,
    Integer,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class OrderItem(Base):
    __tablename__ = "orderItem"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        "orderId",
        Integer,
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    book_id: Mapped[int] = mapped_column(
        "bookId", Integer, ForeignKey("book.id")
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(19, 2))
    total_amount: Mapped[Decimal] = mapped_column("totalAmount", DECIMAL(19, 2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("orderId", "bookId", name="uqOrderUserBook"),
        CheckConstraint("quantity >= 1", name="check_order_item_quantity"),
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship(back_populates="order_items")
    review: Mapped[Optional["Review"]] = relationship(
        back_populates="order_item", uselist=False
    )
    settlement_orders: Mapped[list["SettlementOrder"]] = relationship(
        back_populates="order_item"
    )
