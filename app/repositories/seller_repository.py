"""Seller repository module for database operations.

This module handles all database CRUD operations for seller profiles.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.seller_profile import SellerProfile


class SellerRepository:
    """Repository for seller-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

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

    def create(self, seller_data: dict, *, commit: bool = True) -> SellerProfile:
        """Create a new seller profile.

        Args:
            seller_data: Dictionary containing seller fields.
            commit: If True, commit the transaction. Default True.

        Returns:
            SellerProfile: Created seller profile instance.
        """
        db_seller = SellerProfile(**seller_data)
        self.db.add(db_seller)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_seller)
        return db_seller

    def update(self, seller: SellerProfile, update_data: dict, *, commit: bool = True) -> SellerProfile:
        """Update seller profile information.

        Args:
            seller: SellerProfile instance to update.
            update_data: Dictionary of fields to update.
            commit: If True, commit the transaction. Default True.

        Returns:
            SellerProfile: Updated seller profile instance.
        """
        for key, value in update_data.items():
            if value is not None:
                setattr(seller, key, value)
        if commit:
            self.db.commit()
            self.db.refresh(seller)
        return seller
