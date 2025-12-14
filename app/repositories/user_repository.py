"""User repository module for database operations.

This module handles all database CRUD operations for users.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """Repository for user-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100, keyword: Optional[str] = None):
        query = self.db.query(User)
        if keyword:
            query = query.filter(
                or_(User.name.ilike(f"%{keyword}%"), User.email.ilike(f"%{keyword}%"))
            )
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def create(self, user_data: dict, *, commit: bool = True) -> User:
        """Create a new user.

        Args:
            user_data: Dictionary containing user fields.
            commit: If True, commit the transaction. Default True for auth operations.

        Returns:
            User: Created user instance.
        """
        db_user = User(**user_data)
        self.db.add(db_user)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def update(self, user: User, update_data: dict, *, commit: bool = True) -> User:
        """Update user information.

        Args:
            user: User instance to update.
            update_data: Dictionary of fields to update.
            commit: If True, commit the transaction. Default True.

        Returns:
            User: Updated user instance.
        """
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        if commit:
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str, *, commit: bool = True) -> User:
        """Update user password.

        Args:
            user: User instance to update.
            hashed_password: New hashed password.
            commit: If True, commit the transaction. Default True.

        Returns:
            User: Updated user instance.
        """
        user.password = hashed_password
        if commit:
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_role(self, user: User, role: str, *, commit: bool = True) -> User:
        """Update user role.

        Args:
            user: User instance to update.
            role: New role value.
            commit: If True, commit the transaction. Default True.

        Returns:
            User: Updated user instance.
        """
        user.role = role
        if commit:
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_status(self, user: User, is_active: bool, *, commit: bool = True) -> User:
        """Update user active status.

        Args:
            user: User instance to update.
            is_active: New active status value.
            commit: If True, commit the transaction. Default True.

        Returns:
            User: Updated user instance.
        """
        user.is_active = is_active
        if commit:
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user: User, *, commit: bool = True) -> None:
        """Delete a user.

        Args:
            user: User instance to delete.
            commit: If True, commit the transaction. Default True.
        """
        self.db.delete(user)
        if commit:
            self.db.commit()
