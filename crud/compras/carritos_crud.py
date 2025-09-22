"""Servicios/CRUD para carritos.
- Obtener carrito abierto del usuario
- Crear carrito
- Cerrar carrito
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from Entities.carritos import CARRITOS, CarritoCreate, CarritoUpdate


def get_carrito(db: Session, carrito_id: int) -> Optional[CARRITOS]:
    return db.get(CARRITOS, carrito_id)


def get_carrito_abierto_usuario(db: Session, id_usuario: int) -> Optional[CARRITOS]:
    return (
        db.query(CARRITOS)
        .filter(and_(CARRITOS.id_usuario == id_usuario, CARRITOS.estado == "abierto"))
        .first()
    )


def list_carritos_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
) -> List[CARRITOS]:
    return (
        db.query(CARRITOS)
        .filter(CARRITOS.id_usuario == id_usuario)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_carrito(db: Session, data: CarritoCreate) -> CARRITOS:
    obj = CARRITOS(**data.dict(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def cerrar_carrito(db: Session, carrito_id: int) -> Optional[CARRITOS]:
    obj = db.get(CARRITOS, carrito_id)
    if not obj:
        return None
    obj.estado = "cerrado"
    db.commit()
    db.refresh(obj)
    return obj


def update_carrito(
    db: Session, carrito_id: int, data: CarritoUpdate
) -> Optional[CARRITOS]:
    obj = db.get(CARRITOS, carrito_id)
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
