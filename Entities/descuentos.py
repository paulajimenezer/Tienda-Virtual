from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DESCUENTOS(Base):
    __tablename__ = 'DESCUENTOS'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    porcentaje = Column(Float, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    pedidos = relationship("PEDIDOS", back_populates="descuento")