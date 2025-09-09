from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PEDIDOS(Base):
    __tablename__ = 'PEDIDOS'
    
    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('USUARIOS.id'))
    id_direccion = Column(Integer, ForeignKey('DIRECCIONES.id'))
    id_descuento = Column(Integer, ForeignKey('DESCUENTOS.id'), nullable=True)
    fecha_pedido = Column(DateTime, nullable=False)
    estado = Column(String(50), nullable=False)
    total = Column(Float, nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    usuario = relationship("USUARIOS", back_populates="pedidos")
    direccion = relationship("DIRECCIONES", back_populates="pedidos")
    descuento = relationship("DESCUENTOS", back_populates="pedidos")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    pedido_items = relationship("PEDIDO_ITEMS", back_populates="pedido")
    factura = relationship("FACTURAS", back_populates="pedido", uselist=False)