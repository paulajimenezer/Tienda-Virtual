# 🛒 Tienda Virtual - Sistema de Gestión de Productos y Carrito de Compras

## 📋 Descripción del Proyecto

Sistema de tienda virtual desarrollado en Python que implementa un carrito de compras con gestión de productos, categorías, stock y sistema de descuentos. El proyecto utiliza Programación Orientada a Objetos (POO) con principios de encapsulación, herencia, polimorfismo y abstracción.

## 🚀 Características Principales

- **Gestión de Productos**: Sistema de categorías (Electrónicos, Ropa, Comida)
- **Carrito de Compras**: Agregar, eliminar, visualizar y vaciar carrito
- **Control de Stock**: Validación automática de disponibilidad
- **Sistema de Descuentos**: Descuentos porcentuales y fijos
- **Interfaz de Consola**: Menú interactivo para usuarios
- **Validación de Datos**: Entradas validadas para prevenir errores

## 🏗️ Estructura del Proyecto
Tienda-Virtual/
│
├── Clases/
│ ├── init.py
│ ├── carrito.py # Clase Carrito y lógica de gestión
│ ├── productos.py # Clases abstractas y concretas de productos
│ └── tienda.py # Clase Tienda con menú principal
│
├── main.py # Punto de entrada de la aplicación
└── README.md

text

## 🛍️ Categorías de Productos

### 1. **Productos Electrónicos**
- Atributos: Marca, modelo, meses de garantía
- Ejemplo: Computadores, smartphones, tablets

### 2. **Productos de Ropa**
- Atributos: Marca, material, talla, color
- Ejemplo: Camisas, jeans, chaquetas

### 3. **Productos de Comida**
- Atributos: Tipo, peso en gramos, fecha de vencimiento
- Ejemplo: Frutas, cereales, lácteos

## ⚙️ Instalación y Uso

### Requisitos
- Python 3.7 o superior
- No se requieren dependencias externas

### Ejecución
```bash
# Clonar el repositorio
git clone https://github.com/paulajimenezer/Tienda-Virtual.git

# Navegar al directorio
cd Tienda-Virtual

# Ejecutar la aplicación
python main.py
🎮 Funcionalidades del Sistema
Menú Principal
Ver productos disponibles - Lista todos los productos con detalles

Agregar producto al carrito - Selección por ID y cantidad

Eliminar producto del carrito - Por nombre del producto

Ver carrito - Muestra contenido con subtotales y total

Calcular total - Muestra el total actual del carrito

Aplicar descuento - Opciones de 10% o $20 de descuento

Vaciar carrito - Elimina todos los productos

Salir - Finaliza la aplicación

🧩 Principios de POO Implementados
Abstracción: Clase base Producto con métodos abstractos

Encapsulación: Atributos privados con getters y setters

Herencia: Categorías de productos heredan de clase base

Polimorfismo: Métodos str personalizados por categoría

📦 Productos Predefinidos
El sistema incluye 15 productos de ejemplo en 3 categorías:

5 Electrónicos: Computadores, smartphones, tablets

5 Ropa: Camisas, jeans, chaquetas, zapatos

5 Comida: Frutas, cereales, lácteos, pasta

👥 Autores
Paula Jiménez - @paulajimenezer
Miguel Mejía - @miguemjia
Santiago Ospina - @santi-osp

Equipo de Desarrollo - Colaboradores del proyecto

📄 Licencia
Este proyecto está bajo la Licencia MIT.# Tienda-Virtual
Proyecto de tienda virtual para el curso de programación de software
