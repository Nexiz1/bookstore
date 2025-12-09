from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_item(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_items(self, skip: int = 0, limit: int = 100):
        return self.db.query(Item).offset(skip).limit(limit).all()

    def create_item(self, item: ItemCreate):
        db_item = Item(**item.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update_item(self, item_id: int, item: ItemUpdate):
        db_item = self.get_item(item_id)
        if db_item:
            update_data = item.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int):
        db_item = self.get_item(item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
        return db_item
