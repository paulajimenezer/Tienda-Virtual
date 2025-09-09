from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CARRITOS(Base):
    __tablename__ = 'CARRITOS'
    
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('USUARIOS.id'))
    fecha_creacion = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion_audit = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    usuario = relationship("USUARIOS", back_populates="carritos")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    carrito_items = relationship("CARRITO_ITEMS", back_populates="carrito")