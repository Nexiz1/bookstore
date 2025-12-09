from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate
from app.exceptions.item_exceptions import ItemNotFoundException

class ItemService:
    def __init__(self, db: Session):
        self.repository = ItemRepository(db)

    def get_item(self, item_id: int):
        item = self.repository.get_item(item_id)
        if not item:
            raise ItemNotFoundException(item_id)
        return item

    def get_items(self, skip: int = 0, limit: int = 100):
        return self.repository.get_items(skip=skip, limit=limit)

    def create_item(self, item: ItemCreate):
        return self.repository.create_item(item)

    def update_item(self, item_id: int, item: ItemUpdate):
        db_item = self.repository.get_item(item_id)
        if not db_item:
            raise ItemNotFoundException(item_id)
        return self.repository.update_item(item_id=item_id, item=item)

    def delete_item(self, item_id: int):
        db_item = self.repository.get_item(item_id)
        if not db_item:
            raise ItemNotFoundException(item_id)
        return self.repository.delete_item(item_id=item_id)
