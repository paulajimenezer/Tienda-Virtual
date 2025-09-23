"""
Script para poblar la base de datos con datos iniciales.
"""

import uuid
from sqlalchemy.orm import sessionmaker
from database.config import engine
from Entities.usuarios import Usuarios
from Entities.roles import Roles
from Entities.sexo import Sexo
from Entities.tipo_documento import Tipo_documento
from Entities.categorias import Categorias
from Entities.productos import Productos
from Entities.direcciones import Direcciones
from Entities.pedidos import Pedidos
from Entities.pedido_items import Pedido_items
from Entities.facturas import Facturas
from Entities.carritos import Carritos
from Entities.carrito_items import Carrito_items
from Entities.descuentos import Descuentos

Session = sessionmaker(bind=engine)
session = Session()

rol_admin = Roles(id=uuid.uuid4(), nombre="admin")
rol_cliente = Roles(id=uuid.uuid4(), nombre="cliente")
session.add_all([rol_admin, rol_cliente])

sexos = [
    Sexo(id=uuid.uuid4(), nombre="M"),
    Sexo(id=uuid.uuid4(), nombre="F"),
    Sexo(id=uuid.uuid4(), nombre="O"),
]
session.add_all(sexos)

tipos_doc = [
    Tipo_documento(id=uuid.uuid4(), nombre="CC"),
    Tipo_documento(id=uuid.uuid4(), nombre="TI"),
    Tipo_documento(id=uuid.uuid4(), nombre="PP"),
]
session.add_all(tipos_doc)

usuario_admin = Usuarios(
    id=uuid.uuid4(),
    nombre="Admin",
    apellido="Principal",
    email="admin@admin.com",
    password="admin123",  
    id_sexo=sexos[0].id,
    id_tipo_documento=tipos_doc[0].id,
    numero_documento="123456789",
    id_rol=rol_admin.id,
    activo=True,
    id_usuario_crea=None,  
    id_usuario_edita=None,
)
usuario_cliente = Usuarios(
    id=uuid.uuid4(),
    nombre="Cliente",
    apellido="Ejemplo",
    email="cliente@correo.com",
    password="cliente123",
    id_sexo=sexos[1].id,
    id_tipo_documento=tipos_doc[1].id,
    numero_documento="987654321",
    id_rol=rol_cliente.id,
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add_all([usuario_admin, usuario_cliente])

direccion_admin = Direcciones(
    id=uuid.uuid4(),
    id_usuario=usuario_admin.id,
    direccion="Calle Admin 123",
    ciudad="AdminCity",
    departamento="AdminDept",
    pais="Colombia",
    telefono="1111111",
    codigo_postal="00001",
    principal=True,
)
direccion_cliente = Direcciones(
    id=uuid.uuid4(),
    id_usuario=usuario_cliente.id,
    direccion="Calle Cliente 456",
    ciudad="ClienteCity",
    departamento="ClienteDept",
    pais="Colombia",
    telefono="2222222",
    codigo_postal="00002",
    principal=True,
)
session.add_all([direccion_admin, direccion_cliente])

cat1 = Categorias(id=uuid.uuid4(), nombre="Electrónica")
cat2 = Categorias(id=uuid.uuid4(), nombre="Ropa")
session.add_all([cat1, cat2])

prod1 = Productos(id=uuid.uuid4(), nombre="Laptop", id_categoria=cat1.id, precio=1000)
prod2 = Productos(id=uuid.uuid4(), nombre="Camiseta", id_categoria=cat2.id, precio=20)
session.add_all([prod1, prod2])

carrito_admin = Carritos(id=uuid.uuid4(), id_usuario=usuario_admin.id, activo=True)
carrito_cliente = Carritos(id=uuid.uuid4(), id_usuario=usuario_cliente.id, activo=True)
session.add_all([carrito_admin, carrito_cliente])

carrito_item1 = Carrito_items(
    id=uuid.uuid4(),
    id_carrito=carrito_admin.id,
    id_producto=prod1.id,
    cantidad=1,
    precio_unitario=1000
)
carrito_item2 = Carrito_items(
    id=uuid.uuid4(),
    id_carrito=carrito_cliente.id,
    id_producto=prod2.id,
    cantidad=2,
    precio_unitario=20
)
session.add_all([carrito_item1, carrito_item2])

descuento1 = Descuentos(
    id=uuid.uuid4(),
    codigo="BIENVENIDO10",
    descripcion="10% de descuento en tu primera compra",
    porcentaje=10,
    activo=True
)
session.add(descuento1)

pedido1 = Pedidos(
    id=uuid.uuid4(),
    id_usuario=usuario_cliente.id,
    id_direccion=direccion_cliente.id,
    estado="pendiente",
    fecha_pedido="2024-01-01"
)
session.add(pedido1)

pedido_item1 = Pedido_items(
    id=uuid.uuid4(),
    id_pedido=pedido1.id,
    id_producto=prod2.id,
    cantidad=2,
    precio_unitario=20
)
session.add(pedido_item1)

factura1 = Facturas(
    id=uuid.uuid4(),
    id_pedido=pedido1.id,
    numero_factura="F0001",
    total=40,
    fecha_emision="2024-01-02"
)
session.add(factura1)

session.commit()
session.close()
print("Datos iniciales insertados correctamente.")