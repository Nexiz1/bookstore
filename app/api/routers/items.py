from typing import List
from fastapi import APIRouter, Depends
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.schemas.response import SuccessResponse
from app.api.dependencies import get_item_service
from app.services.item_service import ItemService

router = APIRouter()

@router.post("/", response_model=SuccessResponse[Item], status_code=201)
def create_item(item: ItemCreate, service: ItemService = Depends(get_item_service)):
    created_item = service.create_item(item)
    return SuccessResponse(data=created_item)

@router.get("/", response_model=SuccessResponse[List[Item]])
def read_items(skip: int = 0, limit: int = 100, service: ItemService = Depends(get_item_service)):
    items = service.get_items(skip=skip, limit=limit)
    return SuccessResponse(data=items)

@router.get("/{item_id}", response_model=SuccessResponse[Item])
def read_item(item_id: int, service: ItemService = Depends(get_item_service)):
    item = service.get_item(item_id)
    return SuccessResponse(data=item)

@router.put("/{item_id}", response_model=SuccessResponse[Item])
def update_item(item_id: int, item: ItemUpdate, service: ItemService = Depends(get_item_service)):
    updated_item = service.update_item(item_id, item)
    return SuccessResponse(data=updated_item)

@router.delete("/{item_id}", response_model=SuccessResponse[Item])
def delete_item(item_id: int, service: ItemService = Depends(get_item_service)):
    deleted_item = service.delete_item(item_id)
    return SuccessResponse(data=deleted_item)
