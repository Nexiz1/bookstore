from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_admin_user, get_current_user, get_user_service
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.schemas.user import (
    PasswordChange,
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[UserResponse])
def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """내 프로필 조회"""
    user = service.get_me(current_user.id)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.patch("/me", response_model=SuccessResponse[UserResponse])
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """내 프로필 수정 (주소, 전화번호 등)"""
    user = service.update_me(current_user.id, update_data)
    return SuccessResponse(
        data=UserResponse.model_validate(user), message="Profile updated successfully"
    )


@router.post("/me/password", response_model=SuccessResponse)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """비밀번호 변경"""
    service.change_password(current_user.id, password_data)
    return SuccessResponse(message="Password changed successfully")


@router.get("/", response_model=SuccessResponse[UserListResponse])
def get_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    service: UserService = Depends(get_user_service),
):
    """전체 회원 목록 조회 (페이지네이션, 검색) - Admin only"""
    result = service.get_all_users(page=page, size=size, keyword=keyword)
    return SuccessResponse(data=result)


@router.patch("/{user_id}/role", response_model=SuccessResponse[UserResponse])
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    admin_user: User = Depends(get_admin_user),
    service: UserService = Depends(get_user_service),
):
    """회원 권한 변경 (User ↔ Seller ↔ Admin) - Admin only"""
    user = service.update_user_role(user_id, role_data.role.value, admin_user.id)
    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User role updated successfully"
    )


@router.patch("/{user_id}/deactivate", response_model=SuccessResponse[UserResponse])
def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    service: UserService = Depends(get_user_service),
):
    """사용자 계정 비활성화 - Admin only

    비활성화된 계정은 로그인 및 API 접근이 차단됩니다.
    관리자 계정은 비활성화할 수 없습니다.
    """
    user = service.deactivate_user(admin_user.id, user_id)
    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User account deactivated successfully"
    )
