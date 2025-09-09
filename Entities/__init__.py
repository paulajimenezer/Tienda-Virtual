"""
Módulo de entidades
===================

Este paquete agrupa todas las entidades (SQLAlchemy) y sus esquemas Pydantic
para validación y serialización.
"""

# Usuarios
from .usuarios import (
    USUARIOS,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
)

# Catálogo comercial
from .categorias import CATEGORIAS, CategoriaCreate, CategoriaUpdate, CategoriaResponse
from .productos import PRODUCTOS, ProductoCreate, ProductoUpdate, ProductoResponse

# Estandarización de datos
from .roles import ROLES, RolCreate, RolUpdate, RolResponse
from .sexo import SEXO, SexoCreate, SexoUpdate, SexoResponse
from .tipo_documento import (
    TIPO_DOCUMENTO,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
    TipoDocumentoResponse,
)

# Recursos de usuario
from .direcciones import (
    DIRECCIONES,
    DireccionCreate,
    DireccionUpdate,
    DireccionResponse,
)

# Compras
from .carritos import CARRITOS, CarritoCreate, CarritoUpdate, CarritoResponse
from .carrito_items import (
    CARRITO_ITEMS,
    CarritoItemCreate,
    CarritoItemUpdate,
    CarritoItemResponse,
)
from .descuentos import DESCUENTOS, DescuentoCreate, DescuentoUpdate, DescuentoResponse

# Pedidos
from .pedidos import PEDIDOS, PedidoCreate, PedidoUpdate, PedidoResponse
from .pedido_items import (
    PEDIDO_ITEMS,
    PedidoItemCreate,
    PedidoItemUpdate,
    PedidoItemResponse,
)
from .facturas import FACTURAS, FacturaCreate, FacturaUpdate, FacturaResponse

__all__ = [
    # Usuarios
    "USUARIOS",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioListResponse",
    # Catálogo comercial
    "CATEGORIAS",
    "CategoriaCreate",
    "CategoriaUpdate",
    "CategoriaResponse",
    "PRODUCTOS",
    "ProductoCreate",
    "ProductoUpdate",
    "ProductoResponse",
    # Estandarización de datos
    "ROLES",
    "RolCreate",
    "RolUpdate",
    "RolResponse",
    "SEXO",
    "SexoCreate",
    "SexoUpdate",
    "SexoResponse",
    "TIPO_DOCUMENTO",
    "TipoDocumentoCreate",
    "TipoDocumentoUpdate",
    "TipoDocumentoResponse",
    # Recursos de usuario
    "DIRECCIONES",
    "DireccionCreate",
    "DireccionUpdate",
    "DireccionResponse",
    # Compras
    "CARRITOS",
    "CarritoCreate",
    "CarritoUpdate",
    "CarritoResponse",
    "CARRITO_ITEMS",
    "CarritoItemCreate",
    "CarritoItemUpdate",
    "CarritoItemResponse",
    "DESCUENTOS",
    "DescuentoCreate",
    "DescuentoUpdate",
    "DescuentoResponse",
    # Pedidos
    "PEDIDOS",
    "PedidoCreate",
    "PedidoUpdate",
    "PedidoResponse",
    "PEDIDO_ITEMS",
    "PedidoItemCreate",
    "PedidoItemUpdate",
    "PedidoItemResponse",
    "FACTURAS",
    "FacturaCreate",
    "FacturaUpdate",
    "FacturaResponse",
]
