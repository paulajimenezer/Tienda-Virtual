"""CRUD/servicios para facturas."""

from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID

from Entities.facturas import FACTURAS, FacturaCreate, FacturaUpdate


def get_factura(db: Session, factura_id: UUID) -> Optional[FACTURAS]:
    return db.get(FACTURAS, factura_id)


def list_facturas_pedido(
    db: Session, id_pedido: UUID, skip: int = 0, limit: int = 100
) -> List[FACTURAS]:
    return (
        db.query(FACTURAS)
        .filter(FACTURAS.id_pedido == id_pedido)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_factura(db: Session, data: FacturaCreate) -> FACTURAS:
    obj = FACTURAS(
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


def update_factura(
    db: Session, factura_id: UUID, data: FacturaUpdate
) -> Optional[FACTURAS]:
    obj = db.get(FACTURAS, factura_id)
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
