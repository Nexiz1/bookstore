from datetime import datetime

from sqlalchemy import ForeignKey, Integer, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorite"

    # SQLAlchemy 2.0 style with Mapped
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        "userId",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    book_id: Mapped[int] = mapped_column(
        "bookId",
        Integer,
        ForeignKey("book.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt", TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("userId", "bookId", name="uqWishUserBook"),)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="favorites")
    book: Mapped["Book"] = relationship(back_populates="favorites")
