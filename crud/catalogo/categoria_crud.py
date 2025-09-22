"""Operaciones CRUD para Categorías.
Basado en el patrón de Programacion-de-software/03-Introduccion-ORM/crud.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from Entities.categorias import CATEGORIAS, CategoriaCreate, CategoriaUpdate


def get_categoria(db: Session, categoria_id: int) -> Optional[CATEGORIAS]:
    return db.get(CATEGORIAS, categoria_id)


def list_categorias(db: Session, skip: int = 0, limit: int = 100) -> List[CATEGORIAS]:
    return db.query(CATEGORIAS).offset(skip).limit(limit).all()


def create_categoria(db: Session, data: CategoriaCreate) -> CATEGORIAS:
    payload = (
        data.dict(exclude_unset=True)
        if hasattr(data, "dict")
        else data.model_dump(exclude_unset=True)
    )
    obj = CATEGORIAS(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_categoria(
    db: Session, categoria_id: int, data: CategoriaUpdate
) -> Optional[CATEGORIAS]:
    obj = db.get(CATEGORIAS, categoria_id)
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


def delete_categoria(db: Session, categoria_id: int) -> bool:
    obj = db.query(CATEGORIAS).get(categoria_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
