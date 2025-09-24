"""
Módulo de menús de consola para Tienda Virtual.

Define los menús interactivos para clientes y administradores.
"""

from sqlalchemy.orm import Session
from Entities.usuarios import Usuarios
from Entities.productos import Productos
from Entities.categorias import Categorias
from Entities.carritos import Carritos
from Entities.direcciones import Direcciones
from .tienda import Tienda

# CRUD y utilidades
from crud.compras.carritos_crud import (
    list_carritos_usuario,
    get_or_create_carrito_activo,
    update_carrito,
    cerrar_carrito,
)
from crud.compras.carrito_items_crud import list_items_carrito, clear_carrito
from crud.compras.descuentos_crud import (
    list_descuentos,
    create_descuento,
    delete_descuento,
    update_descuento,
    validar_codigo,
)
from crud.pedidos.pedidos_crud import PedidoCRUD
from crud.pedidos.pedido_items_crud import PedidoItemCRUD
from crud.pedidos.facturas_crud import FacturaCRUD


def _listar_usuarios(db: Session, limit: int = 50):
    """
    Lista usuarios básicos para el menú admin.
    """
    print("\n--- Usuarios (top) ---")
    for i, u in enumerate(db.query(Usuarios).limit(limit).all(), start=1):
        rol = getattr(getattr(u, "rol", None), "nombre", None)
        print(f"[{i}] {u.nombre} {u.apellido} | {u.email} | rol: {rol}")


def _listar_productos(db: Session, limit: int = 50):
    """
    Lista productos básicos para el menú admin.
    """
    print("\n--- Productos (top) ---")
    for i, p in enumerate(db.query(Productos).limit(limit).all(), start=1):
        print(f"[{i}] {p.nombre} | ${float(p.precio):.2f} | stock: {int(p.stock)}")


def _gestionar_carritos(db: Session, user: Usuarios):
    """
    Submenú para gestionar múltiples carritos del cliente:
    - Ver carritos
    - Crear nuevo carrito (desactiva el actual)
    - Cambiar carrito activo
    - Cerrar carrito activo
    """
    while True:
        print("\n--- Carritos ---")
        print("1) Ver mis carritos")
        print("2) Crear nuevo carrito (y activar)")
        print("3) Cambiar carrito activo")
        print("4) Cerrar carrito activo")
        print("9) Volver")
        op = input("Seleccione: ").strip()
        if op == "9":
            break
        elif op == "1":
            carritos = list_carritos_usuario(db, user.id, limit=200)
            if not carritos:
                print("No tiene carritos aún.")
                continue
            for i, c in enumerate(carritos, start=1):
                print(f"[{i}] {c.id} | activo: {bool(c.activo)}")
        elif op == "2":
            # Desactivar carritos actuales y crear uno nuevo activo
            carritos = list_carritos_usuario(db, user.id, limit=200)
            for c in carritos:
                if bool(c.activo):
                    update_carrito(db, c.id, activo=False, id_usuario_edita=user.id)
            nuevo = get_or_create_carrito_activo(db, user.id, id_usuario_crea=user.id)
            print(f"Nuevo carrito activo: {nuevo.id}")
        elif op == "3":
            carritos = list_carritos_usuario(db, user.id, limit=200)
            if not carritos:
                print("No tiene carritos.")
                continue
            for i, c in enumerate(carritos, start=1):
                print(f"[{i}] {c.id} | activo: {bool(c.activo)}")
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(carritos):
                print("Selección inválida.")
                continue
            elegido = carritos[int(sel) - 1]
            # Desactivar todos y activar el elegido
            for c in carritos:
                update_carrito(
                    db, c.id, activo=(c.id == elegido.id), id_usuario_edita=user.id
                )
            print(f"Carrito activo ahora: {elegido.id}")
        elif op == "4":
            activo = get_or_create_carrito_activo(db, user.id, id_usuario_crea=user.id)
            cerrar_carrito(db, activo.id, id_usuario_edita=user.id)
            print("Carrito activo cerrado.")
        else:
            print("Opción inválida")


