from datetime import date, datetime
from typing import Optional

from sqlalchemy import TIMESTAMP, Column, Date, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
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

    # Relationships
    seller_profile = relationship("SellerProfile", back_populates="user", uselist=False)
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
