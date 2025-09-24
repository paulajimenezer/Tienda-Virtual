"""
Módulo de lógica de tienda para Tienda Virtual.

Define la clase Tienda con métodos para operaciones de cliente sobre el carrito,
productos y descuentos, usando los CRUD correspondientes.
"""

from sqlalchemy.orm import Session
from crud.catalogo.producto_crud import ProductoCRUD
from crud.compras.carritos_crud import get_or_create_carrito_activo
from crud.compras.carrito_items_crud import (
    add_item,
    list_items_carrito,
    remove_item,
    clear_carrito,
)
from crud.compras.descuentos_crud import validar_codigo


class Tienda:
    """
    Lógica de operaciones de tienda para un usuario cliente.

    Métodos:
        - ver_productos
        - agregar_al_carrito
        - eliminar_del_carrito
        - mostrar_carrito
        - calcular_total
        - gestionar_descuento
        - buscar_en_carrito
        - vaciar_carrito
    """

    def __init__(self, db: Session, id_usuario) -> None:
        """
        Inicializa la instancia de Tienda para un usuario.

        Args:
            db: Sesión de base de datos.
            id_usuario: UUID del usuario autenticado.
        """
        self.db = db
        self.id_usuario = id_usuario
        self.carrito = get_or_create_carrito_activo(self.db, id_usuario)

    def _listar_productos(self, limit: int = 50):
        return ProductoCRUD(self.db).obtener_productos_activos(limit=limit)

    def _listar_items(self):
        return list_items_carrito(self.db, self.carrito.id, limit=200)

    def ver_productos(self):
        print("\n--- PRODUCTOS DISPONIBLES ---")
        productos = self._listar_productos()
        if not productos:
            print("No hay productos activos.")
            return
        for i, p in enumerate(productos, start=1):
            print(f"[{i}] {p.nombre} | ${float(p.precio):.2f} | stock: {int(p.stock)}")
        return productos

    def agregar_al_carrito(self):
        productos = self.ver_productos()
        if not productos:
            return
        entrada_producto = input("Ingrese el número del producto: ").strip()
        if not entrada_producto.isdigit():
            print("Debe ingresar un número válido para el producto.")
            return
        idx = int(entrada_producto)
        if idx < 1 or idx > len(productos):
            print(f"Producto no válido. Debe seleccionar 1..{len(productos)}.")
            return

        entrada_cantidad = input("Ingrese la cantidad: ").strip()
        if not entrada_cantidad.isdigit():
            print("Debe ingresar un número válido para la cantidad.")
            return
        cantidad = int(entrada_cantidad)
        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0.")
            return

        prod = productos[idx - 1]
        try:
            add_item(
                self.db,
                id_carrito=self.carrito.id,
                id_producto=prod.id,
                cantidad=cantidad,
                id_usuario_crea=self.id_usuario,
            )
            print(f"{cantidad} unidad(es) de '{prod.nombre}' agregadas al carrito.")
        except Exception as e:
            print(f"No se pudo agregar: {e}")

    def eliminar_del_carrito(self):
        nombre = (input("Ingrese el nombre del producto a eliminar: ") or "").strip()
        if not nombre:
            print("Nombre inválido.")
            return
        items = self._listar_items()
        if not items:
            print("El carrito está vacío.")
            return

        prod = ProductoCRUD(self.db).obtener_producto_por_nombre(nombre)
        if not prod:
            print("Producto no encontrado.")
            return

        for it in items:
            if getattr(it, "id_producto", None) == getattr(prod, "id", None):
                if remove_item(self.db, it.id):
                    print(f"Producto '{prod.nombre}' eliminado del carrito.")
                else:
                    print("No se pudo eliminar el producto del carrito.")
                return
        print("Producto no encontrado en el carrito.")

    def mostrar_carrito(self):
        items = self._listar_items()
        if not items:
            print("El carrito está vacío")
            return
        print("\nCarrito de Compras:")
        total = 0.0
        prod_crud = ProductoCRUD(self.db)
        for it in items:
            prod = prod_crud.obtener_producto(it.id_producto)
            if not prod:
                continue
            precio = float(prod.precio or 0.0)
            qty = int(it.cantidad or 0)
            subtotal = precio * qty
            total += subtotal
            print(f"> {prod.nombre} / {qty} x ${precio:.2f} = ${subtotal:.2f}")
        print(f"Total actual: ${total:.2f}")

    def calcular_total(self) -> float:
        total = 0.0
        prod_crud = ProductoCRUD(self.db)
        for it in self._listar_items():
            prod = prod_crud.obtener_producto(it.id_producto)
            if prod:
                total += float(prod.precio or 0.0) * int(it.cantidad or 0)
        return total

    def gestionar_descuento(self):
        total = self.calcular_total()
        if total <= 0:
            print("El carrito está vacío. No se puede aplicar descuento.")
            return
        codigo = (input("Ingrese código de descuento: ") or "").strip()
        if not codigo:
            print("Código inválido.")
            return
        d = validar_codigo(self.db, codigo)
        if not d:
            print("Descuento no válido o fuera de vigencia.")
            return
        total_desc = total * (1.0 - float(d.porcentaje) / 100.0)
        print(f"Total original: ${total:.2f}")
        print(f"Descuento aplicado: {float(d.porcentaje):.2f}%")
        print(f"Total con descuento: ${total_desc:.2f}")
        print(f"Ahorro: ${total - total_desc:.2f}")

    def buscar_en_carrito(self):
        nombre = (input("Ingrese el nombre del producto a buscar: ") or "").strip()
        if not nombre:
            print("Nombre inválido.")
            return
        prod = ProductoCRUD(self.db).obtener_producto_por_nombre(nombre)
        if not prod:
            print("No se encontró el producto en el carrito.")
            return
        for it in self._listar_items():
            if getattr(it, "id_producto", None) == getattr(prod, "id", None):
                print(
                    f"El producto '{prod.nombre}' está en el carrito con {int(it.cantidad)} unidad(es)."
                )
                return
        print("No se encontró el producto en el carrito.")

    def vaciar_carrito(self):
        count = clear_carrito(self.db, self.carrito.id)
        print(f"Carrito vaciado correctamente. Items eliminados: {count}")

    def mostrar_menu(self):
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

            entrada = input("Seleccione una opción: ").strip()
            if not entrada.isdigit():
                print("Debe ingresar un número válido, no texto.")
                continue

            opcion = int(entrada)
            if opcion == 1:
                self.ver_productos()
            elif opcion == 2:
                self.agregar_al_carrito()
            elif opcion == 3:
                self.eliminar_del_carrito()
            elif opcion == 4:
                self.mostrar_carrito()
            elif opcion == 5:
                print(f"Total actual: ${self.calcular_total():.2f}")
            elif opcion == 6:
                self.gestionar_descuento()
            elif opcion == 7:
                self.buscar_en_carrito()
            elif opcion == 8:
                self.vaciar_carrito()
            elif opcion == 9:
                print("Gracias por su compra. ¡Hasta luego!")
                break
            else:
                print("Opción inválida. Debe seleccionar un número entre 1 y 9.")
