"""CRUD para la entidad Carritos.

Permite:
- Obtener carrito por ID.
- Obtener o crear el carrito activo de un usuario.
- Listar carritos de un usuario.
- Cerrar (desactivar) un carrito.
- Actualizar campos permitidos del carrito.

Todas las operaciones validan la existencia y estado del carrito.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from Entities.carritos import Carritos as CARRITOS


class CarritoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_carrito(self, carrito_id: UUID) -> Optional[CARRITOS]:
        """Obtiene un carrito por su ID."""
        return self.db.get(CARRITOS, carrito_id)

    def get_carrito_activo_usuario(self, id_usuario: UUID) -> Optional[CARRITOS]:
        """Obtiene el carrito activo (activo=True) del usuario, si existe."""
        return (
            self.db.query(CARRITOS)
            .filter(and_(CARRITOS.id_usuario == id_usuario, CARRITOS.activo == True))
            .first()
        )

    def get_or_create_carrito_activo(
        self, id_usuario: UUID, id_usuario_crea: Optional[UUID] = None
    ) -> CARRITOS:
        """
        Obtiene el carrito activo del usuario o lo crea si no existe.

        Args:
            id_usuario: UUID del usuario.
            id_usuario_crea: UUID del usuario que crea el carrito (opcional).

        Returns:
            Instancia de Carritos.
        """
        existente = self.get_carrito_activo_usuario(id_usuario)
        if existente:
            return existente
        obj = CARRITOS(
            id_usuario=id_usuario,
            activo=True,
            id_usuario_crea=id_usuario_crea or id_usuario,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_carritos_usuario(
        self, id_usuario: UUID, skip: int = 0, limit: int = 100
    ) -> List[CARRITOS]:
        """Lista los carritos de un usuario con paginación."""
        return (
            self.db.query(CARRITOS)
            .filter(CARRITOS.id_usuario == id_usuario)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def cerrar_carrito(
        self, carrito_id: UUID, id_usuario_edita: Optional[UUID] = None
    ) -> Optional[CARRITOS]:
        """
        Desactiva (cierra) el carrito. No elimina ítems.

        Args:
            carrito_id: UUID del carrito.
            id_usuario_edita: UUID del usuario que edita (opcional).

        Returns:
            Instancia de Carritos actualizada o None si no existe.
        """
        obj = self.db.get(CARRITOS, carrito_id)
        if not obj:
            return None
        obj.activo = False
        if hasattr(obj, "id_usuario_edita") and id_usuario_edita:
            obj.id_usuario_edita = id_usuario_edita
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_carrito(
        self,
        carrito_id: UUID,
        *,
        activo: Optional[bool] = None,
        id_usuario_edita: Optional[UUID] = None,
    ) -> Optional[CARRITOS]:
        """
        Actualiza campos permitidos del carrito (actualmente solo 'activo').

        Args:
            carrito_id: UUID del carrito.
            activo: Nuevo estado activo/inactivo (opcional).
            id_usuario_edita: UUID del usuario que edita (opcional).

        Returns:
            Instancia de Carritos actualizada o None si no existe.
        """
        obj = self.db.get(CARRITOS, carrito_id)
        if not obj:
            return None
        if activo is not None:
            obj.activo = bool(activo)
        if hasattr(obj, "id_usuario_edita") and id_usuario_edita:
            obj.id_usuario_edita = id_usuario_edita
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def obtener_carritos(self, skip: int = 0, limit: int = 100) -> List[CARRITOS]:
        """Lista todos los carritos con paginación."""
        return (
            self.db.query(CARRITOS)
            .order_by(CARRITOS.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # alias semántico para mantener compatibilidad con APIs que llaman 'obtener_carrito'
    def obtener_carrito(self, carrito_id: UUID) -> Optional[CARRITOS]:
        return self.get_carrito(carrito_id)

    def eliminar_carrito(self, carrito_id: UUID) -> bool:
        """Elimina o desactiva un carrito por su ID."""
        obj = self.db.get(CARRITOS, carrito_id)
        if not obj:
            return False
        if hasattr(obj, "activo"):
            obj.activo = False
            self.db.commit()
            self.db.refresh(obj)
            return True
        self.db.delete(obj)
        self.db.commit()
        return True
