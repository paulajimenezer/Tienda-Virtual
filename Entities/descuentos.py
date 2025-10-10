"""
Entidad Descuentos
==================

Reglas de descuento aplicables a carritos o productos. Incluye validaciones
básicas y utilidades de serialización.
"""

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID as UUID_t

from pydantic import BaseModel, Field, computed_field, field_validator, validator
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Descuentos(Base):
    __tablename__ = "descuentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), unique=True, nullable=False)
    porcentaje = Column(Float, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])
    pedido = relationship(
        "Pedidos", back_populates="descuento", foreign_keys="Pedidos.id_descuento"
    )


class DescuentoModel(BaseModel):
    """Esquema Pydantic para descuentos.

    Alineado con la tabla: codigo, porcentaje, fechas y activo.
    """

    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    porcentaje: Optional[float] = Field(None, ge=0, le=100)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = Field(True)

    class Config:
        extra = "allow"
        str_strip_whitespace = True  # reemplaza anystr_strip_whitespace
        validate_assignment = True

    @validator("codigo")
    def _codigo_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El código no puede estar vacío")
        return v.upper()

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


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


class DescuentoCreate(DescuentoModel):
    """Esquema para crear descuento."""

    codigo: str = Field(..., min_length=1, max_length=50)
    porcentaje: float = Field(..., ge=0, le=100)
    fecha_inicio: datetime = Field(...)
    fecha_fin: datetime = Field(...)
    activo: Optional[bool] = Field(True)


class DescuentoUpdate(BaseModel):
    """Esquema para actualizar descuento."""

    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    porcentaje: Optional[float] = Field(None, ge=0, le=100)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    activo: Optional[bool] = Field(None)

    @validator("codigo")
    def _codigo_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El código no puede estar vacío")
        return v.upper()


class DescuentoResponse(DescuentoModel):
    """Esquema de respuesta para descuento."""

    id: UUID_t  # antes: int
    # Cambiar a lista de UUID y mapear desde la relación 'pedido'
    pedidos: list[UUID_t] = Field(
        default_factory=list, validation_alias="pedido", alias="pedidos"
    )

    # Campo calculado: indica si el descuento es válido "hoy" (UTC)
    @computed_field
    @property
    def vigente(self) -> bool:
        try:
            now = datetime.utcnow()
            if not bool(self.activo):
                return False
            if self.fecha_inicio is None or self.fecha_fin is None:
                return False
            ini = (
                self.fecha_inicio.date()
                if isinstance(self.fecha_inicio, datetime)
                else self.fecha_inicio
            )
            fin = (
                self.fecha_fin.date()
                if isinstance(self.fecha_fin, datetime)
                else self.fecha_fin
            )
            ref = now.date()
            return ini <= ref <= fin
        except Exception:
            return False

    # Convertir objetos PEDIDOS a sus UUIDs
    @field_validator("pedidos", mode="before")
    @classmethod
    def _coerce_pedidos(cls, v):
        if v is None:
            return []
        try:
            return [getattr(it, "id", it) for it in v]
        except TypeError:
            return v

    class Config:
        from_attributes = True
        extra = "forbid"  # no permitir campos extra en la respuesta
