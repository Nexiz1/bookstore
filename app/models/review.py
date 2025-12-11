from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Review(Base):
    __tablename__ = "review"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        "userId",
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    order_item_id: Mapped[int] = mapped_column(
        "orderItemsId",
        Integer,
        ForeignKey("orderItem.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
    )
    book_id: Mapped[int] = mapped_column(
        "bookId",
        Integer,
        ForeignKey("book.id", ondelete="RESTRICT", onupdate="CASCADE"),
    )
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="reviews")
    order_item: Mapped["OrderItem"] = relationship(back_populates="review")
    book: Mapped["Book"] = relationship(back_populates="reviews")
