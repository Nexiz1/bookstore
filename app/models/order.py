from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, Enum, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Order(Base):
    __tablename__ = "order"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        "userId",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    order_date: Mapped[datetime] = mapped_column(
        "orderDate", DateTime, server_default=func.now()
    )
    total_amount: Mapped[Decimal] = mapped_column("totalAmount", DECIMAL(19, 2))
    status: Mapped[str] = mapped_column(
        Enum("CREATED", "SHIPPED", "ARRIVED", "REFUND", name="order_status"),
        default="CREATED",
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
