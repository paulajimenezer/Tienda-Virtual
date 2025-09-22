"""CRUD para Items de Pedido con validaciones de stock y actualización de totales."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from Entities.pedido_items import Pedido_items as PEDIDO_ITEMS
from Entities.pedidos import Pedidos as PEDIDOS
from Entities.productos import Productos as PRODUCTOS
from Entities.usuarios import Usuarios as USUARIOS

ESTADOS_FINALES = {"Entregado", "Cancelado"}


class PedidoItemCRUD:
    """
    Operaciones CRUD para items de pedido.

    Métodos:
        - crear_pedido_item: Crea un ítem de pedido validando stock y pedido editable.
        - obtener_pedido_item: Obtiene un ítem por su UUID.
        - listar_items: Lista ítems de un pedido con paginación.
        - actualizar_pedido_item: Actualiza cantidad/precio del ítem, ajustando stock y total del pedido.
        - eliminar_pedido_item: Elimina un ítem del pedido, restaurando stock y total.
    """

    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def _admin_fallback(self) -> UUID:
        """
        Obtiene el UUID de un usuario administrador para auditoría.

        Returns:
            UUID del usuario administrador.

        Raises:
            ValueError: Si no existe un usuario administrador.
        """
        admin = self.db.query(USUARIOS).filter(USUARIOS.es_admin == True).first()
        if not admin:
            raise ValueError("No se encontró un usuario administrador")
        return getattr(admin, "id", None) or getattr(admin, "id_usuario", None)

    def _ensure_pedido_editable(self, pedido: PEDIDOS):
        """
        Verifica que el pedido no esté en estado final.

        Args:
            pedido: Instancia de PEDIDOS.

        Raises:
            ValueError: Si el pedido está en estado final.
        """
        estado = (pedido.estado or "").strip().title()
        if estado in ESTADOS_FINALES:
            raise ValueError(
                "No se pueden modificar ítems de un pedido en estado final"
            )

    def _recalcular_total(self, id_pedido: UUID):
        """
        Recalcula el total del pedido asociado.

        Args:
            id_pedido: UUID del pedido.
        """
        from .pedidos_crud import PedidoCRUD  

        PedidoCRUD(self.db).recalcular_total(id_pedido)

    def crear_pedido_item(
        self,
        id_pedido: UUID,
        id_producto: UUID,
        cantidad: int,
        precio_unitario: Optional[float] = None,
        id_usuario_crea: Optional[UUID] = None,
    ) -> PEDIDO_ITEMS:
        """
        Crea un ítem de pedido validando stock y pedido editable.

        Args:
            id_pedido: UUID del pedido.
            id_producto: UUID del producto.
            cantidad: Cantidad del producto.
            precio_unitario: Precio unitario (opcional).
            id_usuario_crea: UUID del usuario que crea el ítem (opcional).

        Returns:
            Instancia creada de PEDIDO_ITEMS.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        if cantidad is None or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        pedido = self.db.get(PEDIDOS, id_pedido)
        if not pedido:
            raise ValueError("El pedido especificado no existe")
        self._ensure_pedido_editable(pedido)

        producto = self.db.get(PRODUCTOS, id_producto)
        if not producto:
            raise ValueError("El producto especificado no existe")

        if precio_unitario is None:
            precio_unitario = float(getattr(producto, "precio", 0.0) or 0.0)
        if precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo")

        stock = int(getattr(producto, "stock", 0) or 0)
        if cantidad > stock:
            raise ValueError("Stock insuficiente para el producto")

        if id_usuario_crea is None:
            id_usuario_crea = self._admin_fallback()

        producto.stock = stock - cantidad
        obj = PEDIDO_ITEMS(
            id_pedido=id_pedido,
            id_producto=id_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        self._recalcular_total(id_pedido)
        return obj

    def obtener_pedido_item(self, item_id: UUID) -> Optional[PEDIDO_ITEMS]:
        """
        Obtiene un ítem de pedido por su UUID.

        Args:
            item_id: UUID del ítem.

        Returns:
            Instancia de PEDIDO_ITEMS si existe, None en caso contrario.
        """
        return self.db.get(PEDIDO_ITEMS, item_id)

    def listar_items(
        self, id_pedido: UUID, skip: int = 0, limit: int = 100
    ) -> List[PEDIDO_ITEMS]:
        """
        Lista ítems de un pedido con paginación.

        Args:
            id_pedido: UUID del pedido.
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de ítems del pedido.
        """
        return (
            self.db.query(PEDIDO_ITEMS)
            .filter(PEDIDO_ITEMS.id_pedido == id_pedido)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def actualizar_pedido_item(
        self, item_id: UUID, id_usuario_edita: Optional[UUID] = None, **kwargs
    ) -> Optional[PEDIDO_ITEMS]:
        """
        Actualiza cantidad/precio del ítem, ajustando stock y total del pedido.

        Args:
            item_id: UUID del ítem.
            id_usuario_edita: UUID del usuario que edita (opcional).
            **kwargs: Campos a actualizar.

        Returns:
            Instancia actualizada de PEDIDO_ITEMS, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        obj = self.db.get(PEDIDO_ITEMS, item_id)
        if not obj:
            return None

        pedido = self.db.get(PEDIDOS, obj.id_pedido)
        self._ensure_pedido_editable(pedido)

        if "id_producto" in kwargs or "id_pedido" in kwargs:
            raise ValueError("No se permite cambiar el producto o el pedido del ítem")

        if "precio_unitario" in kwargs and kwargs["precio_unitario"] is not None:
            if kwargs["precio_unitario"] < 0:
                raise ValueError("El precio unitario no puede ser negativo")

        if "cantidad" in kwargs and kwargs["cantidad"] is not None:
            nueva = int(kwargs["cantidad"])
            if nueva <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            producto = self.db.get(PRODUCTOS, obj.id_producto)
            actual = int(obj.cantidad)
            delta = nueva - actual
            if delta != 0:
                stock = int(getattr(producto, "stock", 0) or 0)
                if delta > 0 and delta > stock:
                    raise ValueError("Stock insuficiente para incrementar la cantidad")
                producto.stock = (
                    stock - delta
                )  
        if id_usuario_edita is None:
            id_usuario_edita = self._admin_fallback()
        if hasattr(obj, "id_usuario_edita"):
            obj.id_usuario_edita = id_usuario_edita
        obj.fecha_edicion = datetime.utcnow()

        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        self.db.commit()
        self.db.refresh(obj)
        self._recalcular_total(obj.id_pedido)
        return obj

    def eliminar_pedido_item(self, item_id: UUID) -> bool:
        """
        Elimina un ítem del pedido, restaurando stock y total.

        Args:
            item_id: UUID del ítem.

        Returns:
            True si se eliminó correctamente, False si no existe.

        Raises:
            ValueError: Si el pedido está en estado final.
        """
        obj = self.db.get(PEDIDO_ITEMS, item_id)
        if not obj:
            return False

        pedido = self.db.get(PEDIDOS, obj.id_pedido)
        self._ensure_pedido_editable(pedido)

        producto = self.db.get(PRODUCTOS, obj.id_producto)
        producto.stock = int(getattr(producto, "stock", 0) or 0) + int(obj.cantidad)

        id_pedido = obj.id_pedido
        self.db.delete(obj)
        self.db.commit()

        self._recalcular_total(id_pedido)
        return True
