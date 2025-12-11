from typing import Optional

from sqlalchemy.orm import Session

from app.models.seller_profile import SellerProfile


class SellerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, seller_id: int) -> Optional[SellerProfile]:
        return (
            self.db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[SellerProfile]:
        return (
            self.db.query(SellerProfile)
            .filter(SellerProfile.user_id == user_id)
            .first()
        )

    def get_by_business_name(self, business_name: str) -> Optional[SellerProfile]:
        return (
            self.db.query(SellerProfile)
            .filter(SellerProfile.business_name == business_name)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[SellerProfile]:
        return self.db.query(SellerProfile).filter(SellerProfile.email == email).first()

    def create(self, seller_data: dict) -> SellerProfile:
        db_seller = SellerProfile(**seller_data)
        self.db.add(db_seller)
        self.db.commit()
        self.db.refresh(db_seller)
        return db_seller

    def update(self, seller: SellerProfile, update_data: dict) -> SellerProfile:
        for key, value in update_data.items():
            if value is not None:
                setattr(seller, key, value)
        self.db.commit()
        self.db.refresh(seller)
        return seller
