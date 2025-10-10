"""
Entidad Direcciones
===================

Direcciones de usuarios para envío/facturación. Valida campos de estructura
básica y normaliza strings.
"""

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Direcciones(Base):
    __tablename__ = "direcciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    direccion = Column(String(255), nullable=False)
    ciudad = Column(String(100), nullable=False)
    codigo_postal = Column(String(20))
    pais = Column(String(100), nullable=False)
    principal = Column(Boolean, default=False)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario = relationship(
        "Usuarios", back_populates="direccion", foreign_keys=[id_usuario]
    )
    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])
    pedido = relationship(
        "Pedidos", back_populates="direccion", foreign_keys="Pedidos.id_direccion"
    )


class DireccionModel(BaseModel):
    """Esquema Pydantic para direcciones de usuarios."""

    id_usuario: Optional[int] = Field(None, ge=1)
    linea1: Optional[str] = Field(
        None, min_length=3, max_length=120, description="Calle y número"
    )
    linea2: Optional[str] = Field(None, max_length=120)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=80)
    estado: Optional[str] = Field(None, min_length=2, max_length=80)
    pais: Optional[str] = Field(None, min_length=2, max_length=80)
    codigo_postal: Optional[str] = Field(None, min_length=2, max_length=20)
    principal: Optional[bool] = Field(False)

    class Config:
        extra = "allow"
        anystr_strip_whitespace = True
        validate_assignment = True

    @validator("linea1", "ciudad", "estado", "pais", "codigo_postal")
    def _no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El valor no puede estar vacío")
        return v

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class DireccionCreate(DireccionModel):
    """Esquema para crear dirección."""

    id_usuario: int = Field(..., ge=1)
    linea1: str = Field(..., min_length=3, max_length=120)
    ciudad: str = Field(..., min_length=2, max_length=80)
    pais: str = Field(..., min_length=2, max_length=80)


class DireccionUpdate(BaseModel):
    """Esquema para actualizar dirección."""

    linea1: Optional[str] = Field(None, min_length=3, max_length=120)
    linea2: Optional[str] = Field(None, max_length=120)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=80)
    estado: Optional[str] = Field(None, min_length=2, max_length=80)
    pais: Optional[str] = Field(None, min_length=2, max_length=80)
    codigo_postal: Optional[str] = Field(None, min_length=2, max_length=20)
    principal: Optional[bool] = Field(None)

    @validator("linea1", "ciudad", "pais")
    def _no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El valor no puede estar vacío")
        return v


class DireccionResponse(DireccionModel):
    """Esquema de respuesta de dirección."""

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
