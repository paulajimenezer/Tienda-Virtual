"""
Entidad Carritos
================

Carrito de compras de un usuario. Incluye validaciones básicas y utilidades
para serialización.
"""

import uuid
from typing import Any, Optional
from uuid import UUID as UUID_t

from pydantic import BaseModel, Field, validator
from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Carritos(Base):
    __tablename__ = "carritos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario = relationship(
        "Usuarios", back_populates="carrito", foreign_keys=[id_usuario]
    )
    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])
    carrito_item = relationship("Carrito_items", back_populates="carrito")


class CarritoModel(BaseModel):
    """Esquema Pydantic para carritos.

    - id_usuario requerido al crear (en Create), opcional aquí para flexibilidad.
    - Normaliza strings.
    """

    id_usuario: Optional[UUID_t] = Field(None)  # <-- antes int
    estado: Optional[str] = Field(
        None, max_length=30, description="estado del carrito, p.ej. activo, cerrado"
    )

    class Config:
        extra = "allow"
        anystr_strip_whitespace = True
        validate_assignment = True

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class CarritoCreate(CarritoModel):
    """Esquema para crear carrito."""

    id_usuario: UUID_t = Field(...)


class CarritoUpdate(BaseModel):
    """Esquema para actualizar carrito."""

    estado: Optional[str] = Field(None, max_length=30)

    @validator("estado")
    def _estado_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El estado no puede estar vacío")
        return v


class CarritoResponse(CarritoModel):
    """Esquema de respuesta para carrito."""

    id: UUID_t  # <-- antes int

    class Config:
        from_attributes = True


try:
    from sqlalchemy.inspection import inspect as _sa_inspect
except Exception:
    _sa_inspect = None


def _to_dict_default(self) -> dict[str, Any]:
    try:
        if _sa_inspect is not None:
            try:
                return {
                    c.key: getattr(self, c.key)
                    for c in _sa_inspect(self).mapper.column_attrs
                }
            except Exception:
                pass
        return {
            k: v
            for k, v in getattr(self, "__dict__", {}).items()
            if not str(k).startswith("_")
        }
    except Exception:
        return {}


def _repr_default(self) -> str:
    return f"{self.__class__.__name__}({_to_dict_default(self)})"


try:
    Base
    if not hasattr(Base, "to_dict"):
        setattr(Base, "to_dict", _to_dict_default)
    if not hasattr(Base, "__repr__"):
        setattr(Base, "__repr__", _repr_default)
except Exception:
    pass
