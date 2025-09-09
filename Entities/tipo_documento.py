from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TIPO_DOCUMENTO(Base):
    __tablename__ = 'TIPO_DOCUMENTO'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    id_usuario_crea = Column(Integer, ForeignKey('USUARIOS.id'), nullable=False)
    id_usuario_edita = Column(Integer, ForeignKey('USUARIOS.id'), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False, server_default=text('NOW()'))
    fecha_edicion = Column(DateTime, nullable=True)
    
    usuario_crea = relationship("USUARIOS", foreign_keys=[id_usuario_crea])
    usuario_edita = relationship("USUARIOS", foreign_keys=[id_usuario_edita])
    usuarios = relationship("USUARIOS", back_populates="tipo_documento")
