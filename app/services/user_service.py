from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.exceptions.user_exceptions import UserNotFoundException, UserAlreadyExistsException

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self, user_id: int):
        user = self.repository.get_user(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_users(skip=skip, limit=limit)
    
    def create_user(self, user: UserCreate):
        db_user = self.repository.get_user_by_email(user.email)
        if db_user:
            raise UserAlreadyExistsException(user.email)
        return self.repository.create_user(user)

    def update_user(self, user_id: int, user: UserUpdate):
        db_user = self.repository.get_user(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        return self.repository.update_user(user_id=user_id, user=user)

    def delete_user(self, user_id: int):
        db_user = self.repository.get_user(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)
        return self.repository.delete_user(user_id=user_id)
