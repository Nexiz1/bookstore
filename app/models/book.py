from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CHAR, DECIMAL, TIMESTAMP, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Book(Base):
    __tablename__ = "book"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        "sellerId",
        Integer,
        ForeignKey("sellerProfiles.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    status: Mapped[str] = mapped_column(
        Enum("SOLDOUT", "ONSALE", "TOBESOLD", name="book_status"),
        nullable=False,
        default="TOBESOLD",
    )
    title: Mapped[str] = mapped_column(String(20))
    author: Mapped[str] = mapped_column(String(20))
    publisher: Mapped[str] = mapped_column(String(20))
    average_rating: Mapped[Decimal] = mapped_column(
        "averageRating", DECIMAL(4, 2), default=0
    )
    review_count: Mapped[int] = mapped_column("reviewCount", Integer, default=0)
    purchase_count: Mapped[int] = mapped_column("purchaseCount", Integer, default=0)
    summary: Mapped[str] = mapped_column(String(100))
    isbn: Mapped[str] = mapped_column(CHAR(15))
    price: Mapped[Decimal] = mapped_column(DECIMAL(19, 2))
    publication_date: Mapped[Optional[date]] = mapped_column("publicationDate", Date)
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    seller: Mapped["SellerProfile"] = relationship(back_populates="books")
    cart_items: Mapped[list["Cart"]] = relationship(back_populates="book")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="book")
    reviews: Mapped[list["Review"]] = relationship(back_populates="book")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="book")
    rankings: Mapped[list["Ranking"]] = relationship(back_populates="book")
    sale_books: Mapped[list["SaleBookList"]] = relationship(back_populates="book")
