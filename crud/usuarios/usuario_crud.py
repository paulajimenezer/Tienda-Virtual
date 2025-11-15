"""
Operaciones CRUD y utilidades para la entidad Usuarios.

Incluye creación, consulta, actualización, eliminación, autenticación y gestión de contraseñas,
con validaciones de entrada y verificación de entidades normalizadoras (Roles, Sexo, Tipo_documento).
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from auth.security import PasswordManager
from Entities.roles import Roles
from Entities.sexo import Sexo
from Entities.tipo_documento import Tipo_documento
from Entities.usuarios import Usuarios as USUARIOS


class UsuarioCRUD:
    """
    Operaciones CRUD y utilidades de autenticación/administración para Usuarios.
    """

    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def _validar_email(self, email: str) -> bool:
        """
        Valida el formato de un email.

        Args:
            email: Email a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email or "") is not None

    def _validar_numero_documento(self, numero: str) -> bool:
        """
        Valida que el número de documento tenga entre 7 y 12 dígitos numéricos.

        Args:
            numero: Número de documento a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        numero = (numero or "").strip()
        return numero.isdigit() and 7 <= len(numero) <= 12

    def crear_usuario(
        self,
        nombre: str,
        apellido: str,
        email: str,
        password: str,
        numero_documento: str,
        id_rol: UUID,
        id_tipo_documento: UUID,
        id_sexo: Optional[UUID] = None,
        id_usuario_crea: Optional[UUID] = None,
    ) -> USUARIOS:
        """
        Crea un nuevo usuario con validaciones y normalización.

        Args:
            nombre: Nombre del usuario (máximo 100 caracteres).
            apellido: Apellido del usuario (máximo 100 caracteres).
            email: Correo electrónico válido y único.
            password: Contraseña en texto plano que será hasheada.
            numero_documento: Número del documento.
            id_rol: UUID del rol asignado al usuario.
            id_tipo_documento: UUID del tipo de documento.
            id_sexo: UUID del sexo del usuario (opcional).
            id_usuario_crea: UUID del usuario que crea este registro (opcional).

        Returns:
            Instancia creada de USUARIOS.

        Raises:
            ValueError: Si los datos son inválidos o si los FKs no existen.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")
        if not apellido or not apellido.strip():
            raise ValueError("El apellido es obligatorio")
        if not email or not self._validar_email(email):
            raise ValueError("Email inválido")
        if not password:
            raise ValueError("La contraseña es obligatoria")
        es_valida, mensaje = PasswordManager.validate_password_strength(password)
        if not es_valida:
            raise ValueError(f"Contraseña inválida: {mensaje}")
        if not numero_documento or not self._validar_numero_documento(numero_documento):
            raise ValueError("Número de documento inválido")

        # Unicidad
        if self.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")
        existente_doc = (
            self.db.query(USUARIOS)
            .filter(USUARIOS.numero_documento == numero_documento.strip())
            .first()
        )
        if existente_doc:
            raise ValueError("El número de documento ya está registrado")

        # FKs
        if self.db.get(Roles, id_rol) is None:
            raise ValueError("El rol especificado no existe")
        if self.db.get(Tipo_documento, id_tipo_documento) is None:
            raise ValueError("El tipo de documento especificado no existe")
        if id_sexo is not None and self.db.get(Sexo, id_sexo) is None:
            raise ValueError("El sexo especificado no existe")

        usuario = USUARIOS(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.lower().strip(),
            password=PasswordManager.hash_password(password),
            numero_documento=numero_documento.strip(),
            id_rol=id_rol,
            id_tipo_documento=id_tipo_documento,
            id_sexo=id_sexo,
        )
        if hasattr(usuario, "id_usuario_crea") and id_usuario_crea:
            usuario.id_usuario_crea = id_usuario_crea

        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def obtener_usuario(self, usuario_id: UUID) -> Optional[USUARIOS]:
        """
        Obtiene un usuario por su clave primaria.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            Instancia de USUARIOS si existe, None en caso contrario.
        """
        return self.db.get(USUARIOS, usuario_id)

    def obtener_usuario_por_email(self, email: str) -> Optional[USUARIOS]:
        """
        Obtiene un usuario a partir de su email.

        Args:
            email: Correo electrónico del usuario.

        Returns:
            Instancia de USUARIOS si existe, None en caso contrario.
        """
        return (
            self.db.query(USUARIOS)
            .filter(USUARIOS.email == (email or "").lower().strip())
            .first()
        )

    def obtener_usuarios(self, skip: int = 0, limit: int = 100) -> List[USUARIOS]:
        """
        Lista usuarios con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Límite máximo de registros a retornar.

        Returns:
            Lista de instancias de USUARIOS.
        """
        return self.db.query(USUARIOS).offset(skip).limit(limit).all()

    def autenticar_usuario(self, email: str, password: str) -> Optional[USUARIOS]:
        """
        Autentica un usuario por nombre de usuario o email y contraseña.

        Args:
            email: Nombre de usuario o email.
            password: Contraseña en texto plano.

        Returns:
            Instancia de USUARIOS si las credenciales son válidas, None en caso contrario.
        """
        usuario = self.obtener_usuario_por_email(email)
        if not usuario or (hasattr(usuario, "activo") and not usuario.activo):
            return None
        if PasswordManager.verify_password(password, usuario.password):
            return usuario
        return None

    def cambiar_contraseña(
        self, usuario_id: UUID, contraseña_actual: str, nueva_contraseña: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario tras verificar la actual y la política.

        Args:
            usuario_id: UUID del usuario.
            contraseña_actual: Contraseña actual.
            nueva_contraseña: Nueva contraseña.

        Returns:
            True si se actualizó correctamente, False si el usuario no existe.

        Raises:
            ValueError: Si la contraseña actual es incorrecta o la nueva no cumple la política.
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False

        if not PasswordManager.verify_password(contraseña_actual, usuario.password):
            raise ValueError("La contraseña actual es incorrecta")

        es_valida, mensaje = PasswordManager.validate_password_strength(
            nueva_contraseña
        )
        if not es_valida:
            raise ValueError(f"Nueva contraseña inválida: {mensaje}")

        usuario.password = PasswordManager.hash_password(nueva_contraseña)
        self.db.commit()
        return True

    def actualizar_usuario(self, usuario_id: UUID, **kwargs) -> Optional[USUARIOS]:
        """
        Actualiza un usuario con validaciones y normalización.
        Campos soportados (si existen): nombre, apellido, email, password, numero_documento,
        id_rol, id_tipo_documento, id_sexo, activo.

        Args:
            usuario_id: UUID del usuario.
            **kwargs: Campos a actualizar.

        Returns:
            Instancia actualizada de USUARIOS, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return None

        if "email" in kwargs and kwargs["email"] is not None:
            email = kwargs["email"]
            if not self._validar_email(email):
                raise ValueError("Email inválido")
            existente = self.obtener_usuario_por_email(email)
            if existente and getattr(existente, "id", None) != usuario_id:
                raise ValueError("El email ya está registrado")
            kwargs["email"] = email.lower().strip()

        if "password" in kwargs and kwargs["password"] is not None:
            pw = kwargs.pop("password")
            es_valida, mensaje = PasswordManager.validate_password_strength(pw)
            if not es_valida:
                raise ValueError(f"Contraseña inválida: {mensaje}")
            kwargs["password"] = PasswordManager.hash_password(pw)

        if "numero_documento" in kwargs and kwargs["numero_documento"] is not None:
            numero = kwargs["numero_documento"]
            if not self._validar_numero_documento(numero):
                raise ValueError("Número de documento inválido")
            existente_doc = (
                self.db.query(USUARIOS)
                .filter(USUARIOS.numero_documento == numero.strip())
                .first()
            )
            if existente_doc and getattr(existente_doc, "id", None) != usuario_id:
                raise ValueError("El número de documento ya está registrado")
            kwargs["numero_documento"] = numero.strip()

        if "id_rol" in kwargs and kwargs["id_rol"] is not None:
            if self.db.get(Roles, kwargs["id_rol"]) is None:
                raise ValueError("El rol especificado no existe")

        if "id_tipo_documento" in kwargs and kwargs["id_tipo_documento"] is not None:
            if self.db.get(Tipo_documento, kwargs["id_tipo_documento"]) is None:
                raise ValueError("El tipo de documento especificado no existe")

        if "id_sexo" in kwargs and kwargs["id_sexo"] is not None:
            if self.db.get(Sexo, kwargs["id_sexo"]) is None:
                raise ValueError("El sexo especificado no existe")

        for key, value in kwargs.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)

        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def eliminar_usuario(self, usuario_id: UUID) -> bool:
        """
        Desactiva (soft delete) un usuario por su ID si el modelo soporta 'activo'.
        Si no soporta 'activo', realiza borrado físico.
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False
        if hasattr(usuario, "activo"):
            usuario.activo = False
            self.db.commit()
            self.db.refresh(usuario)
            return True
        self.db.delete(usuario)
        self.db.commit()
        return True

    def desactivar_usuario(self, usuario_id: UUID) -> Optional[USUARIOS]:
        """
        Desactiva un usuario (soft delete) si el modelo soporta el campo 'activo'.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            Instancia de USUARIOS desactivada, o None si no existe.
        """
        if not hasattr(USUARIOS, "activo"):
            return self.obtener_usuario(usuario_id)
        return self.actualizar_usuario(usuario_id, activo=False)

    def obtener_usuarios_admin(self) -> List[USUARIOS]:
        """
        Obtiene todos los usuarios con privilegios de administrador.

        Returns:
            Lista de instancias de USUARIOS con es_admin=True.
        """
        return (
            self.db.query(USUARIOS)
            .join(Roles, Roles.id == USUARIOS.id_rol)
            .filter(Roles.nombre.ilike("admin"))
            .all()
        )

    def es_admin(self, usuario_id: UUID) -> bool:
        """
        Indica si un usuario es administrador.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            True si es administrador, False en caso contrario.
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False
        rol = self.db.get(Roles, getattr(usuario, "id_rol", None))
        return bool(rol and (rol.nombre or "").strip().lower() == "admin")

    def obtener_admin_por_defecto(self) -> Optional[USUARIOS]:
        """
        Obtiene el usuario administrador por defecto.

        Returns:
            Instancia de USUARIOS con email 'admin@system.com' y es_admin=True, o None.
        """
        return (
            self.db.query(USUARIOS)
            .join(Roles, Roles.id == USUARIOS.id_rol)
            .filter(USUARIOS.email == "admin@system.com", Roles.nombre.ilike("admin"))
            .first()
        )
