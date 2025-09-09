"""
Entidad Pedidos
===============

Pedidos realizados por los usuarios. Incluye validaciones y utilidades de
serialización.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from database.database import Base
from sqlalchemy.sql import func


class PEDIDOS(Base):
    __tablename__ = "PEDIDOS"

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("USUARIOS.id"))
    id_direccion = Column(Integer, ForeignKey("DIRECCIONES.id"))
    id_descuento = Column(Integer, ForeignKey("DESCUENTOS.id"), nullable=True)
    fecha_pedido = Column(DateTime, nullable=False)
    estado = Column(String(50), nullable=False)
    total = Column(Float, nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey("USUARIOS.id"), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey("USUARIOS.id"), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario = relationship("USUARIOS", back_populates="pedidos")
    direccion = relationship("DIRECCIONES", back_populates="pedidos")
    descuento = relationship("DESCUENTOS", back_populates="pedidos")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    pedido_items = relationship("PEDIDO_ITEMS", back_populates="pedido")
    factura = relationship("FACTURAS", back_populates="pedido", uselist=False)


class PedidoModel(BaseModel):
    """Esquema Pydantic para pedidos."""

    id_usuario: Optional[int] = Field(None, ge=1)
    id_carrito: Optional[int] = Field(None, ge=1)
    estado: Optional[str] = Field(None, max_length=30)
    fecha: Optional[datetime] = None
    total: Optional[float] = Field(None, ge=0)

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


class PedidoCreate(PedidoModel):
    """Esquema para crear pedido."""

    id_usuario: int = Field(..., ge=1)
    id_carrito: int = Field(..., ge=1)
    total: float = Field(..., ge=0)


class PedidoUpdate(BaseModel):
    """Esquema para actualizar pedido."""

    estado: Optional[str] = Field(None, max_length=30)
    total: Optional[float] = Field(None, ge=0)

    @validator("estado")
    def _estado_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El estado no puede estar vacío")
        return v


class PedidoResponse(PedidoModel):
    """Esquema de respuesta para pedido."""

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
