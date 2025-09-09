"""
Paquete CRUD para Tienda-Virtual.

"""

# Importaciones explícitas de submódulos (reemplaza los imports con comodín)
from .catalogo import categoria_crud, producto_crud
from .estandarizacion import roles_crud, sexo_crud, tipo_documento_crud
from .usuarios import usuario_crud, direcciones_crud
from .compras import carritos_crud, carrito_items_crud, descuentos_crud
from .pedidos import pedidos_crud, pedido_items_crud, facturas_crud

__all__ = [
    # catálogo comercial
    "categoria_crud",
    "producto_crud",
    # estandarización de datos
    "roles_crud",
    "sexo_crud",
    "tipo_documento_crud",
    # usuarios
    "usuario_crud",
    "direcciones_crud",
    # compras
    "carritos_crud",
    "carrito_items_crud",
    "descuentos_crud",
    # pedidos
    "pedidos_crud",
    "pedido_items_crud",
    "facturas_crud",
]
