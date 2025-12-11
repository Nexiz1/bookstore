from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.exceptions.auth_exceptions import (
    ForbiddenException,
    InvalidCredentialsException,
)
from app.exceptions.user_exceptions import UserNotFoundException
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordChange, UserListResponse, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_me(self, user_id: int) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

    def update_me(self, user_id: int, update_data: UserUpdate) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        update_dict = update_data.model_dump(exclude_unset=True)
        updated_user = self.user_repo.update(user, update_dict)
        return updated_user

    def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        # 현재 비밀번호 검증
        if not verify_password(password_data.current_password, user.password):
            raise InvalidCredentialsException("Current password is incorrect")

        # 새 비밀번호 해싱 및 저장
        hashed_password = get_password_hash(password_data.new_password)
        self.user_repo.update_password(user, hashed_password)
        return True

    def get_all_users(
        self, page: int = 1, size: int = 10, keyword: str = None
    ) -> UserListResponse:
        skip = (page - 1) * size
        users, total = self.user_repo.get_all(skip=skip, limit=size, keyword=keyword)
        return UserListResponse(
            users=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
        )

    def update_user_role(self, user_id: int, role: str, admin_id: int) -> UserResponse:
        # 자기 자신의 권한은 변경 불가
        if user_id == admin_id:
            raise ForbiddenException("Cannot change your own role")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        updated_user = self.user_repo.update_role(user, role)
        return updated_user
