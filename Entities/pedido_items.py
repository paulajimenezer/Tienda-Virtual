"""
Entidad Pedido Items
====================

Ítems que componen un pedido. Incluye validaciones y utilidades para
serialización.
"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from database.database import Base

# Asegurar import de func para server_default portables
from sqlalchemy.sql import func


class Pedido_items(Base):
    __tablename__ = "pedido_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pedido = Column(UUID(as_uuid=True), ForeignKey("pedidos.id"))
    id_producto = Column(UUID(as_uuid=True), ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    pedido = relationship("Pedidos", back_populates="pedido_item")
    producto = relationship("Productos", back_populates="pedido_item")
    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])


class PedidoItemModel(BaseModel):
    """Esquema Pydantic para items de pedido."""

    id_pedido: Optional[int] = Field(None, ge=1)
    id_producto: Optional[int] = Field(None, ge=1)
    cantidad: Optional[int] = Field(None, ge=1)
    precio_unitario: Optional[float] = Field(None, ge=0)
    descuento: Optional[float] = Field(None, ge=0)

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


class PedidoItemCreate(PedidoItemModel):
    """Esquema para crear item de pedido."""

    id_pedido: int = Field(..., ge=1)
    id_producto: int = Field(..., ge=1)
    cantidad: int = Field(..., ge=1)
    precio_unitario: float = Field(..., ge=0)
    descuento: Optional[float] = Field(None, ge=0)


class PedidoItemUpdate(BaseModel):
    """Esquema para actualizar item de pedido."""

    cantidad: Optional[int] = Field(None, ge=1)
    precio_unitario: Optional[float] = Field(None, ge=0)
    descuento: Optional[float] = Field(None, ge=0)


class PedidoItemResponse(PedidoItemModel):
    """Esquema de respuesta para item de pedido."""

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
