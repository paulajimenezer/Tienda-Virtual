"""
Entidad Productos
=================

Catálogo de productos. Incluye validaciones de datos, normalización y
utilidades de serialización.
"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from database.config import Base
from sqlalchemy.sql import func
from uuid import UUID as UUID_t


class Productos(Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    id_categoria = Column(UUID(as_uuid=True), ForeignKey("categorias.id"))
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    categoria = relationship(
        "Categorias", back_populates="producto", foreign_keys=[id_categoria]
    )
    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])
    carrito_item = relationship("Carrito_items", back_populates="producto")
    pedido_items = relationship("Pedido_items", back_populates="producto")


class ProductoModel(BaseModel):
    """Esquema Pydantic para productos."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    id_categoria: Optional[int] = Field(None, ge=1)
    id_usuario_crea: Optional[int] = Field(None, ge=1)
    id_usuario_edita: Optional[int] = Field(None, ge=1)
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


class ProductoCreate(ProductoModel):
    """Esquema para crear producto."""

    nombre: str = Field(..., min_length=2, max_length=100)
    precio: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    id_categoria: int = Field(..., ge=1)
    id_usuario_crea: int = Field(..., ge=1)


class ProductoUpdate(BaseModel):
    """Esquema para actualizar producto."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    precio: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    id_categoria: Optional[int] = Field(None, ge=1)
    id_usuario_edita: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None

    @validator("nombre")
    def _nombre_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v.title()


class ProductoResponse(ProductoModel):
    """Esquema de respuesta de producto."""

    id: UUID_t

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
