"""Operaciones CRUD para Usuarios.
Basado en el patrón de Programacion-de-software/03-Introduccion-ORM/crud.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.usuarios import USUARIOS, UsuarioCreate, UsuarioUpdate


def get_usuario(db: Session, usuario_id: UUID) -> Optional[USUARIOS]:
    return db.get(USUARIOS, usuario_id)


def list_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[USUARIOS]:
    return db.query(USUARIOS).offset(skip).limit(limit).all()


def create_usuario(db: Session, data: UsuarioCreate) -> USUARIOS:
    payload = (
        data.dict(exclude_unset=True)
        if hasattr(data, "dict")
        else data.model_dump(exclude_unset=True)
    )
    obj = USUARIOS(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_usuario(
    db: Session, usuario_id: UUID, data: UsuarioUpdate
) -> Optional[USUARIOS]:
    obj = db.get(USUARIOS, usuario_id)
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


def delete_usuario(db: Session, usuario_id: UUID) -> bool:
    obj = db.get(USUARIOS, usuario_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
