from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PEDIDO_ITEMS(Base):
    __tablename__ = 'PEDIDO_ITEMS'
    
    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('PEDIDOS.id'))
    id_producto = Column(Integer, ForeignKey('PRODUCTOS.id'))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    pedido = relationship("PEDIDOS", back_populates="pedido_items")
    producto = relationship("PRODUCTOS", back_populates="pedido_items")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
