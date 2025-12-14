"""Seller profile model module.

This module defines the SellerProfile SQLAlchemy model.

Note:
    - Table name 'sellerProfiles' is legacy camelCase
    - TODO: Consider migrating to 'seller_profiles' for snake_case consistency
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.sale import SaleInform
    from app.models.settlement import Settlement
    from app.models.user import User


class SellerProfile(Base):
    """Seller profile model for vendor information.

    Attributes:
        id: Primary key.
        user_id: Foreign key to user (unique - one seller profile per user).
        business_name: Registered business name.
        business_number: Business registration number.
        email: Business email address.
        gender: Seller's gender.
        address: Business address.
        phone_number: Business phone number.
        payout_account: Bank account for payouts.
        payout_holder: Bank account holder name.
        created_at: Record creation timestamp.
        updated_at: Last update timestamp.
    """

    # TODO: Consider migrating table name to 'seller_profiles' for consistency
    # Current: 'sellerProfiles' (legacy camelCase)
    __tablename__ = "sellerProfiles"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        "userId",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    business_name: Mapped[str] = mapped_column("businessName", String(32), unique=True)
    business_number: Mapped[str] = mapped_column("businessNumber", String(32))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    gender: Mapped[Optional[str]] = mapped_column(String(8))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column("phoneNumber", String(32))
    payout_account: Mapped[Optional[str]] = mapped_column("payoutAccount", String(32))
    payout_holder: Mapped[Optional[str]] = mapped_column("payoutHolder", String(255))
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships - SQLAlchemy 2.0 style
    user: Mapped["User"] = relationship(back_populates="seller_profile")
    books: Mapped[list["Book"]] = relationship(back_populates="seller")
    sales: Mapped[list["SaleInform"]] = relationship(back_populates="seller")
    settlements: Mapped[list["Settlement"]] = relationship(back_populates="seller")
