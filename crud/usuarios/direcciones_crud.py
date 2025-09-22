"""CRUD para direcciones de usuario."""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.direcciones import DIRECCIONES, DireccionCreate, DireccionUpdate


def get_direccion(db: Session, direccion_id: UUID) -> Optional[DIRECCIONES]:
    return db.get(DIRECCIONES, direccion_id)


def list_direcciones_usuario(
    db: Session, id_usuario: UUID, skip: int = 0, limit: int = 100
) -> List[DIRECCIONES]:
    return (
        db.query(DIRECCIONES)
        .filter(DIRECCIONES.id_usuario == id_usuario)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_direccion(db: Session, data: DireccionCreate) -> DIRECCIONES:
    obj = DIRECCIONES(
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


def update_direccion(
    db: Session, direccion_id: UUID, data: DireccionUpdate
) -> Optional[DIRECCIONES]:
    obj = db.get(DIRECCIONES, direccion_id)
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


def delete_direccion(db: Session, direccion_id: UUID) -> bool:
    obj = db.get(DIRECCIONES, direccion_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
