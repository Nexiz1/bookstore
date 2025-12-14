"""User model module.

This module defines the User SQLAlchemy model with SQLAlchemy 2.0 style.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import TIMESTAMP, Date, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.favorite import Favorite
    from app.models.order import Order
    from app.models.review import Review
    from app.models.seller_profile import SellerProfile


class User(Base):
    """User model representing application users.

    Attributes:
        id: Primary key.
        role: User role (user, admin, seller).
        email: Unique email address.
        password: Hashed password (Argon2id).
        name: User's name.
        birth_date: Date of birth.
        gender: User's gender.
        address: User's address.
        phone_number: Contact phone number.
        created_at: Record creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "user"

    # SQLAlchemy 2.0 스타일 - Pylance 타입 체크 개선
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", "seller", name="user_role"),
        nullable=False,
        default="user",
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(
        "birthDate", Date, default=func.current_date()
    )
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column("phoneNumber", String(20))
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships - SQLAlchemy 2.0 style with Mapped type hints
    seller_profile: Mapped[Optional["SellerProfile"]] = relationship(
        back_populates="user", uselist=False
    )
    carts: Mapped[list["Cart"]] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
