"""Sale model module.

This module defines the SaleInform SQLAlchemy model for time-limited sales.

Note:
    - Table name 'sale_informs' follows snake_case convention
    - Column 'discountRate' fixed from typo 'discoutRate'
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, DateTime, Enum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.sale_book_list import SaleBookList
    from app.models.seller_profile import SellerProfile


class SaleInform(Base):
    """Sale information model for time-limited discount events.

    Attributes:
        id: Primary key.
        sale_name: Name of the sale event.
        seller_id: Foreign key to seller profile.
        discount_rate: Discount percentage (e.g., 10.00 = 10%).
        started_at: Sale start datetime.
        ended_at: Sale end datetime.
        status: Sale status (ACTIVE/INACTIVE).
        created_at: Record creation timestamp.
        updated_at: Last update timestamp.
    """

    # TODO: Consider migrating table name to 'sale_informs' for consistency
    # Current: 'saleInform' (legacy camelCase)
    __tablename__ = "saleInform"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    sale_name: Mapped[str] = mapped_column("saleName", String(20))
    seller_id: Mapped[int] = mapped_column(
        "sellerId",
        Integer,
        ForeignKey("sellerProfiles.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    # Fixed typo: 'discoutRate' -> 'discountRate'
    discount_rate: Mapped[Decimal] = mapped_column("discountRate", DECIMAL(5, 2))
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
