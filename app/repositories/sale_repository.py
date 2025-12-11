from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.sale import SaleInform
from app.models.sale_book_list import SaleBookList


class SaleRepository:
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

    def create(self, sale_data: dict) -> SaleInform:
        db_sale = SaleInform(**sale_data)
        self.db.add(db_sale)
        self.db.commit()
        self.db.refresh(db_sale)
        return db_sale

    def add_book(self, sale_id: int, book_id: int) -> SaleBookList:
        db_sale_book = SaleBookList(sale_id=sale_id, book_id=book_id)
        self.db.add(db_sale_book)
        self.db.commit()
        self.db.refresh(db_sale_book)
        return db_sale_book

    def get_sale_book(self, sale_id: int, book_id: int) -> Optional[SaleBookList]:
        return (
            self.db.query(SaleBookList)
            .filter(SaleBookList.sale_id == sale_id, SaleBookList.book_id == book_id)
            .first()
        )

    def update_status(self, sale: SaleInform, status: str) -> SaleInform:
        sale.status = status
        self.db.commit()
        self.db.refresh(sale)
        return sale
