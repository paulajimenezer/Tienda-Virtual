"""
Entidad Tipo Documento
======================

Catálogo para estandarizar tipos de documento. Valida y normaliza cadenas.
"""

# Usar la Base compartida y func.now()
import uuid
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


class Tipo_documento(Base):
    __tablename__ = "tipo_documento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
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
    usuarios = relationship("Usuarios", back_populates="tipo_documento")


class TipoDocumentoModel(BaseModel):
    """Esquema Pydantic para tipos de documento."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=40)
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
        return v.upper()

    @validator("*", pre=True)
    def _normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class TipoDocumentoCreate(TipoDocumentoModel):
    """Esquema para crear tipo de documento."""

    nombre: str = Field(..., min_length=2, max_length=40)


class TipoDocumentoUpdate(BaseModel):
    """Esquema para actualizar tipo de documento."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=40)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = Field(None)

    @validator("nombre")
    def _nombre_ok(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v.upper()


class TipoDocumentoResponse(TipoDocumentoModel):
    """Esquema de respuesta para tipo de documento."""

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
