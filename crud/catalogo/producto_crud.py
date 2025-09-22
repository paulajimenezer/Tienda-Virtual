"""
Operaciones CRUD para la entidad Productos usando SQLAlchemy.

Incluye creación, lectura, actualización, eliminación y utilidades de consulta con
validaciones de datos y verificación de referencias.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from Entities.productos import Productos as PRODUCTOS
from Entities.categorias import Categorias as CATEGORIAS
from Entities.usuarios import Usuarios as USUARIOS


class ProductoCRUD:
    """
    Operaciones CRUD y utilidades de consulta para Productos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def crear_producto(
        self,
        nombre: str,
        descripcion: str,
        precio: float,
        stock: int,
        categoria_id: UUID,
        usuario_id: UUID,
        id_usuario_crea: UUID = None,
    ) -> PRODUCTOS:
        """
        Crea un nuevo producto con validaciones de negocio y FKs.

        Args:
            nombre: Nombre del producto (máximo 200 caracteres).
            descripcion: Descripción del producto.
            precio: Precio del producto (mayor a 0).
            stock: Cantidad en stock (mayor o igual a 0).
            categoria_id: UUID de la categoría.
            usuario_id: UUID del usuario propietario.
            id_usuario_crea: UUID del usuario que crea el producto (opcional).

        Returns:
            Instancia creada de PRODUCTOS.

        Raises:
            ValueError: Si algún dato es inválido o las referencias no existen.
        """
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre del producto es obligatorio")
        if len(nombre) > 200:
            raise ValueError("El nombre no puede exceder 200 caracteres")
        if not descripcion or len(descripcion.strip()) == 0:
            raise ValueError("La descripción del producto es obligatoria")
        if precio is None or precio <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if stock is None or stock < 0:
            raise ValueError("El stock no puede ser negativo")

        # Validar FK de categoría
        categoria = (
            self.db.query(CATEGORIAS)
            .filter(CATEGORIAS.id_categoria == categoria_id)
            .first()
        )
        if not categoria:
            raise ValueError("La categoría especificada no existe")

        # Validar FK de usuario
        usuario = (
            self.db.query(USUARIOS).filter(USUARIOS.id_usuario == usuario_id).first()
        )
        if not usuario:
            raise ValueError("El usuario especificado no existe")

        if id_usuario_crea is None:
            id_usuario_crea = usuario_id

        obj = PRODUCTOS(
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            precio=precio,
            stock=stock,
            categoria_id=categoria_id,
            usuario_id=usuario_id,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def obtener_producto(self, producto_id: UUID) -> Optional[PRODUCTOS]:
        """
        Obtiene un producto por su UUID.

        Args:
            producto_id: UUID del producto.

        Returns:
            Instancia de PRODUCTOS si existe, None en caso contrario.
        """
        return self.db.get(PRODUCTOS, producto_id)

    def obtener_productos(self, skip: int = 0, limit: int = 100) -> List[PRODUCTOS]:
        """
        Lista productos con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de instancias de PRODUCTOS.
        """
        return self.db.query(PRODUCTOS).offset(skip).limit(limit).all()

    def obtener_productos_por_categoria(self, categoria_id: UUID) -> List[PRODUCTOS]:
        """
        Lista productos filtrados por categoría.

        Args:
            categoria_id: UUID de la categoría.

        Returns:
            Lista de productos pertenecientes a la categoría indicada.
        """
        return (
            self.db.query(PRODUCTOS)
            .filter(PRODUCTOS.categoria_id == categoria_id)
            .all()
        )

    def obtener_productos_por_usuario(self, usuario_id: UUID) -> List[PRODUCTOS]:
        """
        Lista productos filtrados por usuario propietario.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            Lista de productos del usuario indicado.
        """
        return self.db.query(PRODUCTOS).filter(PRODUCTOS.usuario_id == usuario_id).all()

    def buscar_productos_por_nombre(self, nombre: str) -> List[PRODUCTOS]:
        """
        Busca productos por coincidencia parcial en el nombre.

        Args:
            nombre: Texto a buscar.

        Returns:
            Lista de productos que contienen el texto indicado.
        """
        return self.db.query(PRODUCTOS).filter(PRODUCTOS.nombre.contains(nombre)).all()

    def actualizar_producto(
        self, producto_id: UUID, id_usuario_edita: UUID = None, **kwargs
    ) -> Optional[PRODUCTOS]:
        """
        Actualiza un producto validando campos y referencias.

        Args:
            producto_id: UUID del producto a actualizar.
            id_usuario_edita: UUID del usuario que edita (opcional).
            **kwargs: Campos a actualizar (nombre, descripcion, precio, stock, categoria_id, usuario_id).

        Returns:
            Instancia actualizada de PRODUCTOS, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        obj = self.db.get(PRODUCTOS, producto_id)
        if not obj:
            return None

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len(nombre.strip()) == 0:
                raise ValueError("El nombre del producto es obligatorio")
            if len(nombre) > 200:
                raise ValueError("El nombre no puede exceder 200 caracteres")
            kwargs["nombre"] = nombre.strip()

        if "descripcion" in kwargs:
            descripcion = kwargs["descripcion"]
            if not descripcion or len(descripcion.strip()) == 0:
                raise ValueError("La descripción del producto es obligatoria")
            kwargs["descripcion"] = descripcion.strip()

        if "precio" in kwargs:
            precio = kwargs["precio"]
            if precio is None or precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")

        if "stock" in kwargs:
            stock = kwargs["stock"]
            if stock is None or stock < 0:
                raise ValueError("El stock no puede ser negativo")

        if "categoria_id" in kwargs:
            categoria = (
                self.db.query(CATEGORIAS)
                .filter(CATEGORIAS.id_categoria == kwargs["categoria_id"])
                .first()
            )
            if not categoria:
                raise ValueError("La categoría especificada no existe")

        if "usuario_id" in kwargs:
            usuario = (
                self.db.query(USUARIOS)
                .filter(USUARIOS.id_usuario == kwargs["usuario_id"])
                .first()
            )
            if not usuario:
                raise ValueError("El usuario especificado no existe")

        if id_usuario_edita is None:
            # Buscar admin para auditoría (fallback)
            admin = self.db.query(USUARIOS).filter(USUARIOS.es_admin == True).first()
            if not admin:
                raise ValueError(
                    "No se encontró un usuario administrador para editar el producto"
                )
            id_usuario_edita = admin.id_usuario

        # Registrar quién edita si el modelo lo soporta
        if hasattr(obj, "id_usuario_edita"):
            obj.id_usuario_edita = id_usuario_edita

        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def actualizar_stock(
        self, producto_id: UUID, nuevo_stock: int
    ) -> Optional[PRODUCTOS]:
        """
        Actualiza el stock de un producto.

        Args:
            producto_id: UUID del producto.
            nuevo_stock: Nueva cantidad en stock (mayor o igual a 0).

        Returns:
            Instancia actualizada de PRODUCTOS, o None si no existe.

        Raises:
            ValueError: Si el nuevo stock es negativo.
        """
        if nuevo_stock is None or nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        return self.actualizar_producto(producto_id, stock=nuevo_stock)

    def eliminar_producto(self, producto_id: UUID) -> bool:
        """
        Elimina un producto por su UUID.

        Args:
            producto_id: UUID del producto.

        Returns:
            True si se eliminó correctamente, False si no existe.
        """
        obj = self.db.get(PRODUCTOS, producto_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
