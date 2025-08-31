from .productos import Producto
class Carrito:
    def __init__(self):
        self._items = []  # Lista de tuplas (producto, cantidad)

    def agregar_producto(self, producto: Producto, cantidad: int) -> None:
        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0")
            return

        stock = producto.get_stock()
        if stock < cantidad:
            print("Stock insuficiente")
            return
        else:
            # Verificar si el producto ya existe en el carrito
            # enumerate() devuelve pares (índice, valor) para poder modificar elementos específicos
            # i = índice de la posición en la lista (0, 1, 2, etc.)
            for indice, (producto_existente, cantidad_actual) in enumerate(self._items): 
                if producto_existente == producto:
                    # Si existe, actualizar la cantidad
                    nueva_cantidad = cantidad_actual + cantidad #cantidad_actual es la cantidad actual en el carrito y cantidad es la nueva cantidad a agregar
                    self._items[indice] = (producto, nueva_cantidad)
                    stock -= cantidad
                    producto.set_stock(stock)
                    print(f"Stock actual del producto '{producto.nombre}': {stock}")
                    print(f"{cantidad} unidad(es) de {producto.nombre} agregado(s) al carrito")
                    print(f"Cantidad total en carrito: {nueva_cantidad}")
                    return
            
            # Si no existe, agregarlo como nuevo item
            stock -= cantidad
            producto.set_stock(stock)
            print(f"Stock actual: {stock}")
            self._items.append((producto, cantidad))
            print(f"{cantidad} unidad(es) de {producto.nombre} agregado(s) al carrito")

    def eliminar_producto(self, producto: Producto) -> None:
        for item in self._items:
            if item[0] == producto: #item[0] es el producto y item[1] es la cantidad
                cantidad_en_carrito = item[1]
                # Restaurar el stock del producto
                stock_actual = producto.get_stock()
                nuevo_stock = stock_actual + cantidad_en_carrito
                producto.set_stock(nuevo_stock)
                
                self._items.remove(item) 
                print(f"{producto.nombre} eliminado del carrito")
                print(f"Stock restaurado: {nuevo_stock}")
                return
        print("Producto no encontrado en el carrito")

    def mostrar_carrito(self) -> None:
        if not self._items: #Si no hay productos en el carrito, se imprime un mensaje y se retorna. Si la lista esta vacia python retorna false y por lo tanto se cumple la condicion
            print("El carrito está vacío")
            return
        
        print("\nCarrito de Compras:")
        total = 0
        for producto, cantidad in self._items:
            subtotal = producto.get_precio() * cantidad
            total += subtotal
            print(f"> {producto.nombre} / {cantidad} x ${producto.get_precio():.2f} = ${subtotal:.2f}")
        print(f"Total actual: ${total:.2f}")

    def buscar_producto(self, producto_nombre:str) -> None: #En caso de carritos muy extensos el usuario podria necesitar buscar si ya agrego un producto y de ser asi cuanta cantidad
        for producto, cantidad in self._items:
            if producto.nombre.lower() == producto_nombre.lower(): #lower() para que no importe si el usuario escribe mayusculas o minusculas
                print(f"El producto '{producto.nombre}' está en el carrito con {cantidad} unidad(es).")
        return None

    def vaciar(self) -> None:
        self._items = []
        print("Carrito vaciado correctamente")