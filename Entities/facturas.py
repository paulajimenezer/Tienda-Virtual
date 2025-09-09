"""
Entidad Facturas
================

Comprobantes generados a partir de pedidos. Incluye validación y utilidades
para serialización.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from database.database import Base

# Asegurar import de func para server_default portables
from sqlalchemy.sql import func


class FACTURAS(Base):
    __tablename__ = "FACTURAS"

    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey("PEDIDOS.id"))
    numero_factura = Column(String(100), unique=True, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    subtotal = Column(Float, nullable=False)
    impuestos = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey("USUARIOS.id"), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey("USUARIOS.id"), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    pedido = relationship("PEDIDOS", back_populates="factura")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])


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