def _seleccionar_direccion(db: Session, user: Usuarios) -> Direcciones | None:
    """
    Permite escoger una dirección del usuario o crear una nueva.
    """
    while True:
        direcciones = (
            db.query(Direcciones).filter(Direcciones.id_usuario == user.id).all()
        )
        print("\n--- Direcciones ---")
        if not direcciones:
            print("No tiene direcciones.")
        else:
            for i, d in enumerate(direcciones, start=1):
                print(
                    f"[{i}] {d.direccion}, {d.ciudad}, {d.pais} | CP {d.codigo_postal}"
                )
        print("A) Agregar nueva dirección")
        print("X) Cancelar")
        sel = input("Seleccione: ").strip().upper()
        if sel == "X":
            return None
        if sel == "A":
            direccion = input("Dirección: ").strip()
            ciudad = input("Ciudad: ").strip()
            cp = input("Código postal (opcional): ").strip() or None
            pais = input("País: ").strip()
            if not direccion or not ciudad or not pais:
                print("Dirección/Ciudad/País son obligatorios.")
                continue
            obj = Direcciones(
                id_usuario=user.id,
                direccion=direccion,
                ciudad=ciudad,
                codigo_postal=cp,
                pais=pais,
                principal=False,
                id_usuario_crea=user.id,
            )
            db.add(obj)
            db.commit()
            db.refresh(obj)
            print("Dirección creada.")
            return obj
        if sel.isdigit():
            idx = int(sel)
            if 1 <= idx <= len(direcciones):
                return direcciones[idx - 1]
        print("Selección inválida.")


def _checkout(db: Session, user: Usuarios):
    """
    Flujo de compra:
    - Usa el carrito activo.
    - Selección o creación de dirección.
    - Aplicación de descuento opcional.
    - Crea Pedido, Pedido_items y Factura.
    - Limpia y cierra el carrito.
    """
    carrito = get_or_create_carrito_activo(db, user.id, id_usuario_crea=user.id)
    items = list_items_carrito(db, carrito.id, limit=500)
    if not items:
        print("El carrito está vacío.")
        return

    # Calcular total con precios actuales
    total = 0.0
    productos = {p.id: p for p in db.query(Productos).all()}
    for it in items:
        p = productos.get(it.id_producto)
        if not p:
            continue
        total += float(p.precio or 0.0) * int(it.cantidad or 0)

    dcto = None
    code = input("Código de descuento (ENTER para omitir): ").strip()
    if code:
        dcto = validar_codigo(db, code)
        if not dcto:
            print("Código de descuento inválido o vencido. Continuando sin descuento.")
        else:
            total = total * (1.0 - float(dcto.porcentaje) / 100.0)

    direccion = _seleccionar_direccion(db, user)
    if not direccion:
        print("Compra cancelada (sin dirección).")
        return

    # Crear pedido
    pedido = PedidoCRUD(db).crear_pedido(
        id_usuario=user.id,
        id_direccion=direccion.id,
        total=float(total),
        estado="Creado",
        id_descuento=getattr(dcto, "id", None),
        id_usuario_crea=user.id,
    )

    # Crear ítems del pedido con precios actuales
    pi_crud = PedidoItemCRUD(db)
    for it in items:
        p = productos.get(it.id_producto)
        if not p:
            continue
        pi_crud.crear_pedido_item(
            id_pedido=pedido.id,
            id_producto=p.id,
            cantidad=int(it.cantidad or 0),
            precio_unitario=float(p.precio or 0.0),
            id_usuario_crea=user.id,
        )

    # Crear factura simple
    numero = f"F{pedido.id.hex[:8].upper()}"
    FacturaCRUD(db).crear_factura(
        id_pedido=pedido.id,
        numero_factura=numero,
        subtotal=float(total),
        impuesto=0.0,
        total=float(total),
        id_usuario_crea=user.id,
    )

    # Limpiar y cerrar carrito
    clear_carrito(db, carrito.id)
    cerrar_carrito(db, carrito.id, id_usuario_edita=user.id)
    print(f"Compra realizada. Número de factura: {numero}")


