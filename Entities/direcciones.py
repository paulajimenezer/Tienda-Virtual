from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DIRECCIONES(Base):
    __tablename__ = 'DIRECCIONES'
    
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('USUARIOS.id'))
    direccion = Column(String(255), nullable=False)
    ciudad = Column(String(100), nullable=False)
    codigo_postal = Column(String(20))
    pais = Column(String(100), nullable=False)
    principal = Column(Boolean, default=False)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    usuario = relationship("USUARIOS", back_populates="direcciones")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    pedidos = relationship("PEDIDOS", back_populates="direccion")