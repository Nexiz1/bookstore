from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
)
from app.exceptions.user_exceptions import UserAlreadyExistsException
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def signup(self, user_data: UserCreate) -> dict:
        # 이메일 중복 체크
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException("Email already registered")

        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)

        # 사용자 생성
        user_dict = user_data.model_dump()
        user_dict["password"] = hashed_password

        user = self.user_repo.create(user_dict)
        return user

    def login(self, email: str, password: str) -> TokenResponse:
        # 사용자 조회
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsException()

        # 비활성화된 계정 체크
        if not user.is_active:
            raise InvalidCredentialsException("Account is deactivated")

        # 비밀번호 검증
        if not verify_password(password, user.password):
            raise InvalidCredentialsException()

        # 토큰 생성
        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        # 리프레시 토큰 검증
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenException()

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(int(user_id))
        if not user:
            raise InvalidTokenException()

        # 새 토큰 발급
        token_data = {"sub": str(user.id), "role": user.role}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=new_access_token, refresh_token=new_refresh_token
        )

    def logout(self) -> bool:
        # JWT는 stateless이므로 클라이언트에서 토큰 삭제로 처리
        # 실제 구현에서는 토큰 블랙리스트를 사용할 수 있음
        return True

    def get_current_user_from_token(self, token: str):
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise InvalidTokenException()

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(int(user_id))
        if not user:
            raise InvalidTokenException()

        return user
