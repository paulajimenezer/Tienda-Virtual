from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PRODUCTOS(Base):
    __tablename__ = 'PRODUCTOS'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    id_categoria = Column(Integer, ForeignKey('CATEGORIAS.id'))
    imagen_url = Column(String(255))
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    categoria = relationship("CATEGORIAS", back_populates="productos")
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    carrito_items = relationship("CARRITO_ITEMS", back_populates="producto")
    pedido_items = relationship("PEDIDO_ITEMS", back_populates="producto")