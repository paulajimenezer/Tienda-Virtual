"""Operaciones de catálogo para Roles.
- list/get: abiertos
- create/update/delete: típicamente administrados
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.roles import ROLES, RolCreate, RolUpdate


def get_rol(db: Session, rol_id: UUID) -> Optional[ROLES]:
    return db.get(ROLES, rol_id)


def list_roles(db: Session, skip: int = 0, limit: int = 100) -> List[ROLES]:
    return db.query(ROLES).offset(skip).limit(limit).all()


def create_rol(db: Session, data: RolCreate) -> ROLES:
    obj = ROLES(
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


def update_rol(db: Session, rol_id: UUID, data: RolUpdate) -> Optional[ROLES]:
    obj = db.get(ROLES, rol_id)
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


def delete_rol(db: Session, rol_id: UUID) -> bool:
    obj = db.get(ROLES, rol_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
