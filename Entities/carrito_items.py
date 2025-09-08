from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CARRITO_ITEMS(Base):
    __tablename__ = 'CARRITO_ITEMS'
    
    id = Column(Integer, primary_key=True)
    id_carrito = Column(Integer, ForeignKey('CARRITOS.id'))
    id_producto = Column(Integer, ForeignKey('PRODUCTOS.id'))
    cantidad = Column(Integer, nullable=False, default=1)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    carrito = relationship("CARRITOS", back_populates="carrito_items")
    producto = relationship("PRODUCTOS", back_populates="carrito_items")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])