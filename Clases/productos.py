#Clase padre Producto
class Producto:
    def __init__(self, id:int, nombre:str, precio:float, categoria:str):
        self._id = id #(Encapsulado)
        self.nombre = nombre
        self._precio = precio #(Encapsulado)
        self.categoria = categoria
    
    #Gets para los encapsulados
    def get_id(self):
        return self._id
    
    def get_precio(self):
        return self._precio

#Clase hija electrónicos:    
class ProductoElectronico(Producto):
    def __init__(self, id:int, nombre:str, precio:float, marca:str, modelo:str, mesesGarantia:int):
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Electrónico")
        self.marca = marca
        self.modelo=modelo
        self.mesesGarantia = mesesGarantia  
    
    # Polimorfismo (sobreescritura del método "mostrar_informacion")
    def mostrar_informacion(self):
        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio()}, modelo: {self.modelo} categoría: {self.categoria}, garantía: {self.mesesGarantia} meses."
    
#Clase hija ropa:
class ProductoRopa(Producto):
    def __init__(self, id:int, nombre:str, precio:float, marca:str, material:str, talla:str, color:str):
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Ropa")
        self.marca=marca
        self.material=material
        self.talla=talla
        self.color=color

     # Polimorfismo (sobreescritura del método "mostrar_informacion")
    def mostrar_informacion(self):
        return f"Código: {self.get_id()}, nombre: {self.nombre}, marca: {self.marca}, precio: ${self.get_precio()}, categoría: {self.categoria}, talla: {self.talla}, color: {self.color}"

#Clase hija comida:    
class ProductoComida(Producto):
    def __init__(self, id:int, nombre:str, precio:float, tipo:str, peso_gr:int, fechaVencimiento:str):
        #Le envía la información a la clase padre:
        super().__init__(id, nombre, precio, "Comida")
        self.tipo=tipo
        self.peso_gr=peso_gr #Peso en gramos
        self.fechaVencimiento=fechaVencimiento
    
    #Polimorfismo (sobreescritura del método "motrar_informacion")
    def mostrar_informacion(self):
        return f"Código: {self.get_id()}, nombre: {self.nombre}, precio: {self.get_precio()}, categoría: {self.categoria}, tipo: {self.tipo}, peso en gramos: {self.peso_gr} fechaVencimiento: {self.fechaVencimiento}"

#PRUEBAS
# Crear 1 producto de cada tipo
computador = ProductoElectronico(1, "Computador Gamer", 1500, "HP", "Pavilion", 24)
camisa = ProductoRopa(2, "Camisa Formal", 4500, "Zara", "Algodón", "M", "Azul")
manzana = ProductoComida(3, "Manzana Royal", 2, "Fruta", 200, "2024-12-31")

# Imprimir información de cada producto
print(computador.mostrar_informacion())
print(camisa.mostrar_informacion())
print(manzana.mostrar_informacion())