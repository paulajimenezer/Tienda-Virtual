"""Operaciones de catálogo para Tipo de Documento."""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.tipo_documento import (
    TIPO_DOCUMENTO,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
)


def get_tipo_documento(
    db: Session, tipo_documento_id: UUID
) -> Optional[TIPO_DOCUMENTO]:
    return db.get(TIPO_DOCUMENTO, tipo_documento_id)


def list_tipos_documento(
    db: Session, skip: int = 0, limit: int = 100
) -> List[TIPO_DOCUMENTO]:
    return db.query(TIPO_DOCUMENTO).offset(skip).limit(limit).all()


def create_tipo_documento(db: Session, data: TipoDocumentoCreate) -> TIPO_DOCUMENTO:
    obj = TIPO_DOCUMENTO(
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


def update_tipo_documento(
    db: Session, tipo_documento_id: UUID, data: TipoDocumentoUpdate
) -> Optional[TIPO_DOCUMENTO]:
    obj = db.get(TIPO_DOCUMENTO, tipo_documento_id)
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


def delete_tipo_documento(db: Session, tipo_documento_id: UUID) -> bool:
    obj = db.get(TIPO_DOCUMENTO, tipo_documento_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