def _admin_cupones(db: Session, admin: Usuarios):
    while True:
        print("\n--- Admin: Cupones ---")
        print("1) Listar cupones")
        print("2) Crear cupón")
        print("3) Activar/Desactivar cupón")
        print("4) Eliminar cupón")
        print("9) Volver")
        op = input("Seleccione: ").strip()
        if op == "9":
            break
        elif op == "1":
            dctos = list_descuentos(db, limit=100)
            for i, d in enumerate(dctos, start=1):
                print(
                    f"[{i}] {d.codigo} | {float(d.porcentaje):.2f}% | activo: {bool(d.activo)}"
                )
        elif op == "2":
            codigo = input("Código: ").strip()
            try:
                porcentaje = float(input("Porcentaje (0-100): ").strip())
                dias = int(input("Vigencia en días: ").strip())
            except Exception:
                print("Entradas inválidas.")
                continue
            from datetime import datetime, timedelta

            try:
                create_descuento(
                    db,
                    codigo=codigo,
                    porcentaje=porcentaje,
                    fecha_inicio=datetime.utcnow(),
                    fecha_fin=datetime.utcnow() + timedelta(days=dias),
                    activo=True,
                    id_usuario_crea=admin.id,
                )
                print("Cupón creado.")
            except Exception as e:
                print(f"Error: {e}")
        elif op == "3":
            dctos = list_descuentos(db, limit=100)
            if not dctos:
                print("No hay cupones.")
                continue
            for i, d in enumerate(dctos, start=1):
                print(
                    f"[{i}] {d.codigo} | {float(d.porcentaje):.2f}% | activo: {bool(d.activo)}"
                )
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(dctos):
                print("Selección inválida.")
                continue
            d = dctos[int(sel) - 1]
            try:
                update_descuento(
                    db, d.id, activo=not bool(d.activo), id_usuario_edita=admin.id
                )
                print("Actualizado.")
            except Exception as e:
                print(f"Error: {e}")
        elif op == "4":
            dctos = list_descuentos(db, limit=100)
            if not dctos:
                print("No hay cupones.")
                continue
            for i, d in enumerate(dctos, start=1):
                print(f"[{i}] {d.codigo}")
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(dctos):
                print("Selección inválida.")
                continue
            d = dctos[int(sel) - 1]
            if delete_descuento(db, d.id):
                print("Cupón eliminado.")
            else:
                print("No se pudo eliminar.")
        else:
            print("Opción inválida")


def _admin_categorias(db: Session, admin: Usuarios):
    while True:
        print("\n--- Admin: Categorías ---")
        print("1) Listar")
        print("2) Crear")
        print("3) Eliminar")
        print("9) Volver")
        op = input("Seleccione: ").strip()
        if op == "9":
            break
        elif op == "1":
            cats = db.query(Categorias).order_by(Categorias.nombre.asc()).all()
            for i, c in enumerate(cats, start=1):
                print(f"[{i}] {c.nombre} | {c.descripcion}")
        elif op == "2":
            nombre = input("Nombre: ").strip()
            descripcion = input("Descripción (opcional): ").strip() or None
            if not nombre:
                print("Nombre obligatorio.")
                continue
            if db.query(Categorias).filter(Categorias.nombre == nombre).first():
                print("Ya existe una categoría con ese nombre.")
                continue
            obj = Categorias(
                nombre=nombre, descripcion=descripcion, id_usuario_crea=admin.id
            )
            db.add(obj)
            db.commit()
            print("Categoría creada.")
        elif op == "3":
            cats = db.query(Categorias).order_by(Categorias.nombre.asc()).all()
            if not cats:
                print("No hay categorías.")
                continue
            for i, c in enumerate(cats, start=1):
                print(f"[{i}] {c.nombre}")
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(cats):
                print("Selección inválida.")
                continue
            db.delete(cats[int(sel) - 1])
            db.commit()
            print("Categoría eliminada.")
        else:
            print("Opción inválida")


