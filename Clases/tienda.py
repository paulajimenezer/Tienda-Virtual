from .carrito import Carrito
from .productos import ProductoElectronico, ProductoRopa, ProductoComida
from abc import ABC, abstractmethod

# Clase Descuento (Polimorfismo)


class Descuento(ABC):
    @abstractmethod
    def aplicar_descuento(self, total: float) -> float:
        pass


class DescuentoPorcentaje(Descuento):
    def __init__(self, porcentaje: float):
        self.porcentaje = porcentaje

    def aplicar_descuento(self, total: float) -> float:
        return total * (
            1 - self.porcentaje / 100
        )  # Este metodo aplica un descuento del 10% al total del monto


class DescuentoFijo(Descuento):
    def __init__(self, monto: float):
        self.monto = monto

    def aplicar_descuento(self, total: float) -> float:
        return max(
            0, total - self.monto
        )  # Este metodo aplica un descuento fijo de 20$ y con max 0 impide que el resultado sea negativo


# Clase Tienda (Menú Principal)


class Tienda:
    def __init__(self) -> None:
        # Productos iniciales de prueba
        self.productos_disponibles = [
            # Productos Electrónicos
            ProductoElectronico(
                1, "Computador Gamer", 1500.90, "HP", "Pavilion", 24, 5
            ),
            ProductoElectronico(
                2, "Smartphone", 899.99, "Samsung", "Galaxy S24", 12, 15
            ),
            ProductoElectronico(
                3, "Laptop Ultrabook", 1200.50, "Dell", "XPS 13", 24, 8
            ),
            ProductoElectronico(
                4, "Auriculares Bluetooth", 249.99, "Sony", "WH-1000XM5", 12, 20
            ),
            ProductoElectronico(5, "Tablet", 450.75, "Apple", "iPad Air", 12, 12),
            # Productos de Ropa
            ProductoRopa(6, "Camisa Formal", 45.99, "Zara", "Algodón", "M", "Azul", 10),
            ProductoRopa(
                7, "Jeans Clásicos", 75.50, "Levi's", "Denim", "32", "Negro", 25
            ),
            ProductoRopa(
                8, "Chaqueta Deportiva", 120.00, "Nike", "Poliéster", "L", "Gris", 8
            ),
            ProductoRopa(9, "Vestido Casual", 65.99, "H&M", "Algodón", "S", "Rojo", 15),
            ProductoRopa(
                10,
                "Zapatos Deportivos",
                180.25,
                "Adidas",
                "Sintético",
                "42",
                "Blanco",
                18,
            ),
            # Productos de Comida
            ProductoComida(11, "Manzana Royal", 2.09, "Fruta", 200, "2024-12-31", 50),
            ProductoComida(
                12, "Cereal Integral", 8.75, "Desayuno", 500, "2025-06-15", 30
            ),
            ProductoComida(13, "Yogurt Natural", 3.50, "Lácteo", 250, "2024-09-15", 40),
            ProductoComida(
                14, "Pasta Italiana", 4.25, "Carbohidrato", 400, "2025-12-01", 35
            ),
            ProductoComida(
                15, "Chocolate Premium", 12.99, "Dulce", 100, "2025-03-20", 22
            ),
        ]
        self.carrito = Carrito()

    def mostrar_menu(
        self,
    ):  # Menú principal, con todas las opciones disponibles para el usuario
        while True:
            print("\n--- MENÚ TIENDA ONLINE ---")
            print("1. Ver productos disponibles")
            print("2. Agregar producto al carrito")
            print("3. Eliminar producto del carrito")
            print("4. Ver carrito")
            print("5. Calcular total")
            print("6. Aplicar descuento")
            print("7. Buscar producto en carrito")
            print("8. Vaciar carrito")
            print("9. Salir")

            entrada = input("Seleccione una opción: ")

            # Validar que sea un número
            if entrada.isdigit():
                opcion = int(entrada)

                if opcion == 1:
                    self.ver_productos()
                elif opcion == 2:
                    self.agregar_al_carrito()
                elif opcion == 3:
                    self.eliminar_del_carrito()
                elif opcion == 4:
                    self.carrito.mostrar_carrito()
                elif opcion == 5:
                    print(f"Total actual: ${self.calcular_total():.2f}")
                elif opcion == 6:
                    self.gestionar_descuento()
                elif opcion == 7:
                    self.buscar_en_carrito()
                elif opcion == 8:
                    self.carrito.vaciar()
                elif opcion == 9:
                    print("Gracias por su compra. ¡Hasta luego!")
                    break
                else:
                    print("Opción inválida. Debe seleccionar un número entre 1 y 9.")
            else:
                print("Debe ingresar un número válido, no texto.")

    def ver_productos(
        self,
    ):  # Muestra todos los productos disponibles en la tienda recorriendolos en un for
        print("\n--- PRODUCTOS DISPONIBLES ---")
        for i, producto in enumerate(self.productos_disponibles, start=1):
            print(f"[{i}] {producto}")

    def agregar_al_carrito(
        self,
    ):  # Pide al usuario el id del producto y la cantidad, valida que el id sea correcto y llama al metodo agregar_producto del carrito
        entrada_producto = input("Ingrese el número del producto: ")

        # Validar que sea un número
        if entrada_producto.isdigit():
            id_producto = int(entrada_producto)

            # Validar que el número esté en el rango correcto
            if id_producto < 1 or id_producto > len(self.productos_disponibles):
                print(
                    f"Producto no válido. Debe seleccionar un número entre 1 y {len(self.productos_disponibles)}."
                )
                return
        else:
            print("Debe ingresar un número válido para el producto.")
            return

        entrada_cantidad = input("Ingrese la cantidad: ")

        # Validar que sea un número
        if entrada_cantidad.isdigit():
            cantidad = int(entrada_cantidad)

            # Validar que la cantidad sea positiva
            if cantidad <= 0:
                print("La cantidad debe ser mayor a 0.")
                return
        else:
            print("Debe ingresar un número válido para la cantidad.")
            return

        # Convertir a índice de lista (restar 1)
        indice_producto = id_producto - 1
        self.carrito.agregar_producto(
            self.productos_disponibles[indice_producto], cantidad
        )

    def eliminar_del_carrito(
        self,
    ):  # Pide al usuario el nombre del producto a eliminar, busca el producto en la lista de productos disponibles y llama al metodo eliminar_producto del carrito
        nombre = input("Ingrese el nombre del producto a eliminar: ")
        for producto in self.productos_disponibles:
            if producto.nombre.lower() == nombre.lower():
                self.carrito.eliminar_producto(producto)
                return
        print("Producto no encontrado en la tienda.")

    def calcular_total(
        self,
    ):  # Calcula el total del carrito recorriendo los productos y sumando su precio por la cantidad
        total = 0
        for producto, cantidad in self.carrito._items:
            total += producto.get_precio() * cantidad
        return total

    def gestionar_descuento(
        self,
    ):  # Muestra un menu de descuentos disponibles, pide al usuario que seleccione uno y aplica el descuento al total
        total = self.calcular_total()

        # Validar que el carrito no esté vacío
        if total == 0:
            print("El carrito está vacío. No se puede aplicar descuento.")
            return

        print("\n--- DESCUENTOS ---")
        print("1. 10% de descuento")
        print("2. $20 de descuento fijo")

        entrada = input("Seleccione descuento: ")

        # Validar que sea un número
        if entrada.isdigit():
            opcion = int(entrada)

            if opcion == 1:
                descuento = DescuentoPorcentaje(10)
            elif opcion == 2:
                descuento = DescuentoFijo(20)
            else:
                print("Opción inválida. Debe seleccionar 1 o 2.")
                return
        else:
            print("Debe ingresar un número válido (1 o 2).")
            return

        total_desc = descuento.aplicar_descuento(total)
        print(f"Total original: ${total:.2f}")
        print(f"Total con descuento: ${total_desc:.2f}")
        print(f"Ahorro: ${total - total_desc:.2f}")

    def buscar_en_carrito(self) -> None:
        nombre = input("Ingrese el nombre del producto a buscar: ")
        self.carrito.buscar_producto(nombre)
