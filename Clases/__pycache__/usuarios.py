from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class USUARIOS(Base):
    __tablename__ = 'USUARIOS'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    sexo = Column(String(1), nullable=False)
    id_tipo_documento = Column(Integer, ForeignKey('TIPO_DOCUMENTO.id'))
    numero_documento = Column(String(20), unique=True, nullable=False)
    id_rol = Column(Integer, ForeignKey('ROLES.id'))
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    tipo_documento = relationship("TIPO_DOCUMENTO", back_populates="usuarios")
    rol = relationship("ROLES", back_populates="usuarios")
    direcciones = relationship("DIRECCIONES", back_populates="usuario")
    carritos = relationship("CARRITOS", back_populates="usuario")
    pedidos = relationship("PEDIDOS", back_populates="usuario")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea], remote_side=[id])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita], remote_side=[id])