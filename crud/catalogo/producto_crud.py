"""Operaciones CRUD para Productos.
Basado en el patrón de Programacion-de-software/03-Introduccion-ORM/crud.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID  # NEW

from Entities.productos import PRODUCTOS, ProductoCreate, ProductoUpdate


def get_producto(db: Session, producto_id: UUID) -> Optional[PRODUCTOS]:
    return db.get(PRODUCTOS, producto_id)


def list_productos(db: Session, skip: int = 0, limit: int = 100) -> List[PRODUCTOS]:
    return db.query(PRODUCTOS).offset(skip).limit(limit).all()


def create_producto(db: Session, data: ProductoCreate) -> PRODUCTOS:
    payload = (
        data.dict(exclude_unset=True)
        if hasattr(data, "dict")
        else data.model_dump(exclude_unset=True)
    )
    obj = PRODUCTOS(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_producto(
    db: Session, producto_id: UUID, data: ProductoUpdate
) -> Optional[PRODUCTOS]:
    obj = db.get(PRODUCTOS, producto_id)
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


def delete_producto(db: Session, producto_id: UUID) -> bool:
    obj = db.query(PRODUCTOS).get(producto_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
