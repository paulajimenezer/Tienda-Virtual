"""
Modelos Pydantic para las respuestas de la API
"""

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    numero_documento: str
    id_rol: UUID
    id_tipo_documento: UUID
    id_sexo: Optional[UUID] = None
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str
    # id_usuario_crea es opcional si el modelo lo soporta
    id_usuario_crea: Optional[UUID] = None


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    numero_documento: Optional[str] = None
    id_rol: Optional[UUID] = None
    id_tipo_documento: Optional[UUID] = None
    id_sexo: Optional[UUID] = None
    activo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class CambioContraseña(BaseModel):
    contraseña_actual: str
    nueva_contraseña: str


class loginResponse(BaseModel):
    clave: str
    nombre_usuario: UsuarioResponse


class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    id: UUID
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductoBase(BaseModel):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria_id: UUID
    usuario_id: UUID


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None


class ProductoResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    id_categoria: UUID
    activo: bool = True
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductoConCategoria(ProductoResponse):
    categoria: CategoriaResponse


class UsuarioConProductos(UsuarioResponse):
    productos: list[ProductoResponse] = []


class CategoriaConProductos(CategoriaResponse):
    productos: list[ProductoResponse] = []


class RespuestaAPI(BaseModel):
    mensaje: str
    exito: bool = True
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    mensaje: str
    exito: bool = False
    error: str
    codigo: int


class CarritoResponse(BaseModel):
    id: UUID
    id_usuario: UUID
    activo: bool
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarritoItemResponse(BaseModel):
    id: UUID
    id_carrito: UUID
    id_producto: UUID
    cantidad: int
    # precio_unitario may be absent in some DB designs; keep optional to avoid response validation errors
    precio_unitario: Optional[float] = None

    class Config:
        from_attributes = True


class CarritoEnriquecido(CarritoResponse):
    usuario: Optional[UsuarioResponse] = None
    items: List[CarritoItemResponse] = []


class PedidoItemResponse(BaseModel):
    id: UUID
    id_pedido: UUID
    id_producto: UUID
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True


class DireccionResponse(BaseModel):
    id: UUID
    id_usuario: UUID
    direccion: str
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None

    class Config:
        from_attributes = True


class PedidoEnriquecido(BaseModel):
    # Campos base del pedido
    id: UUID
    id_usuario: UUID
    id_direccion: UUID
    fecha_pedido: datetime
    estado: str
    total: float

    usuario: Optional[UsuarioResponse] = None
    items: List[PedidoItemResponse] = []
    direccion: Optional[DireccionResponse] = None

    class Config:
        from_attributes = True


class FacturaEnriquecida(BaseModel):
    id: UUID
    id_pedido: UUID
    numero_factura: str
    fecha_emision: datetime
    subtotal: float
    impuesto: float
    total: float

    pedido: Optional[PedidoEnriquecido] = None
    usuario: Optional[UsuarioResponse] = None

    class Config:
        from_attributes = True
