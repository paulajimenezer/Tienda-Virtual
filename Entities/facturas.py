"""
Entidad Facturas
================

Comprobantes generados a partir de pedidos. Incluye validación y utilidades
para serialización.
"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from database.config import Base


from sqlalchemy.sql import func


class Facturas(Base):
    __tablename__ = "facturas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pedido = Column(UUID(as_uuid=True), ForeignKey("pedidos.id"))
    numero_factura = Column(String(100), unique=True, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    subtotal = Column(Float, nullable=False)
    impuesto = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    pedido = relationship("Pedidos", back_populates="factura")
    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])


class FacturaModel(BaseModel):
    """Esquema Pydantic para facturas."""

    id_pedido: Optional[int] = Field(None, ge=1)
    numero: Optional[str] = Field(None, min_length=3, max_length=40)
    fecha_emision: Optional[datetime] = None
    total: Optional[float] = Field(None, ge=0)

    class Config:
        extra = "allow"
        anystr_strip_whitespace = True
        validate_assignment = True

    @validator("numero")
    def _num_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El número de factura no puede estar vacío")
        return v.upper()

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class FacturaCreate(FacturaModel):
    """Esquema para crear factura."""

    id_pedido: int = Field(..., ge=1)
    numero: str = Field(..., min_length=3, max_length=40)
    total: float = Field(..., ge=0)


class FacturaUpdate(BaseModel):
    """Esquema para actualizar factura."""

    numero: Optional[str] = Field(None, min_length=3, max_length=40)
    total: Optional[float] = Field(None, ge=0)

    @validator("numero")
    def _num_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El número de factura no puede estar vacío")
        return v.upper()


class FacturaResponse(FacturaModel):
    """Esquema de respuesta para factura."""

    id: int

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
