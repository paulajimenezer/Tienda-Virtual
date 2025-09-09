"""
Entidad Descuentos
==================

Reglas de descuento aplicables a carritos o productos. Incluye validaciones
básicas y utilidades de serialización.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    text,
)
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from database.database import Base
from sqlalchemy.sql import func


class DESCUENTOS(Base):
    __tablename__ = "DESCUENTOS"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    porcentaje = Column(Float, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey("USUARIOS.id"), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey("USUARIOS.id"), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    pedidos = relationship("PEDIDOS", back_populates="descuento")


class DescuentoModel(BaseModel):
    """Esquema Pydantic para descuentos.

    - porcentaje o valor fijo no negativos.
    - fecha vigencia opcional según el diseño actual.
    """

    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    porcentaje: Optional[float] = Field(None, ge=0, le=100)
    valor_fijo: Optional[float] = Field(None, ge=0)
    activo: Optional[bool] = Field(True)

    class Config:
        extra = "allow"
        anystr_strip_whitespace = True
        validate_assignment = True

    @validator("nombre")
    def _nombre_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v.title()

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


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


class DescuentoCreate(DescuentoModel):
    """Esquema para crear descuento."""

    nombre: str = Field(..., min_length=2, max_length=80)


class DescuentoUpdate(BaseModel):
    """Esquema para actualizar descuento."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)
    porcentaje: Optional[float] = Field(None, ge=0, le=100)
    valor_fijo: Optional[float] = Field(None, ge=0)
    activo: Optional[bool] = Field(None)

    @validator("nombre")
    def _nombre_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v.title()


class DescuentoResponse(DescuentoModel):
    """Esquema de respuesta para descuento."""

    id: int

    class Config:
        from_attributes = True
