#Abstract Base Classes
from abc import ABC, abstractmethod


# Clase Padre Abstracta
class Producto(ABC):
    def __init__(self, id:int, nombre:str, precio:float, categoria:str, stock:int) ->None:
        self._id = id #(Encapsulado)
        self.nombre = nombre
        self._precio = precio #(Encapsulado)
        self.categoria = categoria
        self._stock = stock
    #Gets para los encapsulados
    def get_id(self) ->int:
        return self._id
    
    def get_precio(self) ->float:
        return self._precio
    
    def get_stock(self) ->int:
        return self._stock
    
    def set_stock(self, stock:int) ->None:
        self._stock = stock
    
     # Método abstracto (asegura que las hijas lo implementen)
    @abstractmethod
    # Método especial __str__: representación textual del objeto
    def __str__(self) -> str:
            pass


#Clase hija electrónicos:    
class ProductoElectronico(Producto):
    def __init__(self, id:int, nombre:str, precio:float, marca:str, modelo:str, mesesGarantia:int, stock:int) ->None:
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Electrónico", stock)
        self.marca = marca
        self.modelo=modelo
        self.mesesGarantia = mesesGarantia  
    
    # Polimorfismo (sobreescritura del método "__str__")
    def __str__(self) -> str:
        #:.2f para que el valor salga con 2 decimales
        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio():.2f}, modelo: {self.modelo}, categoría: {self.categoria}, garantía: {self.mesesGarantia} meses, stock: {self.get_stock()}"
    
#Clase hija ropa:
class ProductoRopa(Producto):
    def __init__(self, id:int, nombre:str, precio:float, marca:str, material:str, talla:str, color:str, stock:int) ->None:
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Ropa", stock)
        self.marca=marca
        self.material=material
        self.talla=talla
        self.color=color

     # Polimorfismo (sobreescritura del método "__str__")
    def __str__(self) -> str:
        #:.2f para que el valor salga con 2 decimales
        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio():.2f}, categoría: {self.categoria}, talla: {self.talla}, color: {self.color}, stock: {self.get_stock()}"

#Clase hija comida:    
class ProductoComida(Producto):
    def __init__(self, id:int, nombre:str, precio:float, tipo:str, peso_gr:int, fechaVencimiento:str, stock:int) ->None:
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Comida", stock)
        self.tipo=tipo
        self.peso_gr=peso_gr #Peso en gramos
        self.fechaVencimiento=fechaVencimiento
    
    # Polimorfismo (sobreescritura del método "__str__")
    def __str__(self) -> str:
        #:.2f para que el valor salga con 2 decimales
        return f"Código: {self.get_id()}, nombre: {self.nombre}, precio: {self.get_precio():.2f}, categoría: {self.categoria}, tipo: {self.tipo}, peso en gramos: {self.peso_gr}, fecha de vencimiento: {self.fechaVencimiento}, stock: {self.get_stock()}"
