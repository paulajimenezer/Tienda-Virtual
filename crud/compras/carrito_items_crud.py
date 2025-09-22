"""CRUD para la entidad Carrito_items.

Permite:
- Obtener item por ID.
- Listar items de un carrito.
- Agregar producto al carrito (fusiona si ya existe).
- Actualizar cantidad de un item.
- Eliminar item del carrito.
- Limpiar todos los items de un carrito.

Valida existencia y estado de carrito y producto.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from Entities.carrito_items import Carrito_items as CARRITO_ITEMS
from Entities.carritos import Carritos as CARRITOS
from Entities.productos import Productos as PRODUCTOS


def get_item(db: Session, item_id: UUID) -> Optional[CARRITO_ITEMS]:
    """Obtiene un item del carrito por su ID."""
    return db.get(CARRITO_ITEMS, item_id)


def list_items_carrito(
    db: Session, id_carrito: UUID, skip: int = 0, limit: int = 100
) -> List[CARRITO_ITEMS]:
    """Lista los items de un carrito con paginación."""
    return (
        db.query(CARRITO_ITEMS)
        .filter(CARRITO_ITEMS.id_carrito == id_carrito)
        .offset(skip)
        .limit(limit)
        .all()
    )


def _assert_carrito_activo(db: Session, id_carrito: UUID):
    """Valida que el carrito exista y esté activo."""
    carrito = db.get(CARRITOS, id_carrito)
    if not carrito:
        raise ValueError("El carrito no existe")
    if not bool(getattr(carrito, "activo", True)):
        raise ValueError("El carrito no está activo")


def _assert_producto_activo(db: Session, id_producto: UUID):
    """Valida que el producto exista y esté activo."""
    prod = db.get(PRODUCTOS, id_producto)
    if not prod:
        raise ValueError("El producto no existe")
    if hasattr(prod, "activo") and not bool(prod.activo):
        raise ValueError("El producto no está activo")
    return prod


def add_item(
    db: Session,
    *,
    id_carrito: UUID,
    id_producto: UUID,
    cantidad: int,
    id_usuario_crea: Optional[UUID] = None,
) -> CARRITO_ITEMS:
    """
    Agrega un producto al carrito. Si ya existe el item del mismo producto en el carrito,
    incrementa la cantidad. No modifica stock del producto.

    Args:
        db: Sesión de base de datos.
        id_carrito: UUID del carrito.
        id_producto: UUID del producto.
        cantidad: Cantidad a agregar.
        id_usuario_crea: UUID del usuario que crea el item (opcional).

    Returns:
        Instancia de Carrito_items.
    """
    if cantidad is None or cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    _assert_carrito_activo(db, id_carrito)
    prod = _assert_producto_activo(db, id_producto)

    # Validar contra stock disponible sin reservarlo
    if hasattr(prod, "stock"):
        total_existente = (
            db.query(CARRITO_ITEMS)
            .filter(
                and_(
                    CARRITO_ITEMS.id_carrito == id_carrito,
                    CARRITO_ITEMS.id_producto == id_producto,
                )
            )
            .with_entities(CARRITO_ITEMS.cantidad)
            .all()
        )
        total_en_carrito = (
            sum(q or 0 for (q,) in total_existente) if total_existente else 0
        )
        if prod.stock is not None and (total_en_carrito + cantidad) > int(prod.stock):
            raise ValueError("Cantidad supera stock disponible")

    existente = (
        db.query(CARRITO_ITEMS)
        .filter(
            and_(
                CARRITO_ITEMS.id_carrito == id_carrito,
                CARRITO_ITEMS.id_producto == id_producto,
            )
        )
        .first()
    )
    if existente:
        existente.cantidad = int(existente.cantidad) + int(cantidad)
        db.commit()
        db.refresh(existente)
        return existente

    obj = CARRITO_ITEMS(
        id_carrito=id_carrito,
        id_producto=id_producto,
        cantidad=int(cantidad),
        id_usuario_crea=id_usuario_crea or id_carrito,  # fallback simple
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_item_cantidad(
    db: Session,
    item_id: UUID,
    *,
    cantidad: int,
    id_usuario_edita: Optional[UUID] = None,
) -> Optional[CARRITO_ITEMS]:
    """
    Actualiza la cantidad del item. No modifica stock del producto.

    Args:
        db: Sesión de base de datos.
        item_id: UUID del item.
        cantidad: Nueva cantidad.
        id_usuario_edita: UUID del usuario que edita (opcional).

    Returns:
        Instancia de Carrito_items actualizada o None si no existe.
    """
    obj = db.get(CARRITO_ITEMS, item_id)
    if not obj:
        return None
    _assert_carrito_activo(db, obj.id_carrito)
    if cantidad is None or cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    prod = _assert_producto_activo(db, obj.id_producto)
    if hasattr(prod, "stock") and prod.stock is not None and cantidad > int(prod.stock):
        raise ValueError("Cantidad supera stock disponible")

    obj.cantidad = int(cantidad)
    if hasattr(obj, "id_usuario_edita") and id_usuario_edita:
        obj.id_usuario_edita = id_usuario_edita

    db.commit()
    db.refresh(obj)
    return obj


def remove_item(db: Session, item_id: UUID) -> bool:
    """Elimina un item del carrito por su ID."""
    obj = db.get(CARRITO_ITEMS, item_id)
    if not obj:
        return False
    _assert_carrito_activo(db, obj.id_carrito)
    db.delete(obj)
    db.commit()
    return True


def clear_carrito(db: Session, id_carrito: UUID) -> int:
    """
    Elimina todos los items del carrito.

    Args:
        db: Sesión de base de datos.
        id_carrito: UUID del carrito.

    Returns:
        Cantidad de items eliminados.
    """
    _assert_carrito_activo(db, id_carrito)
    q = db.query(CARRITO_ITEMS).filter(CARRITO_ITEMS.id_carrito == id_carrito)
    count = q.count()
    q.delete(synchronize_session=False)
    db.commit()
    return count
