"""Lectura/ajustes de items de pedido.
En la mayoría de casos, los items de pedido son de solo lectura tras confirmar.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from Entities.pedido_items import PEDIDO_ITEMS, PedidoItemCreate, PedidoItemUpdate


def get_pedido_item(db: Session, item_id: int) -> Optional[PEDIDO_ITEMS]:
    return db.get(PEDIDO_ITEMS, item_id)


def list_pedido_items(
    db: Session, pedido_id: int, skip: int = 0, limit: int = 100
) -> List[PEDIDO_ITEMS]:
    return (
        db.query(PEDIDO_ITEMS)
        .filter(PEDIDO_ITEMS.id_pedido == pedido_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_pedido_item(db: Session, data: PedidoItemCreate) -> PEDIDO_ITEMS:
    obj = PEDIDO_ITEMS(
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


def update_pedido_item(
    db: Session, item_id: int, data: PedidoItemUpdate
) -> Optional[PEDIDO_ITEMS]:
    obj = db.get(PEDIDO_ITEMS, item_id)
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
