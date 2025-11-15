"""
API de Autenticación - Endpoints para login y autenticación
"""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from crud.usuarios.usuario_crud import UsuarioCRUD
from database.config import get_db
from schemas import RespuestaAPI, UsuarioLogin, UsuarioResponse
from auth.jwt_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["autenticación"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


def _authenticate_and_build_response(
    email: str, password: str, db: Session
) -> TokenResponse:
    usuario_crud = UsuarioCRUD(db)
    usuario = usuario_crud.autenticar_usuario(email, password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo",
        )

    usuario_schema = UsuarioResponse.from_orm(usuario)
    es_admin = usuario_crud.es_admin(usuario.id)
    rol_valor: str = "admin" if es_admin else "cliente"

    access_token = create_access_token(
        {
            "sub": str(usuario.id),
            "email": usuario.email,
            "rol": rol_valor,
            "es_admin": es_admin,
        },
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=access_token, usuario=usuario_schema)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """Autenticar un usuario con email y contraseña."""
    try:
        return _authenticate_and_build_response(
            login_data.email, login_data.password, db
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el login: {str(e)}",
        )


@router.post("/token", response_model=TokenResponse)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autenticar un usuario usando el flujo de password grant de OAuth2."""
    return _authenticate_and_build_response(form_data.username, form_data.password, db)


@router.post("/crear-admin", response_model=RespuestaAPI)
async def crear_usuario_admin(db: Session = Depends(get_db)):
    """Crear usuario administrador por defecto."""
    try:
        usuario_crud = UsuarioCRUD(db)
        admin_existente = usuario_crud.obtener_admin_por_defecto()
        if admin_existente:
            return RespuestaAPI(
                mensaje="Ya existe un usuario administrador por defecto",
                exito=True,
                datos={"admin_id": str(admin_existente.id)},
            )

        # Buscar rol 'Admin' y un tipo de documento disponible
        from auth.security import PasswordManager
        from Entities.roles import Roles
        from Entities.tipo_documento import Tipo_documento

        rol_admin = db.query(Roles).filter(Roles.nombre.ilike("admin")).first()
        if not rol_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existe un rol 'Admin'. Créelo antes de continuar.",
            )

        tipo_doc = db.query(Tipo_documento).first()
        if not tipo_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existen tipos de documento. Créelos antes de continuar.",
            )

        contraseña_admin = PasswordManager.generate_secure_password(12)

        admin = usuario_crud.crear_usuario(
            nombre="Administrador",
            apellido="Sistema",
            email="admin@system.com",
            password=contraseña_admin,
            numero_documento="9999999",
            id_rol=rol_admin.id,
            id_tipo_documento=tipo_doc.id,
        )

        return RespuestaAPI(
            mensaje="Usuario administrador creado exitosamente",
            exito=True,
            datos={
                "admin_id": str(admin.id),
                "contraseña_temporal": contraseña_admin,
                "mensaje": "IMPORTANTE: Cambie esta contraseña en su primer inicio de sesión",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear administrador: {str(e)}",
        )


@router.get("/verificar/{usuario_id}", response_model=RespuestaAPI)
async def verificar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Verificar si un usuario existe y está activo."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_usuario(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        return RespuestaAPI(
            mensaje="Usuario verificado exitosamente",
            exito=True,
            datos={
                "usuario_id": str(usuario.id),
                "nombre": usuario.nombre,
                "email": usuario.email,
                "activo": usuario.activo,
                "es_admin": UsuarioCRUD(db).es_admin(usuario_id),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar usuario: {str(e)}",
        )


@router.get("/estado", response_model=RespuestaAPI)
async def estado_autenticacion():
    """Verificar el estado del sistema de autenticación."""
    return RespuestaAPI(
        mensaje="Sistema de autenticación funcionando correctamente",
        exito=True,
        datos={
            "sistema": "Sistema de Gestión de Productos",
            "version": "1.0.0",
            "autenticacion": "Activa",
        },
    )


@router.get("/me", response_model=UsuarioResponse)
async def read_current_user(usuario_actual=Depends(get_current_user)):
    return UsuarioResponse.from_orm(usuario_actual)
