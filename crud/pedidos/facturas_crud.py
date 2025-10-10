"""CRUD para Facturas con validaciones de unicidad y vínculo a pedido."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from Entities.facturas import Facturas as FACTURAS
from Entities.pedidos import Pedidos as PEDIDOS
from Entities.usuarios import Usuarios as USUARIOS


class FacturaCRUD:
    """
    Operaciones CRUD para Facturas.

    Métodos:
        - crear_factura: Crea una factura validando pedido, unicidad y montos.
        - obtener_factura: Obtiene una factura por su UUID.
        - obtener_facturas_por_pedido: Lista facturas de un pedido.
        - actualizar_factura: Actualiza número y/o montos de la factura.
        - eliminar_factura: Elimina una factura por su UUID.
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

    def _numero_existe(self, numero: str, excluir_id: Optional[UUID] = None) -> bool:
        """
        Verifica si el número de factura ya existe.

        Args:
            numero: Número de factura.
            excluir_id: UUID de factura a excluir (opcional).

        Returns:
            True si existe, False si no.
        """
        q = self.db.query(FACTURAS).filter(FACTURAS.numero_factura == numero)
        if excluir_id:
            q = q.filter(FACTURAS.id != excluir_id)
        return self.db.query(q.exists()).scalar()

    def crear_factura(
        self,
        id_pedido: UUID,
        numero_factura: str,
        subtotal: float,
        impuesto: float,
        total: float,
        fecha_emision: Optional[datetime] = None,
        id_usuario_crea: Optional[UUID] = None,
    ) -> FACTURAS:
        """
        Crea una factura validando pedido, unicidad y montos.

        Args:
            id_pedido: UUID del pedido.
            numero_factura: Número de factura.
            subtotal: Subtotal de la factura.
            impuesto: Impuesto aplicado.
            total: Total de la factura.
            fecha_emision: Fecha de emisión (opcional).
            id_usuario_crea: UUID del usuario que crea la factura (opcional).

        Returns:
            Instancia creada de FACTURAS.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        if not numero_factura or not numero_factura.strip():
            raise ValueError("El número de factura es obligatorio")
        numero = numero_factura.strip().upper()

        if any(v is None or v < 0 for v in [subtotal, impuesto, total]):
            raise ValueError("Los valores de la factura no pueden ser negativos")

        pedido = self.db.get(PEDIDOS, id_pedido)
        if not pedido:
            raise ValueError("El pedido especificado no existe")
        existente = (
            self.db.query(FACTURAS).filter(FACTURAS.id_pedido == id_pedido).first()
        )
        if existente:
            raise ValueError("El pedido ya tiene una factura asociada")

        if self._numero_existe(numero):
            raise ValueError("El número de factura ya existe")

        if id_usuario_crea is None:
            id_usuario_crea = self._admin_fallback()

        obj = FACTURAS(
            id_pedido=id_pedido,
            numero_factura=numero,
            fecha_emision=fecha_emision or datetime.utcnow(),
            subtotal=subtotal,
            impuesto=impuesto,
            total=total,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def obtener_factura(self, factura_id: UUID) -> Optional[FACTURAS]:
        """
        Obtiene una factura por su UUID.

        Args:
            factura_id: UUID de la factura.

        Returns:
            Instancia de FACTURAS si existe, None en caso contrario.
        """
        return self.db.get(FACTURAS, factura_id)

    def obtener_facturas_por_pedido(
        self, id_pedido: UUID, skip: int = 0, limit: int = 100
    ) -> List[FACTURAS]:
        """
        Lista facturas filtradas por pedido con paginación.

        Args:
            id_pedido: UUID del pedido.
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de facturas del pedido indicado.
        """
        return (
            self.db.query(FACTURAS)
            .filter(FACTURAS.id_pedido == id_pedido)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def actualizar_factura(
        self, factura_id: UUID, id_usuario_edita: Optional[UUID] = None, **kwargs
    ) -> Optional[FACTURAS]:
        """
        Actualiza número y/o montos de la factura (valida unicidad y rangos).

        Args:
            factura_id: UUID de la factura.
            id_usuario_edita: UUID del usuario que edita (opcional).
            **kwargs: Campos a actualizar.

        Returns:
            Instancia actualizada de FACTURAS, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        obj = self.db.get(FACTURAS, factura_id)
        if not obj:
            return None

        if "numero_factura" in kwargs:
            numero = (kwargs["numero_factura"] or "").strip().upper()
            if not numero:
                raise ValueError("El número de factura es obligatorio")
            if self._numero_existe(numero, excluir_id=factura_id):
                raise ValueError("El número de factura ya existe")
            kwargs["numero_factura"] = numero

        for campo in ("subtotal", "impuesto", "total"):
            if campo in kwargs and kwargs[campo] is not None:
                if kwargs[campo] < 0:
                    raise ValueError(f"El campo {campo} no puede ser negativo")

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

    def eliminar_factura(self, factura_id: UUID) -> bool:
        """
        Elimina una factura por su UUID.

        Args:
            factura_id: UUID de la factura.

        Returns:
            True si se eliminó correctamente, False si no existe.
        """
        obj = self.db.get(FACTURAS, factura_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
