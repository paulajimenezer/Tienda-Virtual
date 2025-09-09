from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FACTURAS(Base):
    __tablename__ = 'FACTURAS'
    
    id = Column(Integer, primary_key=True)
    id_pedido = Column(Integer, ForeignKey('PEDIDOS.id'))
    numero_factura = Column(String(100), unique=True, nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    subtotal = Column(Float, nullable=False)
    impuestos = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    pedido = relationship("PEDIDOS", back_populates="factura")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])