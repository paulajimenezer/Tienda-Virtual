"""
Entidad Usuario
===============

Modelo de Usuario con SQLAlchemy y esquemas de validación con Pydantic.
Este módulo adapta el estilo de documentación, validación y serialización
mostrado en Programacion-de-software/03-Introduccion-ORM/entities/usuario.py
al esquema de la entidad USUARIOS de este proyecto.
"""

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.sql import func
from database.database import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List


class Usuarios(Base):
    """Modelo de Usuario que representa la tabla 'USUARIOS'.

    Atributos:
            id: Identificador único del usuario
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            email: Correo electrónico único del usuario
            password: Hash/contraseña del usuario
            id_sexo: Relación al sexo del usuario
            id_tipo_documento: Relación al tipo de documento
            numero_documento: Número de documento único
            id_rol: Relación al rol del usuario
            activo: Estado del usuario (activo/inactivo)
            id_usuario_crea: Usuario que creó el registro
            id_usuario_edita: Último usuario que editó el registro
            fecha_creacion: Fecha de creación
            fecha_edicion: Fecha de última edición
    """

    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    id_sexo = Column(UUID(as_uuid=True), ForeignKey("sexo.id"))
    id_tipo_documento = Column(UUID(as_uuid=True), ForeignKey("tipo_documento.id"))
    numero_documento = Column(String(20), unique=True, nullable=False)
    id_rol = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    id_usuario_edita = Column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_edicion = Column(DateTime, nullable=True)

    sexo = relationship("Sexo")
    tipo_documento = relationship("Tipo_documento", back_populates="usuarios")
    rol = relationship("Roles", back_populates="usuarios")
    usuario_crea = relationship(
        "Usuarios", foreign_keys=[id_usuario_crea], remote_side=[id]
    )
    usuario_edita = relationship(
        "Usuarios", foreign_keys=[id_usuario_edita], remote_side=[id]
    )
    direccion = relationship("Direcciones", back_populates="usuario")
    carrito = relationship("Carritos", back_populates="usuario")
    pedido = relationship("Pedidos", back_populates="usuario")

    def __repr__(self) -> str:
        """Representación legible del objeto usuarios."""
        return (
            f"<usuarios(id={self.id}, nombre='{getattr(self, 'nombre', None)}', "
            f"apellido='{getattr(self, 'apellido', None)}', email='{getattr(self, 'email', None)}')>"
        )

    def to_dict(self) -> dict:
        """Convierte la instancia en un diccionario simple (solo columnas)."""
        return {
            "id": getattr(self, "id", None),
            "nombre": getattr(self, "nombre", None),
            "apellido": getattr(self, "apellido", None),
            "email": getattr(self, "email", None),
            "password": getattr(self, "password", None),
            "id_sexo": getattr(self, "id_sexo", None),
            "id_tipo_documento": getattr(self, "id_tipo_documento", None),
            "numero_documento": getattr(self, "numero_documento", None),
            "id_rol": getattr(self, "id_rol", None),
            "activo": getattr(self, "activo", None),
            "id_usuario_crea": getattr(self, "id_usuario_crea", None),
            "id_usuario_edita": getattr(self, "id_usuario_edita", None),
            "fecha_creacion": (
                self.fecha_creacion.isoformat()
                if getattr(self, "fecha_creacion", None)
                else None
            ),
            "fecha_edicion": (
                self.fecha_edicion.isoformat()
                if getattr(self, "fecha_edicion", None)
                else None
            ),
        }


class UsuarioBase(BaseModel):
    """Esquema base para Usuario (datos comunes)."""

    nombre: str = Field(
        ..., min_length=2, max_length=100, description="Nombre del usuario"
    )
    apellido: str = Field(
        ..., min_length=2, max_length=100, description="Apellido del usuario"
    )
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    id_sexo: int = Field(..., ge=1, description="ID del sexo del usuario")
    id_tipo_documento: int = Field(..., ge=1, description="ID del tipo de documento")
    numero_documento: str = Field(
        ..., min_length=3, max_length=20, description="Número de documento"
    )
    id_rol: int = Field(..., ge=1, description="ID del rol")
    activo: bool = Field(True, description="Estado del usuario")

    @validator("nombre", "apellido")
    def validar_nombre_apellido(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre/apellido no puede estar vacío")
        return v.strip().title()

    @validator("numero_documento")
    def validar_numero_documento(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El número de documento no puede estar vacío")

        permitidos = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- .")
        vn = v.upper()
        if not set(vn).issubset(permitidos):
            raise ValueError("Número de documento con caracteres inválidos")
        return vn


class UsuarioCreate(UsuarioBase):
    """Esquema para crear un nuevo usuario."""

    password: str = Field(
        ..., min_length=8, max_length=255, description="Contraseña del usuario"
    )
    id_usuario_crea: int = Field(
        ..., ge=1, description="ID del usuario que crea el registro"
    )

    @validator("password")
    def validar_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La contraseña no puede estar vacía")
        return v


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar un usuario existente (campos opcionales)."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    id_sexo: Optional[int] = Field(None, ge=1)
    id_tipo_documento: Optional[int] = Field(None, ge=1)
    numero_documento: Optional[str] = Field(None, min_length=3, max_length=20)
    id_rol: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None
    id_usuario_edita: Optional[int] = Field(None, ge=1)

    @validator("nombre", "apellido")
    def validar_nombre_apellido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("El nombre/apellido no puede estar vacío")
        return v.strip().title()

    @validator("numero_documento")
    def validar_numero_documento(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El número de documento no puede estar vacío")
        permitidos = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- .")
        vn = v.upper()
        if not set(vn).issubset(permitidos):
            raise ValueError("Número de documento con caracteres inválidos")
        return vn


if "UsuarioResponse" not in globals():
    from pydantic import BaseModel

    class UsuarioResponse(BaseModel):
        id: int

        class Config:
            from_attributes = True


if "UsuarioListResponse" not in globals():
    from typing import List
    from pydantic import BaseModel

    class UsuarioListResponse(BaseModel):
        items: List[UsuarioResponse]
        total: int