def _admin_productos(db: Session, admin: Usuarios):
    while True:
        print("\n--- Admin: Productos ---")
        print("1) Listar")
        print("2) Crear")
        print("3) Actualizar precio/stock")
        print("4) Eliminar")
        print("9) Volver")
        op = input("Seleccione: ").strip()
        if op == "9":
            break
        elif op == "1":
            _listar_productos(db, limit=200)
        elif op == "2":
            nombre = input("Nombre: ").strip()
            descripcion = input("Descripción: ").strip()
            try:
                precio = float(input("Precio: ").strip())
                stock = int(input("Stock: ").strip())
            except Exception:
                print("Valores de precio/stock inválidos.")
                continue
            cats = db.query(Categorias).order_by(Categorias.nombre.asc()).all()
            if not cats:
                print("Debe crear categorías primero.")
                continue
            for i, c in enumerate(cats, start=1):
                print(f"[{i}] {c.nombre}")
            sel = input("Categoría (índice): ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(cats):
                print("Selección inválida.")
                continue
            cat = cats[int(sel) - 1]
            obj = Productos(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                stock=stock,
                id_categoria=cat.id,
                activo=True,
                id_usuario_crea=admin.id,
            )
            db.add(obj)
            db.commit()
            print("Producto creado.")
        elif op == "3":
            prods = db.query(Productos).order_by(Productos.nombre.asc()).all()
            if not prods:
                print("No hay productos.")
                continue
            for i, p in enumerate(prods, start=1):
                print(
                    f"[{i}] {p.nombre} | ${float(p.precio):.2f} | stock: {int(p.stock)}"
                )
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(prods):
                print("Selección inválida.")
                continue
            p = prods[int(sel) - 1]
            nuevo_precio = input("Nuevo precio (ENTER para mantener): ").strip()
            nuevo_stock = input("Nuevo stock (ENTER para mantener): ").strip()
            if nuevo_precio:
                try:
                    p.precio = float(nuevo_precio)
                except Exception:
                    print("Precio inválido (ignorado).")
            if nuevo_stock:
                try:
                    p.stock = int(nuevo_stock)
                except Exception:
                    print("Stock inválido (ignorado).")
            db.commit()
            print("Producto actualizado.")
        elif op == "4":
            prods = db.query(Productos).order_by(Productos.nombre.asc()).all()
            if not prods:
                print("No hay productos.")
                continue
            for i, p in enumerate(prods, start=1):
                print(f"[{i}] {p.nombre}")
            sel = input("Seleccione índice: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(prods):
                print("Selección inválida.")
                continue
            db.delete(prods[int(sel) - 1])
            db.commit()
            print("Producto eliminado.")
        else:
            print("Opción inválida")


def _admin_usuarios(db: Session, admin: Usuarios):
    while True:
        print("\n--- Admin: Usuarios ---")
        print("1) Listar usuarios")
        print("2) Crear cliente")
        print("3) Eliminar usuario")
        print("9) Volver")
        op = input("Seleccione: ").strip()
        if op == "9":
            break
        elif op == "1":
            _listar_usuarios(db, limit=200)
        elif op == "2":
            # Reusa el registro simple (cliente)
            from .auth import register_client_prompt

            register_client_prompt(db)
        elif op == "3":
            users = db.query(Usuarios).order_by(Usuarios.email.asc()).all()
            if not users:
                print("No hay usuarios.")
                continue
            for i, u in enumerate(users, start=1):
                rol = getattr(getattr(u, "rol", None), "nombre", None)
                print(f"[{i}] {u.email} | rol: {rol}")
            sel = input("Seleccione índice a eliminar: ").strip()
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(users):
                print("Selección inválida.")
                continue
            u = users[int(sel) - 1]
            if u.id == admin.id:
                print("No puede eliminar su propia cuenta.")
                continue
            db.delete(u)
            db.commit()
            print("Usuario eliminado.")
        else:
            print("Opción inválida")


def cliente_menu(db: Session, user: Usuarios):
    """
    Menú de cliente: bucle interactivo para operaciones de tienda.

    Args:
        db: Sesión de base de datos.
        user: Usuario autenticado.
    """
    print(f"\nBienvenido (Cliente) {user.nombre}")
    tienda = Tienda(db, user.id)
    while True:
        print("\n--- MENÚ TIENDA ONLINE ---")
        print("1. Ver productos disponibles")
        print("2. Agregar producto al carrito")
        print("3. Eliminar producto del carrito")
        print("4. Ver carrito")
        print("5. Calcular total")
        print("6. Aplicar descuento (código)")
        print("7. Buscar producto en carrito")
        print("8. Vaciar carrito")
        print("9. Salir")
        print("10. Gestionar carritos")
        print("11. Comprar (checkout)")

        entrada = input("Seleccione una opción: ").strip()
        if not entrada.isdigit():
            print("Debe ingresar un número válido, no texto.")
            continue

        opcion = int(entrada)
        if opcion == 1:
            tienda.ver_productos()
        elif opcion == 2:
            tienda.agregar_al_carrito()
        elif opcion == 3:
            tienda.eliminar_del_carrito()
        elif opcion == 4:
            tienda.mostrar_carrito()
        elif opcion == 5:
            print(f"Total actual: ${tienda.calcular_total():.2f}")
        elif opcion == 6:
            tienda.gestionar_descuento()
        elif opcion == 7:
            tienda.buscar_en_carrito()
        elif opcion == 8:
            tienda.vaciar_carrito()
        elif opcion == 10:
            _gestionar_carritos(db, user)
            # refrescar carrito activo para Tienda
            tienda.carrito = get_or_create_carrito_activo(
                db, user.id, id_usuario_crea=user.id
            )
        elif opcion == 11:
            _checkout(db, user)
            # refrescar carrito activo post-checkout
            tienda.carrito = get_or_create_carrito_activo(
                db, user.id, id_usuario_crea=user.id
            )
        elif opcion == 9:
            print("Gracias por su compra. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Debe seleccionar un número entre 1 y 11.")
    print("Sesión de cliente finalizada.")


def admin_menu(db: Session, user: Usuarios):
    """
    Menú de administrador: acceso a utilidades y menú de cliente.

    Args:
        db: Sesión de base de datos.
        user: Usuario autenticado.
    """
    print(f"\nBienvenido (Administrador) {user.nombre}")
    while True:
        print("\n--- Menú Admin ---")
        print("1) Abrir menú de Tienda (como cliente)")
        print("2) Listar usuarios")
        print("3) Listar productos")
        print("4) Gestionar cupones")
        print("5) Gestionar categorías")
        print("6) Gestionar productos")
        print("7) Gestionar usuarios")
        print("9) Cerrar sesión")
        opt = input("Seleccione: ").strip()
        if opt == "1":
            cliente_menu(db, user)
        elif opt == "2":
            _listar_usuarios(db)
        elif opt == "3":
            _listar_productos(db)
        elif opt == "4":
            _admin_cupones(db, user)
        elif opt == "5":
            _admin_categorias(db, user)
        elif opt == "6":
            _admin_productos(db, user)
        elif opt == "7":
            _admin_usuarios(db, user)
        elif opt == "9":
            print("Cerrando sesión de administrador...")
            break
        else:
            print("Opción inválida")
