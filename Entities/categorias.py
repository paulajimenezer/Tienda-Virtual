"""
Entidad Categorías
==================

Clasificación de productos. Valida nombres y descripciones y provee utilidades
para serialización y depuración.
"""

import uuid
from typing import Any, Optional
from uuid import UUID as UUID_t

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Categorias(Base):
    __tablename__ = "categorias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
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
    producto = relationship(
        "Productos", back_populates="categoria", foreign_keys="Productos.id_categoria"
    )


class CategoriaModel(BaseModel):
    """Esquema Pydantic para categorías."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)

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


class CategoriaCreate(CategoriaModel):
    """Esquema para crear una categoría."""

    nombre: str = Field(..., min_length=2, max_length=80)


class CategoriaUpdate(BaseModel):
    """Esquema para actualizar una categoría."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=80)
    descripcion: Optional[str] = Field(None, max_length=255)

    @validator("nombre")
    def _nombre_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v.title()


class CategoriaResponse(CategoriaModel):
    """Esquema de respuesta para categoría."""

    id: UUID_t  # antes: int

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
