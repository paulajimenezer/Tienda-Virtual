"""
Operaciones CRUD y utilidades para la entidad Usuarios.

Incluye creación, consulta, actualización, eliminación, autenticación y gestión de contraseñas,
con validaciones de entrada y verificación de entidades normalizadoras (Roles, Sexo, Tipo_documento).
"""

import re
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from auth.security import PasswordManager
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
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email or "") is not None

    def _validar_telefono(self, telefono: str) -> bool:
        """
        Valida el formato internacional de un teléfono.

        Args:
            telefono: Teléfono a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        pattern = r"^\+?[\d\s\-\(\)]{7,15}$"
        return re.match(pattern, telefono or "") is not None

    def _validar_nombre_usuario(self, nombre_usuario: str) -> bool:
        """
        Valida el formato de nombre de usuario.

        Reglas: 3-20 caracteres, alfanumérico y guion bajo.

        Args:
            nombre_usuario: Nombre de usuario a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        pattern = r"^[a-zA-Z0-9_]{3,20}$"
        return re.match(pattern, nombre_usuario or "") is not None

    def _validar_numero_documento(self, numero: str) -> bool:
        """
        Valida que el número de documento tenga 7 o 10 dígitos numéricos.

        Args:
            numero: Número de documento a validar.

        Returns:
            True si el formato es válido, False en caso contrario.
        """
        numero = (numero or "").strip()
        return numero.isdigit() and len(numero) in (7, 10)

    def _get_pk(self, obj) -> Optional[UUID]:
        """
        Obtiene el valor de la clave primaria de un objeto.

        Devuelve el primer atributo encontrado entre 'id' o 'id_usuario'.

        Args:
            obj: Instancia del modelo.

        Returns:
            UUID de la clave primaria o None si no se encuentra.
        """
        return getattr(obj, "id", None) or getattr(obj, "id_usuario", None)

    def crear_usuario(
        self,
        nombre: str,
        nombre_usuario: str,
        email: str,
        contraseña: str,
        numero_documento: str,
        telefono: Optional[str] = None,
        es_admin: bool = False,
        rol_id: UUID = None,
        sexo_id: Optional[UUID] = None,
        tipo_documento_id: UUID = None,
    ) -> USUARIOS:
        """
        Crea un nuevo usuario con validaciones y normalización.

        Args:
            nombre: Nombre del usuario (máximo 100 caracteres).
            nombre_usuario: Identificador único (3-20 caracteres, alfanumérico y guion bajo).
            email: Correo electrónico válido y único.
            contraseña: Contraseña en texto plano que será hasheada.
            numero_documento: Número del documento.
            telefono: Teléfono opcional en formato internacional.
            es_admin: Indica si el usuario es administrador.
            rol_id: UUID de la entidad Roles (obligatorio).
            sexo_id: UUID de la entidad Sexo (opcional).
            tipo_documento_id: UUID de la entidad Tipo_documento (obligatorio).

        Returns:
            Instancia creada de USUARIOS.

        Raises:
            ValueError: Si los datos son inválidos o si los FKs no existen.
        """
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede exceder 100 caracteres")

        if not nombre_usuario or not self._validar_nombre_usuario(nombre_usuario):
            raise ValueError(
                "El nombre de usuario debe tener entre 3-20 caracteres y solo contener letras, números y guiones bajos"
            )
        if self.obtener_usuario_por_nombre_usuario(nombre_usuario):
            raise ValueError("El nombre de usuario ya está registrado")

        if not email or not self._validar_email(email):
            raise ValueError("Email inválido")
        if self.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")

        if not contraseña:
            raise ValueError("La contraseña es obligatoria")
        es_valida, mensaje = PasswordManager.validate_password_strength(contraseña)
        if not es_valida:
            raise ValueError(f"Contraseña inválida: {mensaje}")

        if not numero_documento or not self._validar_numero_documento(numero_documento):
            raise ValueError("Número de documento inválido")
        numero_documento = numero_documento.strip()

        if telefono:
            if not self._validar_telefono(telefono):
                raise ValueError("Formato de teléfono inválido")
            telefono = telefono.strip()

        if rol_id is None:
            raise ValueError("El rol es obligatorio")
        from Entities.roles import Roles

        if self.db.get(Roles, rol_id) is None:
            raise ValueError("El rol especificado no existe")

        if sexo_id is not None:
            from Entities.sexo import Sexo

            if self.db.get(Sexo, sexo_id) is None:
                raise ValueError("El sexo especificado no existe")

        if tipo_documento_id is None:
            raise ValueError("El tipo de documento es obligatorio")
        from Entities.tipo_documento import Tipo_documento

        if self.db.get(Tipo_documento, tipo_documento_id) is None:
            raise ValueError("El tipo de documento especificado no existe")

        if hasattr(USUARIOS, "numero_documento"):
            existente_doc = (
                self.db.query(USUARIOS)
                .filter(
                    USUARIOS.numero_documento == numero_documento,
                )
                .first()
            )
            if existente_doc:
                raise ValueError("El número de documento ya está registrado")

        contraseña_hash = PasswordManager.hash_password(contraseña)

        usuario = USUARIOS(
            nombre=nombre.strip(),
            nombre_usuario=nombre_usuario.strip().lower(),
            email=email.lower().strip(),
            contraseña_hash=contraseña_hash,
            telefono=telefono,
            es_admin=es_admin,
            **(
                {"numero_documento": numero_documento}
                if hasattr(USUARIOS, "numero_documento")
                else {}
            ),
        )

        if hasattr(usuario, "rol_id"):
            usuario.rol_id = rol_id
        if sexo_id is not None and hasattr(usuario, "sexo_id"):
            usuario.sexo_id = sexo_id
        if hasattr(usuario, "tipo_documento_id"):
            usuario.tipo_documento_id = tipo_documento_id

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

    def obtener_usuario_por_nombre_usuario(
        self, nombre_usuario: str
    ) -> Optional[USUARIOS]:
        """
        Obtiene un usuario a partir de su nombre de usuario.

        Args:
            nombre_usuario: Nombre de usuario.

        Returns:
            Instancia de USUARIOS si existe, None en caso contrario.
        """
        return (
            self.db.query(USUARIOS)
            .filter(USUARIOS.nombre_usuario == (nombre_usuario or "").lower().strip())
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

    def autenticar_usuario(
        self, nombre_usuario: str, contraseña: str
    ) -> Optional[USUARIOS]:
        """
        Autentica un usuario por nombre de usuario o email y contraseña.

        Args:
            nombre_usuario: Nombre de usuario o email.
            contraseña: Contraseña en texto plano.

        Returns:
            Instancia de USUARIOS si las credenciales son válidas, None en caso contrario.
        """
        usuario = self.obtener_usuario_por_nombre_usuario(nombre_usuario)
        if not usuario:
            usuario = self.obtener_usuario_por_email(nombre_usuario)
        if not usuario or (hasattr(usuario, "activo") and not usuario.activo):
            return None
        if PasswordManager.verify_password(contraseña, usuario.contraseña_hash):
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

        if not PasswordManager.verify_password(
            contraseña_actual, usuario.contraseña_hash
        ):
            raise ValueError("La contraseña actual es incorrecta")

        es_valida, mensaje = PasswordManager.validate_password_strength(
            nueva_contraseña
        )
        if not es_valida:
            raise ValueError(f"Nueva contraseña inválida: {mensaje}")

        usuario.contraseña_hash = PasswordManager.hash_password(nueva_contraseña)
        self.db.commit()
        return True

    def actualizar_usuario(self, usuario_id: UUID, **kwargs) -> Optional[USUARIOS]:
        """
        Actualiza un usuario con validaciones y normalización.
        Campos soportados (si existen): nombre, nombre_usuario, email, telefono,
        contraseña, activo, es_admin, rol_id (obligatorio si se envía), sexo_id,
        tipo_documento_id (obligatorio si se envía), numero_documento.

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

        if "email" in kwargs:
            email = kwargs["email"]
            if not self._validar_email(email):
                raise ValueError("Email inválido")
            existente = self.obtener_usuario_por_email(email)
            if existente and self._get_pk(existente) != usuario_id:
                raise ValueError("El email ya está registrado")
            kwargs["email"] = email.lower().strip()

        if "telefono" in kwargs and kwargs["telefono"]:
            if not self._validar_telefono(kwargs["telefono"]):
                raise ValueError("Formato de teléfono inválido")
            kwargs["telefono"] = kwargs["telefono"].strip()

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len((nombre or "").strip()) == 0:
                raise ValueError("El nombre es obligatorio")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")
            kwargs["nombre"] = nombre.strip()

        if "nombre_usuario" in kwargs:
            nombre_usuario = kwargs["nombre_usuario"]
            if not self._validar_nombre_usuario(nombre_usuario):
                raise ValueError(
                    "El nombre de usuario debe tener entre 3-20 caracteres y solo contener letras, números y guiones bajos"
                )
            existente = self.obtener_usuario_por_nombre_usuario(nombre_usuario)
            if existente and self._get_pk(existente) != usuario_id:
                raise ValueError("El nombre de usuario ya está registrado")
            kwargs["nombre_usuario"] = nombre_usuario.strip().lower()

        if "contraseña" in kwargs:
            contraseña = kwargs["contraseña"]
            es_valida, mensaje = PasswordManager.validate_password_strength(contraseña)
            if not es_valida:
                raise ValueError(f"Contraseña inválida: {mensaje}")
            kwargs["contraseña_hash"] = PasswordManager.hash_password(contraseña)
            del kwargs["contraseña"]

        if "rol_id" in kwargs:
            if kwargs["rol_id"] is None:
                raise ValueError("El rol no puede ser nulo")
            from Entities.roles import Roles

            if self.db.get(Roles, kwargs["rol_id"]) is None:
                raise ValueError("El rol especificado no existe")

        if "sexo_id" in kwargs and kwargs["sexo_id"] is not None:
            from Entities.sexo import Sexo

            if self.db.get(Sexo, kwargs["sexo_id"]) is None:
                raise ValueError("El sexo especificado no existe")

        if "tipo_documento_id" in kwargs:
            if kwargs["tipo_documento_id"] is None:
                raise ValueError("El tipo de documento no puede ser nulo")
            from Entities.tipo_documento import Tipo_documento

            if self.db.get(Tipo_documento, kwargs["tipo_documento_id"]) is None:
                raise ValueError("El tipo de documento especificado no existe")

        if "numero_documento" in kwargs:
            numero_documento = kwargs["numero_documento"]
            if not numero_documento or not self._validar_numero_documento(
                numero_documento
            ):
                raise ValueError("Número de documento inválido")
            numero_documento = numero_documento.strip()
            kwargs["numero_documento"] = numero_documento

            if hasattr(USUARIOS, "numero_documento"):
                existente_doc = (
                    self.db.query(USUARIOS)
                    .filter(
                        USUARIOS.numero_documento == numero_documento,
                    )
                    .first()
                )
                if existente_doc and self._get_pk(existente_doc) != usuario_id:
                    raise ValueError("El número de documento ya está registrado")

        for key, value in kwargs.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)

        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def eliminar_usuario(self, usuario_id: UUID) -> bool:
        """
        Elimina un usuario por su ID.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            True si se eliminó correctamente, False si no existe.
        """
        usuario = self.obtener_usuario(usuario_id)
        if not usuario:
            return False
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
        return self.db.query(USUARIOS).filter(USUARIOS.es_admin == True).all()

    def es_admin(self, usuario_id: UUID) -> bool:
        """
        Indica si un usuario es administrador.

        Args:
            usuario_id: UUID del usuario.

        Returns:
            True si es administrador, False en caso contrario.
        """
        usuario = self.obtener_usuario(usuario_id)
        return bool(getattr(usuario, "es_admin", False)) if usuario else False

    def obtener_admin_por_defecto(self) -> Optional[USUARIOS]:
        """
        Obtiene el usuario administrador por defecto.

        Returns:
            Instancia de USUARIOS con email 'admin@system.com' y es_admin=True, o None.
        """
        return (
            self.db.query(USUARIOS)
            .filter(USUARIOS.email == "admin@system.com", USUARIOS.es_admin == True)
            .first()
        )
