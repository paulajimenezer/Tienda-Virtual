from .carrito import Carrito
from .productos import ProductoElectronico, ProductoRopa, ProductoComida

# Clase Descuento (Polimorfismo)

class Descuento:
    def aplicar_descuento(self, total: float) -> float:
        return total  # por defecto no hace nada

class DescuentoPorcentaje(Descuento):
    def __init__(self, porcentaje: float):
        self.porcentaje = porcentaje

    def aplicar_descuento(self, total: float) -> float:
        return total * (1 - self.porcentaje / 100)

class DescuentoFijo(Descuento):
    def __init__(self, monto: float):
        self.monto = monto

    def aplicar_descuento(self, total: float) -> float:
        return max(0, total - self.monto)

# Clase Tienda (Menú Principal)

class Tienda:
    def __init__(self):
        # Productos iniciales de prueba
        self.productos_disponibles = [
            ProductoElectronico(1, "Computador Gamer", 1500.90, "HP", "Pavilion", 24, 5),
            ProductoRopa(2, "Camisa Formal", 45.99, "Zara", "Algodón", "M", "Azul", 10),
            ProductoComida(3, "Manzana Royal", 2.09, "Fruta", 200, "2024-12-31", 50)
        ]
        self.carrito = Carrito()

    def mostrar_menu(self):
        while True:
            print("\n--- MENÚ TIENDA ONLINE ---")
            print("1. Ver productos disponibles")
            print("2. Agregar producto al carrito")
            print("3. Eliminar producto del carrito")
            print("4. Ver carrito")
            print("5. Calcular total")
            print("6. Aplicar descuento")
            print("7. Vaciar carrito")
            print("8. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.ver_productos()
            elif opcion == "2":
                self.agregar_al_carrito()
            elif opcion == "3":
                self.eliminar_del_carrito()
            elif opcion == "4":
                self.carrito.mostrar_carrito()
            elif opcion == "5":
                print(f"Total actual: ${self.calcular_total():.2f}")
            elif opcion == "6":
                self.gestionar_descuento()
            elif opcion == "7":
                self.carrito.vaciar()
            elif opcion == "8":
                print("Gracias por su compra. ¡Hasta luego!")
                break
            else:
                print("Opción inválida, intente de nuevo.")

    def ver_productos(self):
        print("\n--- PRODUCTOS DISPONIBLES ---")
        for i, producto in enumerate(self.productos_disponibles, start=1):
            print(f"[{i}] {producto}")

    def agregar_al_carrito(self):
        try:
            id_producto = int(input("Ingrese el número del producto: ")) - 1
            cantidad = int(input("Ingrese la cantidad: "))
            if 0 <= id_producto < len(self.productos_disponibles):
                self.carrito.agregar_producto(self.productos_disponibles[id_producto], cantidad)
            else:
                print("Producto no válido.")
        except ValueError:
            print("Entrada inválida. Intente nuevamente.")

    def eliminar_del_carrito(self):
        nombre = input("Ingrese el nombre del producto a eliminar: ")
        for producto in self.productos_disponibles:
            if producto.nombre.lower() == nombre.lower():
                self.carrito.eliminar_producto(producto)
                return
        print("Producto no encontrado en la tienda.")

    def calcular_total(self):
        total = 0
        for producto, cantidad in self.carrito._items:
            total += producto.get_precio() * cantidad
        return total

    def gestionar_descuento(self):
        print("\n--- DESCUENTOS ---")
        print("1. 10% de descuento")
        print("2. $20 de descuento fijo")
        opcion = input("Seleccione descuento: ")
        total = self.calcular_total()

        if opcion == "1":
            descuento = DescuentoPorcentaje(10)
        elif opcion == "2":
            descuento = DescuentoFijo(20)
        else:
            print("Opción inválida, no se aplica descuento.")
            return

        total_desc = descuento.aplicar_descuento(total)
        print(f"Total con descuento: ${total_desc:.2f}")
