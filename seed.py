"""
Script para poblar la base de datos con datos iniciales.
"""

import uuid
from datetime import datetime, timedelta
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

rol_admin = Roles(
    id=uuid.uuid4(),
    nombre="admin",
    descripcion="Administrador",
    id_usuario_crea=None,
)
rol_cliente = Roles(
    id=uuid.uuid4(),
    nombre="cliente",
    descripcion="Cliente",
    id_usuario_crea=None,
)
session.add_all([rol_admin, rol_cliente])

sexos = [
    Sexo(id=uuid.uuid4(), codigo="M", nombre="Masculino", id_usuario_crea=None),
    Sexo(id=uuid.uuid4(), codigo="F", nombre="Femenino", id_usuario_crea=None),
    Sexo(id=uuid.uuid4(), codigo="O", nombre="Otro", id_usuario_crea=None),
]
session.add_all(sexos)

tipos_doc = [
    Tipo_documento(id=uuid.uuid4(), nombre="CC", id_usuario_crea=None),
    Tipo_documento(id=uuid.uuid4(), nombre="TI", id_usuario_crea=None),
    Tipo_documento(id=uuid.uuid4(), nombre="PP", id_usuario_crea=None),
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
    codigo_postal="00001",
    pais="Colombia",
    principal=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
direccion_cliente = Direcciones(
    id=uuid.uuid4(),
    id_usuario=usuario_cliente.id,
    direccion="Calle Cliente 456",
    ciudad="ClienteCity",
    codigo_postal="00002",
    pais="Colombia",
    principal=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add_all([direccion_admin, direccion_cliente])

cat1 = Categorias(
    id=uuid.uuid4(),
    nombre="Electrónica",
    descripcion="Productos electrónicos",
    id_usuario_crea=None,
    id_usuario_edita=None,
)
cat2 = Categorias(
    id=uuid.uuid4(),
    nombre="Ropa",
    descripcion="Prendas de vestir",
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add_all([cat1, cat2])

prod1 = Productos(
    id=uuid.uuid4(),
    nombre="Laptop",
    descripcion="Laptop de alto rendimiento",
    precio=1000,
    stock=10,
    id_categoria=cat1.id,
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
prod2 = Productos(
    id=uuid.uuid4(),
    nombre="Camiseta",
    descripcion="Camiseta de algodón",
    precio=20,
    stock=50,
    id_categoria=cat2.id,
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add_all([prod1, prod2])

carrito_admin = Carritos(
    id=uuid.uuid4(),
    id_usuario=usuario_admin.id,
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
carrito_cliente = Carritos(
    id=uuid.uuid4(),
    id_usuario=usuario_cliente.id,
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add_all([carrito_admin, carrito_cliente])

carrito_item1 = Carrito_items(
    id=uuid.uuid4(),
    id_carrito=carrito_admin.id,
    id_producto=prod1.id,
    cantidad=1,
    id_usuario_crea=usuario_admin.id,
    id_usuario_edita=None,
)
carrito_item2 = Carrito_items(
    id=uuid.uuid4(),
    id_carrito=carrito_cliente.id,
    id_producto=prod2.id,
    cantidad=2,
    id_usuario_crea=usuario_cliente.id,
    id_usuario_edita=None,
)
session.add_all([carrito_item1, carrito_item2])

hoy = datetime.now()
descuento1 = Descuentos(
    id=uuid.uuid4(),
    codigo="BIENVENIDO10",
    porcentaje=10,
    fecha_inicio=hoy,
    fecha_fin=hoy + timedelta(days=30),
    activo=True,
    id_usuario_crea=None,
    id_usuario_edita=None,
)
session.add(descuento1)

pedido1 = Pedidos(
    id=uuid.uuid4(),
    id_usuario=usuario_cliente.id,
    id_direccion=direccion_cliente.id,
    id_descuento=descuento1.id,
    fecha_pedido=hoy,
    estado="pendiente",
    total=40,
    id_usuario_crea=usuario_cliente.id,
    id_usuario_edita=None,
)
session.add(pedido1)

pedido_item1 = Pedido_items(
    id=uuid.uuid4(),
    id_pedido=pedido1.id,
    id_producto=prod2.id,
    cantidad=2,
    precio_unitario=20,
    id_usuario_crea=usuario_cliente.id,
    id_usuario_edita=None,
)
session.add(pedido_item1)

factura1 = Facturas(
    id=uuid.uuid4(),
    id_pedido=pedido1.id,
    numero_factura="F0001",
    fecha_emision=hoy,
    subtotal=40,
    impuesto=0,
    total=40,
    id_usuario_crea=usuario_cliente.id,
    id_usuario_edita=None,
)
session.add(factura1)

session.commit()
session.close()
print("Datos iniciales insertados correctamente.")