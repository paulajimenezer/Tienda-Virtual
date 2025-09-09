"""
Entidad Carritos
================

Carrito de compras de un usuario. Incluye validaciones básicas y utilidades
para serialización.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from database.database import Base
from sqlalchemy.sql import func


class CARRITOS(Base):
    __tablename__ = "CARRITOS"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("USUARIOS.id"))
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey("USUARIOS.id"), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey("USUARIOS.id"), nullable=True)
    fecha_creacion_audit = Column(
        DateTime, nullable=False, server_default=text("NOW()")
    )
    fecha_edicion = Column(DateTime, nullable=True)

    usuario = relationship("USUARIOS", back_populates="carritos")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    carrito_items = relationship("CARRITO_ITEMS", back_populates="carrito")


class CarritoModel(BaseModel):
    """Esquema Pydantic para carritos.

    - id_usuario requerido al crear (en Create), opcional aquí para flexibilidad.
    - Normaliza strings.
    """

    id_usuario: Optional[int] = Field(None, ge=1)
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

    id_usuario: int = Field(..., ge=1)


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

    id: int

    class Config:
        from_attributes = True


try:
    from sqlalchemy.inspection import inspect as _sa_inspect
except Exception:
    _sa_inspect = None  # type: ignore


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
    Base  # type: ignore[name-defined]
    if not hasattr(Base, "to_dict"):
        setattr(Base, "to_dict", _to_dict_default)  # type: ignore[attr-defined]
    if not hasattr(Base, "__repr__"):
        setattr(Base, "__repr__", _repr_default)  # type: ignore[attr-defined]
except Exception:
    pass
