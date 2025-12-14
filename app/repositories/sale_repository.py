"""Sale repository module for database operations.

This module handles all database CRUD operations for sales.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.sale import SaleInform
from app.models.sale_book_list import SaleBookList


class SaleRepository:
    """Repository for sale-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int) -> Optional[SaleInform]:
        return (
            self.db.query(SaleInform)
            .options(joinedload(SaleInform.sale_books).joinedload(SaleBookList.book))
            .filter(SaleInform.id == sale_id)
            .first()
        )

    def get_by_seller_id(self, seller_id: int) -> List[SaleInform]:
        return self.db.query(SaleInform).filter(SaleInform.seller_id == seller_id).all()

    def create(self, sale_data: dict, *, commit: bool = True) -> SaleInform:
        """Create a new sale.

        Args:
            sale_data: Dictionary containing sale fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            SaleInform: Created sale instance.
        """
        db_sale = SaleInform(**sale_data)
        self.db.add(db_sale)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_sale)
        return db_sale

    def add_book(self, sale_id: int, book_id: int, *, commit: bool = True) -> SaleBookList:
        """Add a book to a sale.

        Args:
            sale_id: ID of the sale.
            book_id: ID of the book to add.
            commit: If True, commit the transaction. Default True.

        Returns:
            SaleBookList: Created sale book list instance.
        """
        db_sale_book = SaleBookList(sale_id=sale_id, book_id=book_id)
        self.db.add(db_sale_book)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_sale_book)
        return db_sale_book

    def get_sale_book(self, sale_id: int, book_id: int) -> Optional[SaleBookList]:
        return (
            self.db.query(SaleBookList)
            .filter(SaleBookList.sale_id == sale_id, SaleBookList.book_id == book_id)
            .first()
        )

    def update_status(self, sale: SaleInform, status: str, *, commit: bool = True) -> SaleInform:
        """Update sale status.

        Args:
            sale: SaleInform instance to update.
            status: New status value.
            commit: If True, commit the transaction. Default True.

        Returns:
            SaleInform: Updated sale instance.
        """
        sale.status = status
        if commit:
            self.db.commit()
            self.db.refresh(sale)
        return sale
