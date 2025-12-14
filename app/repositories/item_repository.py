"""Item repository module for database operations.

This module handles all database CRUD operations for items.
Repositories do NOT commit by default - the service layer manages transactions.
"""

from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository:
    """Repository for item-related database operations.

    Note:
        By default, methods do NOT commit changes. Pass commit=True
        for single-operation transactions, or let the service layer
        manage commits for multi-operation transactions.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_item(self, item_id: int):
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_items(self, skip: int = 0, limit: int = 100):
        return self.db.query(Item).offset(skip).limit(limit).all()

    def create_item(self, item: ItemCreate, *, commit: bool = True):
        """Create a new item.

        Args:
            item: ItemCreate schema instance.
            commit: If True, commit the transaction. Default True.

        Returns:
            Item: Created item instance.
        """
        db_item = Item(**item.model_dump())
        self.db.add(db_item)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def update_item(self, item_id: int, item: ItemUpdate, *, commit: bool = True):
        """Update an item.

        Args:
            item_id: ID of the item to update.
            item: ItemUpdate schema instance.
            commit: If True, commit the transaction. Default True.

        Returns:
            Item: Updated item instance or None.
        """
        db_item = self.get_item(item_id)
        if db_item:
            update_data = item.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)
            if commit:
                self.db.commit()
                self.db.refresh(db_item)
        return db_item

    def delete_item(self, item_id: int, *, commit: bool = True):
        """Delete an item.

        Args:
            item_id: ID of the item to delete.
            commit: If True, commit the transaction. Default True.

        Returns:
            Item: Deleted item instance or None.
        """
        db_item = self.get_item(item_id)
        if db_item:
            self.db.delete(db_item)
            if commit:
                self.db.commit()
        return db_item
