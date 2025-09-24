# Tienda Virtual

Sistema de consola en Python para gestión de catálogo, carrito de compras, pedidos, facturación y administración. Implementa autenticación con registro de clientes, flujo de checkout con cupones y administración de catálogo y descuentos.

## Características

- Autenticación de usuarios con roles (admin y cliente)
- Autoregistro de clientes desde el menú principal
- Catálogo de productos y categorías
- Carrito de compras por usuario
- Descuentos mediante cupones
- Checkout con generación de pedido y factura
- Consulta de facturas del cliente
- Menú de administración: usuarios, productos, categorías, cupones

## Arquitectura

- Utilities: lógica de autenticación, menús y operaciones de tienda
- Entities: modelos ORM (SQLAlchemy) para usuarios, productos, pedidos, etc.
- crud: capa de acceso a datos por módulo (catálogo, compras, pedidos)
- database: configuración de conexión y helpers de inicialización
- Migrations (Alembic): migraciones de esquema (opcional)

Estructura relevante:
- main.py
- init_db.py
- Utilities/
  - auth.py
  - menus.py
  - tienda.py
- Entities/
- crud/
- database/
- Migrations/ (si se usan migraciones)
- requirements.txt

## Requisitos

- Python 3.10 o superior
- PostgreSQL (se recomienda conexión mediante cadena en .env)
- pip para instalación de dependencias

## Configuración

1) Clonar el repositorio
- git clone <url>
- cd Tienda-Virtual

2) Entorno virtual y dependencias
- python -m venv .venv
- .venv\Scripts\activate (Windows) o source .venv/bin/activate (Linux/Mac)
- pip install -r requirements.txt

3) Variables de entorno
- Crear un archivo .env en la raíz con:
  - DATABASE_URL=postgresql://usuario:password@host:puerto/basedatos?sslmode=require

Ejemplo:
- DATABASE_URL=postgresql://neondb_owner:******@host/neondb?sslmode=require&channel_binding=require

4) Inicialización de base de datos
- python init_db.py
- Crea tablas (si no existen) e inserta datos iniciales (seed).

Alternativa sin seeders:
- python -c "from database.config import init_db; init_db(run_seed=False)"

## Ejecución

- python main.py
- Menú principal:
  - 1) Iniciar sesión
  - 2) Crear cuenta (cliente)
  - 9) Salir

## Uso como Cliente

Menú de cliente:
- 1. Ver productos disponibles
- 2. Agregar producto al carrito
- 3. Eliminar producto del carrito
- 4. Ver carrito
- 5. Calcular total
- 6. Aplicar descuento (código)
- 7. Buscar producto en carrito
- 8. Vaciar carrito
- 9. Comprar (checkout)
- 10. Ver mis facturas
- 11. Salir

Notas:
- El checkout genera Pedido, sus ítems y una Factura con número único.
- “Ver mis facturas” lista las facturas del usuario y permite ver su detalle.

## Uso como Administrador

Menú de administración:
- 1) Listar usuarios
- 2) Listar productos
- 3) Gestionar cupones
- 4) Gestionar categorías
- 5) Gestionar productos
- 6) Gestionar usuarios
- 7) Cerrar sesión

## Migraciones (Alembic)

- El archivo alembic.ini apunta a Migrations como script_location.
- Configurar sqlalchemy.url si se requiere ejecutar migraciones fuera del runtime.
- Comandos típicos:
  - alembic revision -m "mensaje"
  - alembic upgrade head
  - alembic downgrade -1

## Datos iniciales (seed)

El script init_db.py (o database.config.init_db) ejecuta seeders que:
- Crean roles, sexos y tipos de documento
- Insertan usuarios de ejemplo (admin y cliente)
- Generan categorías, productos y cupones de bienvenida
- Preparan carritos y una factura de ejemplo

## Consideraciones de Seguridad

- Las contraseñas actualmente se almacenan en texto plano para fines académicos.
- Para uso real, implementar hashing (por ejemplo, bcrypt) y políticas de complejidad.
- No versionar secretos en .env (se incluye en .gitignore).

## Licencia

Proyecto con fines académicos. Ajustar la licencia según las necesidades del equipo.
