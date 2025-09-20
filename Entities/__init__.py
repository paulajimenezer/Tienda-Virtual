"""
Módulo de entidades
===================

Este paquete agrupa todas las entidades (SQLAlchemy) y sus esquemas Pydantic
para validación y serialización.
"""

# Usuarios
from .usuarios import (
    Usuarios,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
)

# Catálogo comercial
from .categorias import Categorias, CategoriaCreate, CategoriaUpdate, CategoriaResponse
from .productos import Productos, ProductoCreate, ProductoUpdate, ProductoResponse

# Estandarización de datos
from .roles import Roles, RolCreate, RolUpdate, RolResponse
from .sexo import Sexo, SexoCreate, SexoUpdate, SexoResponse
from .tipo_documento import (
    Tipo_documento,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
    TipoDocumentoResponse,
)

# Recursos de usuario
from .direcciones import (
    Direcciones,
    DireccionCreate,
    DireccionUpdate,
    DireccionResponse,
)

# Compras
from .carritos import Carritos, CarritoCreate, CarritoUpdate, CarritoResponse
from .carrito_items import (
    Carrito_items,
    CarritoItemCreate,
    CarritoItemUpdate,
    CarritoItemResponse,
)
from .descuentos import Descuentos, DescuentoCreate, DescuentoUpdate, DescuentoResponse

# Pedidos
from .pedidos import Pedidos, PedidoCreate, PedidoUpdate, PedidoResponse
from .pedido_items import (
    Pedido_items,
    PedidoItemCreate,
    PedidoItemUpdate,
    PedidoItemResponse,
)
from .facturas import Facturas, FacturaCreate, FacturaUpdate, FacturaResponse

__all__ = [
    # Usuarios
    "Usuarios",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioListResponse",
    # Catálogo comercial
    "Categorias",
    "CategoriaCreate",
    "CategoriaUpdate",
    "CategoriaResponse",
    "Productos",
    "ProductoCreate",
    "ProductoUpdate",
    "ProductoResponse",
    # Estandarización de datos
    "Roles",
    "RolCreate",
    "RolUpdate",
    "RolResponse",
    "Sexo",
    "SexoCreate",
    "SexoUpdate",
    "SexoResponse",
    "Tipo_documento",
    "TipoDocumentoCreate",
    "TipoDocumentoUpdate",
    "TipoDocumentoResponse",
    # Recursos de usuario
    "Direcciones",
    "DireccionCreate",
    "DireccionUpdate",
    "DireccionResponse",
    # Compras
    "Carritos",
    "CarritoCreate",
    "CarritoUpdate",
    "CarritoResponse",
    "Carrito_items",
    "CarritoItemCreate",
    "CarritoItemUpdate",
    "CarritoItemResponse",
    "Descuentos",
    "DescuentoCreate",
    "DescuentoUpdate",
    "DescuentoResponse",
    # Pedidos
    "Pedidos",
    "PedidoCreate",
    "PedidoUpdate",
    "PedidoResponse",
    "Pedido_items",
    "PedidoItemCreate",
    "PedidoItemUpdate",
    "PedidoItemResponse",
    "Facturas",
    "FacturaCreate",
    "FacturaUpdate",
    "FacturaResponse",
]
