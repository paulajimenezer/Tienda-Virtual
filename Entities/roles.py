"""
Entidad Roles
=============

Roles de usuario para control y estandarización. Valida nombre y
normaliza cadenas. Provee utilidades de serialización.
"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from database.database import Base


class Roles(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255))
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    usuario_crea = relationship("Usuarios", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("Usuarios", foreign_keys=[id_usuario_edita])
    usuarios = relationship("Usuarios", back_populates="rol")


class RolModel(BaseModel):
    """Esquema Pydantic para roles de usuario."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=60)
    descripcion: Optional[str] = Field(None, max_length=255)
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


class RolCreate(RolModel):
    """Esquema para crear un rol."""

    id_usuario_crea: int = Field(..., ge=1, description="Usuario que crea el rol")


class RolUpdate(BaseModel):
    """Esquema para actualizar un rol."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=60)
    descripcion: Optional[str] = Field(None, max_length=255)
    id_usuario_edita: Optional[int] = Field(None, ge=1)

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


class RolResponse(RolModel):
    """Esquema de respuesta para rol."""

    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_edicion: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


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
