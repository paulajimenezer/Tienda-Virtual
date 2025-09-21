"""
Módulo de entidades
===================

Este paquete agrupa todas las entidades (SQLAlchemy) y sus esquemas Pydantic
para validación y serialización.
"""

from .usuarios import (
    Usuarios,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioListResponse,
)


from .categorias import Categorias, CategoriaCreate, CategoriaUpdate, CategoriaResponse
from .productos import Productos, ProductoCreate, ProductoUpdate, ProductoResponse


from .roles import Roles, RolCreate, RolUpdate, RolResponse
from .sexo import Sexo, SexoCreate, SexoUpdate, SexoResponse
from .tipo_documento import (
    Tipo_documento,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
    TipoDocumentoResponse,
)


from .direcciones import (
    Direcciones,
    DireccionCreate,
    DireccionUpdate,
    DireccionResponse,
)


from .carritos import Carritos, CarritoCreate, CarritoUpdate, CarritoResponse
from .carrito_items import (
    Carrito_items,
    CarritoItemCreate,
    CarritoItemUpdate,
    CarritoItemResponse,
)
from .descuentos import Descuentos, DescuentoCreate, DescuentoUpdate, DescuentoResponse


from .pedidos import Pedidos, PedidoCreate, PedidoUpdate, PedidoResponse
from .pedido_items import (
    Pedido_items,
    PedidoItemCreate,
    PedidoItemUpdate,
    PedidoItemResponse,
)
from .facturas import Facturas, FacturaCreate, FacturaUpdate, FacturaResponse

__all__ = [
    "Usuarios",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "UsuarioListResponse",
    "Categorias",
    "CategoriaCreate",
    "CategoriaUpdate",
    "CategoriaResponse",
    "Productos",
    "ProductoCreate",
    "ProductoUpdate",
    "ProductoResponse",
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
    "Direcciones",
    "DireccionCreate",
    "DireccionUpdate",
    "DireccionResponse",
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
