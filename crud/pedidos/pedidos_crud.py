"""Servicios/CRUD para pedidos.
- Crear pedido a partir de un carrito
- Cambiar estado
- Listar por usuario
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from Entities.pedidos import PEDIDOS, PedidoCreate, PedidoUpdate


def get_pedido(db: Session, pedido_id: int) -> Optional[PEDIDOS]:
    return db.get(PEDIDOS, pedido_id)


def list_pedidos_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
) -> List[PEDIDOS]:
    return (
        db.query(PEDIDOS)
        .filter(PEDIDOS.id_usuario == id_usuario)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_pedido(db: Session, data: PedidoCreate) -> PEDIDOS:
    obj = PEDIDOS(
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


def update_pedido(db: Session, pedido_id: int, data: PedidoUpdate) -> Optional[PEDIDOS]:
    obj = db.get(PEDIDOS, pedido_id)
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
