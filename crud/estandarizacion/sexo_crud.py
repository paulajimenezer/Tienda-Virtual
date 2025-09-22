"""Operaciones de catálogo para Sexo."""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.sexo import SEXO, SexoCreate, SexoUpdate


def get_sexo(db: Session, sexo_id: UUID) -> Optional[SEXO]:
    return db.get(SEXO, sexo_id)


def list_sexos(db: Session, skip: int = 0, limit: int = 100) -> List[SEXO]:
    return db.query(SEXO).offset(skip).limit(limit).all()


def create_sexo(db: Session, data: SexoCreate) -> SEXO:
    obj = SEXO(
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


def update_sexo(db: Session, sexo_id: UUID, data: SexoUpdate) -> Optional[SEXO]:
    obj = db.get(SEXO, sexo_id)
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


def delete_sexo(db: Session, sexo_id: UUID) -> bool:
    obj = db.get(SEXO, sexo_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
