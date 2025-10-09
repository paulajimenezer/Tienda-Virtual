"""Servicios/CRUD para pedidos.
- Crear pedido a partir de un carrito
- Cambiar estado
- Listar por usuario
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from Entities.pedidos import Pedidos as PEDIDOS
from Entities.usuarios import Usuarios as USUARIOS
from Entities.direcciones import Direcciones as DIRECCIONES
from Entities.descuentos import Descuentos as DESCUENTOS

ESTADOS_VALIDOS = {"Creado", "Pagado", "Enviado", "Entregado", "Cancelado"}
TRANSICIONES_VALIDAS = {
    "Creado": {"Pagado", "Cancelado"},
    "Pagado": {"Enviado", "Cancelado"},
    "Enviado": {"Entregado"},
    "Entregado": set(),
    "Cancelado": set(),
}
ESTADOS_FINALES = {"Entregado", "Cancelado"}


class PedidoCRUD:
    """
    Operaciones CRUD y utilidades para Pedidos.

    Métodos:
        - crear_pedido: Crea un pedido validando usuario, dirección, descuento y valores.
        - obtener_pedido: Obtiene un pedido por su UUID.
        - obtener_pedidos: Lista pedidos con paginación.
        - obtener_pedidos_usuario: Lista pedidos de un usuario.
        - cambiar_estado: Cambia el estado del pedido validando transiciones.
        - actualizar_pedido: Actualiza campos del pedido (excepto estado).
        - recalcular_total: Recalcula el total del pedido a partir de sus ítems.
        - eliminar_pedido: Elimina un pedido si no está en estado final ni tiene factura ligada.
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

    def crear_pedido(
        self,
        id_usuario: UUID,
        id_direccion: UUID,
        total: float = 0.0,
        estado: str = "Creado",
        id_descuento: Optional[UUID] = None,
        fecha_pedido: Optional[datetime] = None,
        id_usuario_crea: Optional[UUID] = None,
    ) -> PEDIDOS:
        """
        Crea un pedido validando usuario, dirección, descuento y valores.

        Args:
            id_usuario: UUID del usuario.
            id_direccion: UUID de la dirección.
            total: Total del pedido.
            estado: Estado inicial del pedido.
            id_descuento: UUID del descuento (opcional).
            fecha_pedido: Fecha del pedido (opcional).
            id_usuario_crea: UUID del usuario que crea el pedido (opcional).

        Returns:
            Instancia creada de PEDIDOS.

        Raises:
            ValueError: Si algún dato es inválido o las referencias no existen.
        """
        if total is None or total < 0:
            raise ValueError("El total no puede ser negativo")
        estado_norm = (estado or "").strip().title()
        if estado_norm not in ESTADOS_VALIDOS:
            raise ValueError("Estado de pedido inválido")

        usuario = self.db.get(USUARIOS, id_usuario)
        if not usuario:
            raise ValueError("El usuario especificado no existe")

        direccion = self.db.get(DIRECCIONES, id_direccion)
        if not direccion:
            raise ValueError("La dirección especificada no existe")
        if getattr(direccion, "id_usuario", None) != id_usuario:
            raise ValueError("La dirección no pertenece al usuario")

        if id_descuento:
            if self.db.get(DESCUENTOS, id_descuento) is None:
                raise ValueError("El descuento especificado no existe")

        if id_usuario_crea is None:
            id_usuario_crea = self._admin_fallback()

        obj = PEDIDOS(
            id_usuario=id_usuario,
            id_direccion=id_direccion,
            id_descuento=id_descuento,
            fecha_pedido=fecha_pedido or datetime.utcnow(),
            estado=estado_norm,
            total=total,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def obtener_pedido(self, pedido_id: UUID) -> Optional[PEDIDOS]:
        """
        Obtiene un pedido por su UUID.

        Args:
            pedido_id: UUID del pedido.

        Returns:
            Instancia de PEDIDOS si existe, None en caso contrario.
        """
        return self.db.get(PEDIDOS, pedido_id)

    def obtener_pedidos(self, skip: int = 0, limit: int = 100) -> List[PEDIDOS]:
        """
        Lista pedidos con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de instancias de PEDIDOS.
        """
        return self.db.query(PEDIDOS).offset(skip).limit(limit).all()

    def obtener_pedidos_usuario(
        self, id_usuario: UUID, skip: int = 0, limit: int = 100
    ) -> List[PEDIDOS]:
        """
        Lista pedidos filtrados por usuario propietario.

        Args:
            id_usuario: UUID del usuario.
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de pedidos del usuario indicado.
        """
        return (
            self.db.query(PEDIDOS)
            .filter(PEDIDOS.id_usuario == id_usuario)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def cambiar_estado(
        self,
        pedido_id: UUID,
        nuevo_estado: str,
        id_usuario_edita: Optional[UUID] = None,
    ) -> Optional[PEDIDOS]:
        """
        Cambia el estado del pedido validando transiciones.

        Args:
            pedido_id: UUID del pedido.
            nuevo_estado: Estado destino.
            id_usuario_edita: UUID del usuario que edita (opcional).

        Returns:
            Instancia actualizada de PEDIDOS, o None si no existe.

        Raises:
            ValueError: Si la transición no es válida.
        """
        obj = self.db.get(PEDIDOS, pedido_id)
        if not obj:
            return None

        estado_actual = (obj.estado or "").strip().title()
        destino = (nuevo_estado or "").strip().title()
        if destino not in ESTADOS_VALIDOS:
            raise ValueError("Estado de pedido inválido")
        if destino not in TRANSICIONES_VALIDAS.get(estado_actual, set()):
            raise ValueError(f"Transición inválida: {estado_actual} -> {destino}")

        if id_usuario_edita is None:
            id_usuario_edita = self._admin_fallback()

        obj.estado = destino
        if hasattr(obj, "id_usuario_edita"):
            obj.id_usuario_edita = id_usuario_edita
        obj.fecha_edicion = datetime.utcnow()

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def actualizar_pedido(
        self, pedido_id: UUID, id_usuario_edita: Optional[UUID] = None, **kwargs
    ) -> Optional[PEDIDOS]:
        """
        Actualiza campos del pedido (excepto estado, que debe ir por cambiar_estado).

        Args:
            pedido_id: UUID del pedido.
            id_usuario_edita: UUID del usuario que edita (opcional).
            **kwargs: Campos a actualizar.

        Returns:
            Instancia actualizada de PEDIDOS, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        obj = self.db.get(PEDIDOS, pedido_id)
        if not obj:
            return None

        if (obj.estado or "").strip().title() in ESTADOS_FINALES:
            raise ValueError("No se puede editar un pedido en estado final")

        if "estado" in kwargs:
            destino = kwargs.pop("estado")
            obj = self.cambiar_estado(pedido_id, destino, id_usuario_edita)
            if not kwargs:
                return obj

        if "id_direccion" in kwargs:
            dir_id = kwargs["id_direccion"]
            direccion = self.db.get(DIRECCIONES, dir_id)
            if not direccion:
                raise ValueError("La nueva dirección no existe")
            if getattr(direccion, "id_usuario", None) != obj.id_usuario:
                raise ValueError("La dirección no pertenece al usuario del pedido")

        if "id_descuento" in kwargs and kwargs["id_descuento"] is not None:
            if self.db.get(DESCUENTOS, kwargs["id_descuento"]) is None:
                raise ValueError("El descuento especificado no existe")

        if "total" in kwargs:
            total = kwargs["total"]
            if total is None or total < 0:
                raise ValueError("El total no puede ser negativo")

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
        return obj

    def recalcular_total(self, pedido_id: UUID) -> Optional[float]:
        """
        Recalcula el total del pedido a partir de sus ítems.

        Args:
            pedido_id: UUID del pedido.

        Returns:
            Nuevo total calculado, o None si el pedido no existe.
        """
        from Entities.pedido_items import Pedido_items as PEDIDO_ITEMS

        obj = self.db.get(PEDIDOS, pedido_id)
        if not obj:
            return None

        total = 0.0
        for it in self.db.query(PEDIDO_ITEMS).filter(
            PEDIDO_ITEMS.id_pedido == pedido_id
        ):
            total += float(getattr(it, "cantidad", 0) or 0) * float(
                getattr(it, "precio_unitario", 0.0) or 0.0
            )
        obj.total = total
        obj.fecha_edicion = datetime.utcnow()
        self.db.commit()
        self.db.refresh(obj)
        return total

    def eliminar_pedido(self, pedido_id: UUID) -> bool:
        """
        Elimina un pedido si no está en estado final ni tiene factura ligada.

        Args:
            pedido_id: UUID del pedido.

        Returns:
            True si se eliminó correctamente, False si no existe.

        Raises:
            ValueError: Si el pedido está en estado final o tiene factura asociada.
        """
        obj = self.db.get(PEDIDOS, pedido_id)
        if not obj:
            return False

        if (obj.estado or "").strip().title() in ESTADOS_FINALES:
            raise ValueError("No se puede eliminar un pedido en estado final")

        if getattr(obj, "factura", None):
            raise ValueError("El pedido tiene factura asociada")

        self.db.delete(obj)
        self.db.commit()
        return True
