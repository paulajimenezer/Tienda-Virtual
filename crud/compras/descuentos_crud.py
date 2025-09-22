"""CRUD para descuentos (administrado)."""

from typing import Optional, List
from sqlalchemy.orm import Session

from Entities.descuentos import DESCUENTOS, DescuentoCreate, DescuentoUpdate


def get_descuento(db: Session, descuento_id: int) -> Optional[DESCUENTOS]:
    return db.get(DESCUENTOS, descuento_id)


def list_descuentos(db: Session, skip: int = 0, limit: int = 100) -> List[DESCUENTOS]:
    return db.query(DESCUENTOS).offset(skip).limit(limit).all()


def create_descuento(db: Session, data: DescuentoCreate) -> DESCUENTOS:
    obj = DESCUENTOS(
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


def update_descuento(
    db: Session, descuento_id: int, data: DescuentoUpdate
) -> Optional[DESCUENTOS]:
    obj = db.get(DESCUENTOS, descuento_id)
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


def delete_descuento(db: Session, descuento_id: int) -> bool:
    obj = db.get(DESCUENTOS, descuento_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
