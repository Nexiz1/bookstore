from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
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

    def create(self, user_data: dict) -> User:
        db_user = User(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        user.password = hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_role(self, user: User, role: str) -> User:
        user.role = role
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
