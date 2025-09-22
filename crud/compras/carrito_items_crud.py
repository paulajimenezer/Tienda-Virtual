"""CRUD para items del carrito y operaciones de negocio (agregar, actualizar cantidad, eliminar)."""

from typing import Optional, List
from sqlalchemy.orm import Session

from Entities.carrito_items import CARRITO_ITEMS, CarritoItemCreate, CarritoItemUpdate


def get_item(db: Session, item_id: int) -> Optional[CARRITO_ITEMS]:
    return db.get(CARRITO_ITEMS, item_id)


def list_items_carrito(
    db: Session, id_carrito: int, skip: int = 0, limit: int = 100
) -> List[CARRITO_ITEMS]:
    return (
        db.query(CARRITO_ITEMS)
        .filter(CARRITO_ITEMS.id_carrito == id_carrito)
        .offset(skip)
        .limit(limit)
        .all()
    )


def add_item(db: Session, data: CarritoItemCreate) -> CARRITO_ITEMS:
    obj = CARRITO_ITEMS(
        **(
            data.dict(exclude_unset=True)
            if hasattr(data, "dict")
            else data.model_dump(exclude_unset=True)
        )
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_item(
    db: Session, item_id: int, data: CarritoItemUpdate
) -> Optional[CARRITO_ITEMS]:
    obj = db.get(CARRITO_ITEMS, item_id)
    if not obj:
        return None
    for k, v in (
        data.dict(exclude_unset=True)
        if hasattr(data, "dict")
        else data.model_dump(exclude_unset=True)
    ).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def remove_item(db: Session, item_id: int) -> bool:
    obj = db.query(CARRITO_ITEMS).get(item_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
