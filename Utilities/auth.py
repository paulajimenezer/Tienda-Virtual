"""
Módulo de autenticación para Tienda Virtual.

Proporciona funciones para login de usuarios y detección de rol admin.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from Entities.usuarios import Usuarios
from Entities.roles import Roles
from Entities.sexo import Sexo
from Entities.tipo_documento import Tipo_documento


def _is_admin(user: Usuarios) -> bool:
    """
    Determina si el usuario tiene rol de administrador.

    Args:
        user: Instancia de Usuarios.

    Returns:
        True si el usuario es admin, False en caso contrario.
    """
    try:
        rol = getattr(user, "rol", None)
        nombre = getattr(rol, "nombre", "") or ""
        return nombre.strip().lower() == "admin"
    except Exception:
        return False


def login_prompt(db: Session, max_intentos: int = 3) -> Tuple[Optional[Usuarios], bool]:
    """
    Solicita email y password, valida contra la BD y retorna (usuario, is_admin).
    Retorna (None, False) al fallar.

    Args:
        db: Sesión de base de datos.
        max_intentos: Número máximo de intentos permitidos.

    Returns:
        (usuario, is_admin): usuario autenticado y si es admin.
    """
    for _ in range(max_intentos):
        print("\n--- Login ---")
        email = input("Email: ").strip().lower()
        password = input("Password: ").strip()
        if not email or not password:
            print("Credenciales inválidas.")
            continue

        user = (
            db.query(Usuarios)
            .filter(
                Usuarios.email == email,
                Usuarios.password == password,
                Usuarios.activo == True,
            )
            .first()
        )
        if user:
            return user, _is_admin(user)
        print("Usuario o contraseña incorrectos.")
    return None, False


def register_client_prompt(db: Session) -> Optional[Usuarios]:
    """
    Registro interactivo de cuenta cliente.

    Solicita datos mínimos y crea un usuario con rol 'cliente'.

    Reglas:
    - Email único.
    - Número de documento único.
    - Asigna sexo 'O' y tipo documento 'CC' por defecto si existen.

    Returns:
        Usuario creado o None si falló/abortó.
    """
    print("\n--- Crear cuenta (Cliente) ---")
    nombre = input("Nombre: ").strip()
    apellido = input("Apellido: ").strip()
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()
    numero_documento = input("Número de documento: ").strip()
    if not all([nombre, apellido, email, password, numero_documento]):
        print("Todos los campos son obligatorios.")
        return None

    if db.query(Usuarios).filter(Usuarios.email == email).first():
        print("El email ya está registrado.")
        return None
    if db.query(Usuarios).filter(Usuarios.numero_documento == numero_documento).first():
        print("El número de documento ya está registrado.")
        return None

    rol_cliente = db.query(Roles).filter(Roles.nombre.ilike("cliente")).first()
    if not rol_cliente:
        print("No existe el rol 'cliente'. Contacte al administrador.")
        return None

    sexo = db.query(Sexo).filter(Sexo.codigo == "O").first()
    tipo_doc = db.query(Tipo_documento).filter(Tipo_documento.nombre == "CC").first()

    user = Usuarios(
        nombre=nombre,
        apellido=apellido,
        email=email,
        password=password,
        id_sexo=getattr(sexo, "id", None),
        id_tipo_documento=getattr(tipo_doc, "id", None),
        numero_documento=numero_documento,
        id_rol=rol_cliente.id,
        activo=True,
        id_usuario_crea=None,
        id_usuario_edita=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Cuenta creada correctamente. Ya puede iniciar sesión.")
    return user
