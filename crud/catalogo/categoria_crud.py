"""
Operaciones CRUD para Categoría
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from Entities.categorias import Categorias as CATEGORIAS


class CategoriaCRUD:
    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.
        """
        self.db = db

    def crear_categoria(
        self, nombre: str, descripcion: str = None, id_usuario_crea: UUID = None
    ) -> CATEGORIAS:
        """
        Crear una nueva categoría con validaciones.

        Args:
            nombre: Nombre de la categoría (único, máximo 100 caracteres).
            descripcion: Descripción opcional.
            id_usuario_crea: UUID del usuario que crea la categoría.

        Returns:
            La categoría creada (instancia de CATEGORIAS).

        Raises:
            ValueError: Si los datos no son válidos o no hay admin disponible.
        """
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre de la categoría es obligatorio")

        if len(nombre) > 100:
            raise ValueError("El nombre no puede exceder 100 caracteres")

        if self.obtener_categoria_por_nombre(nombre):
            raise ValueError("Ya existe una categoría con ese nombre")

        categoria = CATEGORIAS(
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else None,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def obtener_categoria(self, categoria_id: UUID) -> Optional[CATEGORIAS]:
        """
        Obtener una categoría por ID.

        Args:
            categoria_id: UUID de la categoría.

        Returns:
            Categoría encontrada o None.
        """
        return self.db.get(CATEGORIAS, categoria_id)

    def obtener_categoria_por_nombre(self, nombre: str) -> Optional[CATEGORIAS]:
        """
        Obtener una categoría por nombre.

        Args:
            nombre: Nombre de la categoría.

        Returns:
            Categoría encontrada o None.
        """
        return (
            self.db.query(CATEGORIAS)
            .filter(CATEGORIAS.nombre == nombre.strip())
            .first()
        )

    def obtener_categorias(self, skip: int = 0, limit: int = 100) -> List[CATEGORIAS]:
        """
        Obtener lista de categorías con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Límite de registros a retornar.

        Returns:
            Lista de categorías.
        """
        return self.db.query(CATEGORIAS).offset(skip).limit(limit).all()

    def actualizar_categoria(
        self, categoria_id: UUID, id_usuario_edita: UUID = None, **kwargs
    ) -> Optional[CATEGORIAS]:
        """
        Actualizar una categoría con validaciones.

        Args:
            categoria_id: UUID de la categoría.
            id_usuario_edita: UUID del usuario que edita.
            **kwargs: Campos a actualizar (por ejemplo, nombre, descripcion).

        Returns:
            Categoría actualizada o None.

        Raises:
            ValueError: Si los datos no son válidos o no hay admin disponible.
        """
        categoria = self.obtener_categoria(categoria_id)
        if not categoria:
            return None

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len(nombre.strip()) == 0:
                raise ValueError("El nombre de la categoría es obligatorio")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")

            existente = self.obtener_categoria_por_nombre(nombre)
            if existente and existente.id_categoria != categoria_id:
                raise ValueError("Ya existe una categoría con ese nombre")

            kwargs["nombre"] = nombre.strip()

        if "descripcion" in kwargs and kwargs["descripcion"]:
            kwargs["descripcion"] = kwargs["descripcion"].strip()

        if id_usuario_edita is not None and hasattr(categoria, "id_usuario_edita"):
            categoria.id_usuario_edita = id_usuario_edita

        for key, value in kwargs.items():
            if hasattr(categoria, key):
                setattr(categoria, key, value)

        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def eliminar_categoria(self, categoria_id: UUID) -> bool:
        """
        Eliminar una categoría.
        Si existen productos asociados, no se elimina (para evitar errores por FK).
        """
        categoria = self.obtener_categoria(categoria_id)
        if not categoria:
            return False
        from Entities.productos import Productos as PRODUCTOS

        asociados = (
            self.db.query(PRODUCTOS)
            .filter(PRODUCTOS.id_categoria == categoria.id)
            .count()
        )
        if asociados > 0:
            raise ValueError(
                "No se puede eliminar: la categoría tiene productos asociados"
            )
        self.db.delete(categoria)
        self.db.commit()
        return True
