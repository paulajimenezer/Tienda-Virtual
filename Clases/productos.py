from abc import ABC, abstractmethod


class Producto(ABC):
    def __init__(
        self, id: int, nombre: str, precio: float, categoria: str, stock: int
    ) -> None:
        self._id = id
        self.nombre = nombre
        self._precio = precio
        self.categoria = categoria
        self._stock = stock

    def get_id(self) -> int:
        return self._id

    def get_precio(self) -> float:
        return self._precio

    def get_stock(self) -> int:
        return self._stock

    def set_stock(self, stock: int) -> None:
        self._stock = stock

    @abstractmethod
    def __str__(self) -> str:
        pass


class ProductoElectronico(Producto):
    def __init__(
        self,
        id: int,
        nombre: str,
        precio: float,
        marca: str,
        modelo: str,
        mesesGarantia: int,
        stock: int,
    ) -> None:

        super().__init__(id, nombre, precio, "Electrónico", stock)
        self.marca = marca
        self.modelo = modelo
        self.mesesGarantia = mesesGarantia

    def __str__(self) -> str:

        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio():.2f}, modelo: {self.modelo}, categoría: {self.categoria}, garantía: {self.mesesGarantia} meses, stock: {self.get_stock()}"


class ProductoRopa(Producto):
    def __init__(
        self,
        id: int,
        nombre: str,
        precio: float,
        marca: str,
        material: str,
        talla: str,
        color: str,
        stock: int,
    ) -> None:

        super().__init__(id, nombre, precio, "Ropa", stock)
        self.marca = marca
        self.material = material
        self.talla = talla
        self.color = color

    def __str__(self) -> str:

        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio():.2f}, categoría: {self.categoria}, talla: {self.talla}, color: {self.color}, stock: {self.get_stock()}"


class ProductoComida(Producto):
    def __init__(
        self,
        id: int,
        nombre: str,
        precio: float,
        tipo: str,
        peso_gr: int,
        fechaVencimiento: str,
        stock: int,
    ) -> None:

        super().__init__(id, nombre, precio, "Comida", stock)
        self.tipo = tipo
        self.peso_gr = peso_gr
        self.fechaVencimiento = fechaVencimiento

    def __str__(self) -> str:

        return f"Código: {self.get_id()}, nombre: {self.nombre}, precio: {self.get_precio():.2f}, categoría: {self.categoria}, tipo: {self.tipo}, peso en gramos: {self.peso_gr}, fecha de vencimiento: {self.fechaVencimiento}, stock: {self.get_stock()}"
