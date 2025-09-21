"""
Paquete CRUD para Tienda-Virtual.

"""

from .catalogo import categoria_crud, producto_crud
from .estandarizacion import roles_crud, sexo_crud, tipo_documento_crud
from .usuarios import usuario_crud, direcciones_crud
from .compras import carritos_crud, carrito_items_crud, descuentos_crud
from .pedidos import pedidos_crud, pedido_items_crud, facturas_crud

__all__ = [
    "categoria_crud",
    "producto_crud",
    "roles_crud",
    "sexo_crud",
    "tipo_documento_crud",
    "usuario_crud",
    "direcciones_crud",
    "carritos_crud",
    "carrito_items_crud",
    "descuentos_crud",
    "pedidos_crud",
    "pedido_items_crud",
    "facturas_crud",
]
