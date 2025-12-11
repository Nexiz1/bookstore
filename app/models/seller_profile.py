from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SellerProfile(Base):
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
    business_name: Mapped[str] = mapped_column(
        "businessName", String(32), unique=True
    )
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

    # Relationships
    user: Mapped["User"] = relationship(back_populates="seller_profile")
    books: Mapped[list["Book"]] = relationship(back_populates="seller")
    sales: Mapped[list["SaleInform"]] = relationship(back_populates="seller")
    settlements: Mapped[list["Settlement"]] = relationship(back_populates="seller")
