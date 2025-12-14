from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_auth_service, get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.schemas.auth import TokenRefresh, TokenResponse
from app.schemas.response import SuccessResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=SuccessResponse[UserResponse], status_code=201)
@limiter.limit("10/minute")
def signup(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """회원가입 (일반 유저)

    Rate Limit: 분당 10회
    """
    user = auth_service.signup(user_data)
    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User registered successfully"
    )


@router.post("/login", response_model=SuccessResponse[TokenResponse])
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """로그인 (Access/Refresh Token 발급)

    Rate Limit: 분당 5회 (Brute Force 방지)
    """
    tokens = auth_service.login(login_data.email, login_data.password)
    return SuccessResponse(data=tokens, message="Login successful")


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
@limiter.limit("30/minute")
def refresh_token(
    request: Request,
    token_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Access Token 재발급

    Rate Limit: 분당 30회
    """
    tokens = auth_service.refresh_token(token_data.refresh_token)
    return SuccessResponse(data=tokens, message="Token refreshed successfully")


@router.post("/logout", response_model=SuccessResponse)
def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """로그아웃"""
    auth_service.logout()
    return SuccessResponse(message="Logged out successfully")
