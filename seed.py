"""
Script para poblar la base de datos con datos iniciales.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from database.config import SessionLocal
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


def run_seed():
    session = SessionLocal()
    try:
        # 1) Catálogos base (pueden crearse sin usuario creador)
        rol_admin = session.query(Roles).filter_by(nombre="admin").first()
        if not rol_admin:
            rol_admin = Roles(
                id=uuid.uuid4(),
                nombre="admin",
                descripcion="Administrador",
                id_usuario_crea=None,
            )
            session.add(rol_admin)
        rol_cliente = session.query(Roles).filter_by(nombre="cliente").first()
        if not rol_cliente:
            rol_cliente = Roles(
                id=uuid.uuid4(),
                nombre="cliente",
                descripcion="Cliente",
                id_usuario_crea=None,
            )
            session.add(rol_cliente)

        m = session.query(Sexo).filter_by(codigo="M").first()
        if not m:
            m = Sexo(
                id=uuid.uuid4(), codigo="M", nombre="Masculino", id_usuario_crea=None
            )
            session.add(m)
        f = session.query(Sexo).filter_by(codigo="F").first()
        if not f:
            f = Sexo(
                id=uuid.uuid4(), codigo="F", nombre="Femenino", id_usuario_crea=None
            )
            session.add(f)
        o = session.query(Sexo).filter_by(codigo="O").first()
        if not o:
            o = Sexo(id=uuid.uuid4(), codigo="O", nombre="Otro", id_usuario_crea=None)
            session.add(o)

        cc = session.query(Tipo_documento).filter_by(nombre="CC").first()
        if not cc:
            cc = Tipo_documento(id=uuid.uuid4(), nombre="CC", id_usuario_crea=None)
            session.add(cc)
        ti = session.query(Tipo_documento).filter_by(nombre="TI").first()
        if not ti:
            ti = Tipo_documento(id=uuid.uuid4(), nombre="TI", id_usuario_crea=None)
            session.add(ti)
        pp = session.query(Tipo_documento).filter_by(nombre="PP").first()
        if not pp:
            pp = Tipo_documento(id=uuid.uuid4(), nombre="PP", id_usuario_crea=None)
            session.add(pp)

        session.flush()  # asegurar IDs

        # 2) Usuarios
        usuario_admin = session.query(Usuarios).filter_by(
            email="admin@admin.com"
        ).first() or Usuarios(
            id=uuid.uuid4(),
            nombre="Admin",
            apellido="Principal",
            email="admin@admin.com",
            password="admin123",
            id_sexo=m.id,
            id_tipo_documento=cc.id,
            numero_documento="123456789",
            id_rol=rol_admin.id,
            activo=True,
            id_usuario_crea=None,
            id_usuario_edita=None,
        )
        if usuario_admin not in session:
            session.add(usuario_admin)

        usuario_cliente = session.query(Usuarios).filter_by(
            email="cliente@correo.com"
        ).first() or Usuarios(
            id=uuid.uuid4(),
            nombre="Cliente",
            apellido="Ejemplo",
            email="cliente@correo.com",
            password="cliente123",
            id_sexo=f.id,
            id_tipo_documento=ti.id,
            numero_documento="987654321",
            id_rol=rol_cliente.id,
            activo=True,
            id_usuario_crea=None,
            id_usuario_edita=None,
        )
        if usuario_cliente not in session:
            session.add(usuario_cliente)

        session.flush()

        # 3) Direcciones
        if (
            not session.query(Direcciones)
            .filter_by(id_usuario=usuario_admin.id, principal=True)
            .first()
        ):
            session.add(
                Direcciones(
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
            )
        if (
            not session.query(Direcciones)
            .filter_by(id_usuario=usuario_cliente.id, principal=True)
            .first()
        ):
            session.add(
                Direcciones(
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
            )

        # 4) Categorías y productos
        cat1 = session.query(Categorias).filter_by(nombre="Electrónica").first()
        if not cat1:
            cat1 = Categorias(
                id=uuid.uuid4(),
                nombre="Electrónica",
                descripcion="Productos electrónicos",
                id_usuario_crea=None,
                id_usuario_edita=None,
            )
            session.add(cat1)
        cat2 = session.query(Categorias).filter_by(nombre="Ropa").first()
        if not cat2:
            cat2 = Categorias(
                id=uuid.uuid4(),
                nombre="Ropa",
                descripcion="Prendas de vestir",
                id_usuario_crea=None,
                id_usuario_edita=None,
            )
            session.add(cat2)
        session.flush()

        if not session.query(Productos).filter_by(nombre="Laptop").first():
            session.add(
                Productos(
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
            )
        if not session.query(Productos).filter_by(nombre="Camiseta").first():
            session.add(
                Productos(
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
            )
        session.flush()

        # 5) Carritos e items
        carrito_admin = (
            session.query(Carritos)
            .filter_by(id_usuario=usuario_admin.id, activo=True)
            .first()
        )
        if not carrito_admin:
            carrito_admin = Carritos(
                id=uuid.uuid4(),
                id_usuario=usuario_admin.id,
                activo=True,
                id_usuario_crea=None,
                id_usuario_edita=None,
            )
            session.add(carrito_admin)
        carrito_cliente = (
            session.query(Carritos)
            .filter_by(id_usuario=usuario_cliente.id, activo=True)
            .first()
        )
        if not carrito_cliente:
            carrito_cliente = Carritos(
                id=uuid.uuid4(),
                id_usuario=usuario_cliente.id,
                activo=True,
                id_usuario_crea=None,
                id_usuario_edita=None,
            )
            session.add(carrito_cliente)
        session.flush()

        prod1 = session.query(Productos).filter_by(nombre="Laptop").first()
        prod2 = session.query(Productos).filter_by(nombre="Camiseta").first()

        if (
            prod1
            and not session.query(Carrito_items)
            .filter_by(id_carrito=carrito_admin.id, id_producto=prod1.id)
            .first()
        ):
            session.add(
                Carrito_items(
                    id=uuid.uuid4(),
                    id_carrito=carrito_admin.id,
                    id_producto=prod1.id,
                    cantidad=1,
                    id_usuario_crea=usuario_admin.id,
                    id_usuario_edita=None,
                )
            )
        if (
            prod2
            and not session.query(Carrito_items)
            .filter_by(id_carrito=carrito_cliente.id, id_producto=prod2.id)
            .first()
        ):
            session.add(
                Carrito_items(
                    id=uuid.uuid4(),
                    id_carrito=carrito_cliente.id,
                    id_producto=prod2.id,
                    cantidad=2,
                    id_usuario_crea=usuario_cliente.id,
                    id_usuario_edita=None,
                )
            )

        # 6) Descuento, pedido, items y factura
        hoy = datetime.now()
        descuento1 = session.query(Descuentos).filter_by(codigo="BIENVENIDO10").first()
        if not descuento1:
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
            session.flush()

        direccion_cliente = (
            session.query(Direcciones)
            .filter_by(id_usuario=usuario_cliente.id, principal=True)
            .first()
        )
        pedido1 = (
            session.query(Pedidos)
            .filter_by(id_usuario=usuario_cliente.id, estado="pendiente")
            .first()
        )
        if not pedido1 and direccion_cliente:
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
            session.flush()

        if (
            pedido1
            and prod2
            and not session.query(Pedido_items)
            .filter_by(id_pedido=pedido1.id, id_producto=prod2.id)
            .first()
        ):
            session.add(
                Pedido_items(
                    id=uuid.uuid4(),
                    id_pedido=pedido1.id,
                    id_producto=prod2.id,
                    cantidad=2,
                    precio_unitario=20,
                    id_usuario_crea=usuario_cliente.id,
                    id_usuario_edita=None,
                )
            )

        if (
            pedido1
            and not session.query(Facturas).filter_by(numero_factura="F0001").first()
        ):
            session.add(
                Facturas(
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
            )

        session.commit()
        print("Datos iniciales insertados correctamente.")
    except Exception as e:
        session.rollback()
        print(f"Error durante el seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
