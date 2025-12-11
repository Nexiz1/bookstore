from sqlalchemy.orm import Session

from app.exceptions.book_exceptions import BookNotFoundException, BookNotOwnedException
from app.exceptions.sale_exceptions import (
    SaleBookAlreadyExistsException,
    SaleNotFoundException,
    SaleNotOwnedException,
)
from app.exceptions.seller_exceptions import SellerNotFoundException
from app.repositories.book_repository import BookRepository
from app.repositories.sale_repository import SaleRepository
from app.repositories.seller_repository import SellerRepository
from app.schemas.sale import SaleBookAdd, SaleCreate, SaleResponse


class SaleService:
    def __init__(self, db: Session):
        self.db = db
        self.sale_repo = SaleRepository(db)
        self.seller_repo = SellerRepository(db)
        self.book_repo = BookRepository(db)

    def create_sale(self, user_id: int, sale_data: SaleCreate) -> SaleResponse:
        # 판매자 프로필 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()

        sale = self.sale_repo.create(
            {
                "sale_name": sale_data.sale_name,
                "seller_id": seller.id,
                "discount_rate": sale_data.discount_rate,
                "started_at": sale_data.started_at,
                "ended_at": sale_data.ended_at,
                "status": "INACTIVE",
            }
        )

        return SaleResponse.model_validate(sale)

    def add_book_to_sale(
        self, user_id: int, sale_id: int, book_data: SaleBookAdd
    ) -> SaleResponse:
        # 판매자 프로필 확인
        seller = self.seller_repo.get_by_user_id(user_id)
        if not seller:
            raise SellerNotFoundException()

        # 세일 확인
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            raise SaleNotFoundException()

        # 본인 세일인지 확인
        if sale.seller_id != seller.id:
            raise SaleNotOwnedException()

        # 책 확인
        book = self.book_repo.get_by_id(book_data.book_id)
        if not book:
            raise BookNotFoundException()

        # 본인 책인지 확인
        if book.seller_id != seller.id:
            raise BookNotOwnedException()

        # 이미 세일에 추가되어 있는지 확인
        existing = self.sale_repo.get_sale_book(sale_id, book_data.book_id)
        if existing:
            raise SaleBookAlreadyExistsException()

        self.sale_repo.add_book(sale_id, book_data.book_id)

        # 세일 다시 조회
        sale = self.sale_repo.get_by_id(sale_id)
        return SaleResponse.model_validate(sale)
