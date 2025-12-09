from typing import List
from fastapi import APIRouter, Depends
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.response import SuccessResponse
from app.api.dependencies import get_user_service
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=SuccessResponse[User], status_code=201)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    created_user = service.create_user(user)
    return SuccessResponse(data=created_user)

@router.get("/", response_model=SuccessResponse[List[User]])
def read_users(skip: int = 0, limit: int = 100, service: UserService = Depends(get_user_service)):
    users = service.get_users(skip=skip, limit=limit)
    return SuccessResponse(data=users)

@router.get("/{user_id}", response_model=SuccessResponse[User])
def read_user(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_user(user_id)
    return SuccessResponse(data=user)

@router.put("/{user_id}", response_model=SuccessResponse[User])
def update_user(user_id: int, user: UserUpdate, service: UserService = Depends(get_user_service)):
    updated_user = service.update_user(user_id, user)
    return SuccessResponse(data=updated_user)

@router.delete("/{user_id}", response_model=SuccessResponse[User])
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    deleted_user = service.delete_user(user_id)
    return SuccessResponse(data=deleted_user)
