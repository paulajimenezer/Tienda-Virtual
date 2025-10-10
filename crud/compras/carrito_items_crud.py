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

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from Entities.carrito_items import Carrito_items as CARRITO_ITEMS
from Entities.carritos import Carritos as CARRITOS
from Entities.productos import Productos as PRODUCTOS


class CarritoItemsCRUD:
    """
    Clase que gestiona los ítems del carrito. Provee métodos para:
    - obtener/listar ítems
    - agregar (fusionando si existe)
    - actualizar cantidad
    - eliminar ítem
    - vaciar carrito
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_item(self, item_id: UUID) -> Optional[CARRITO_ITEMS]:
        return self.db.get(CARRITO_ITEMS, item_id)

    def obtener_items(self, skip: int = 0, limit: int = 100) -> List[CARRITO_ITEMS]:
        return self.db.query(CARRITO_ITEMS).offset(skip).limit(limit).all()

    def listar_items(
        self, id_carrito: UUID, skip: int = 0, limit: int = 100
    ) -> List[CARRITO_ITEMS]:
        return (
            self.db.query(CARRITO_ITEMS)
            .filter(CARRITO_ITEMS.id_carrito == id_carrito)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _assert_carrito_activo(self, id_carrito: UUID):
        carrito = self.db.get(CARRITOS, id_carrito)
        if not carrito:
            raise ValueError("El carrito no existe")
        if not bool(getattr(carrito, "activo", True)):
            raise ValueError("El carrito no está activo")

    def _assert_producto_activo(self, id_producto: UUID):
        prod = self.db.get(PRODUCTOS, id_producto)
        if not prod:
            raise ValueError("El producto no existe")
        if hasattr(prod, "activo") and not bool(prod.activo):
            raise ValueError("El producto no está activo")
        return prod

    def crear_item(
        self,
        *,
        id_carrito: UUID,
        id_producto: UUID,
        cantidad: int,
        id_usuario_crea: Optional[UUID] = None,
    ) -> CARRITO_ITEMS:
        if cantidad is None or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        self._assert_carrito_activo(id_carrito)
        prod = self._assert_producto_activo(id_producto)

        if hasattr(prod, "stock"):
            total_existente = (
                self.db.query(CARRITO_ITEMS)
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
            if prod.stock is not None and (total_en_carrito + cantidad) > int(
                prod.stock
            ):
                raise ValueError("Cantidad supera stock disponible")

        existente = (
            self.db.query(CARRITO_ITEMS)
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
            self.db.commit()
            self.db.refresh(existente)
            return existente

        obj = CARRITO_ITEMS(
            id_carrito=id_carrito,
            id_producto=id_producto,
            cantidad=int(cantidad),
            id_usuario_crea=id_usuario_crea or id_carrito,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def actualizar_item_cantidad(
        self,
        item_id: UUID,
        *,
        cantidad: int,
        id_usuario_edita: Optional[UUID] = None,
    ) -> Optional[CARRITO_ITEMS]:
        obj = self.db.get(CARRITO_ITEMS, item_id)
        if not obj:
            return None
        self._assert_carrito_activo(obj.id_carrito)
        if cantidad is None or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        prod = self._assert_producto_activo(obj.id_producto)
        if (
            hasattr(prod, "stock")
            and prod.stock is not None
            and cantidad > int(prod.stock)
        ):
            raise ValueError("Cantidad supera stock disponible")

        obj.cantidad = int(cantidad)
        if hasattr(obj, "id_usuario_edita") and id_usuario_edita:
            obj.id_usuario_edita = id_usuario_edita

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def eliminar_item(self, item_id: UUID) -> bool:
        obj = self.db.get(CARRITO_ITEMS, item_id)
        if not obj:
            return False
        self._assert_carrito_activo(obj.id_carrito)
        self.db.delete(obj)
        self.db.commit()
        return True

    def clear_carrito(self, id_carrito: UUID) -> int:
        self._assert_carrito_activo(id_carrito)
        q = self.db.query(CARRITO_ITEMS).filter(CARRITO_ITEMS.id_carrito == id_carrito)
        count = q.count()
        q.delete(synchronize_session=False)
        self.db.commit()
        return count
