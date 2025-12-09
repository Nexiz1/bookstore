from fastapi import Depends
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.item_service import ItemService
from app.services.user_service import UserService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    return ItemService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)