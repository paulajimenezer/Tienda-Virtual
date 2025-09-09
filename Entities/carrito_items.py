"""
Entidad Carrito Items
=====================

Items contenidos en un carrito. Incluye validaciones de cantidad y precio
mediante Pydantic, y utilidades de serialización/depuración.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from database.database import Base

# Asegurar import de func para server_default portables
from sqlalchemy.sql import func


class CARRITO_ITEMS(Base):
    __tablename__ = "CARRITO_ITEMS"

    id = Column(Integer, primary_key=True)
    id_carrito = Column(Integer, ForeignKey("CARRITOS.id"))
    id_producto = Column(Integer, ForeignKey("PRODUCTOS.id"))
    cantidad = Column(Integer, nullable=False, default=1)
    id_usuario_crea = Column(Integer, ForeignKey("USUARIOS.id"), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey("USUARIOS.id"), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    carrito = relationship("CARRITOS", back_populates="carrito_items")
    producto = relationship("PRODUCTOS", back_populates="carrito_items")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])


class CarritoItemModel(BaseModel):
    """Esquema Pydantic para validar items del carrito.

    Campos opcionales para no romper código existente. Normaliza strings y
    valida que cantidad y precio sean valores positivos si se proporcionan.
    """

    id_carrito: Optional[int] = Field(None, ge=1)
    id_producto: Optional[int] = Field(None, ge=1)
    cantidad: Optional[int] = Field(None, ge=1, description="Cantidad del producto")
    precio_unitario: Optional[float] = Field(None, ge=0, description="Precio unitario")

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


class CarritoItemCreate(CarritoItemModel):
    """Esquema para crear un ítem del carrito."""

    id_carrito: int = Field(..., ge=1)
    id_producto: int = Field(..., ge=1)
    cantidad: int = Field(..., ge=1)
    precio_unitario: float = Field(..., ge=0)


class CarritoItemUpdate(BaseModel):
    """Esquema para actualizar un ítem del carrito."""

    cantidad: Optional[int] = Field(None, ge=1)
    precio_unitario: Optional[float] = Field(None, ge=0)


class CarritoItemResponse(CarritoItemModel):
    """Esquema de respuesta para ítem del carrito."""

    id: int

    class Config:
        from_attributes = True


# Utilidades: __repr__ y to_dict para todos los modelos ORM
try:
    from sqlalchemy.inspection import inspect as _sa_inspect
except Exception:  # pragma: no cover
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
