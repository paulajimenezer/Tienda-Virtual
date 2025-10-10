"""
API de Roles - Endpoints para gestión de roles
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud.estandarizacion.roles_crud import RolCRUD
from database.config import get_db
from schemas import RespuestaAPI

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RolesResponse])
async def obtener_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todos los roles con paginación."""
    try:
        rol_crud = RolCRUD(db)
        roles = rol_crud.obtener_roles(skip=skip, limit=limit)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener roles: {str(e)}",
        )


@router.get("/{rol_id}", response_model=RolesResponse)
async def obtener_rol(rol_id: UUID, db: Session = Depends(get_db)):
    """Obtener un rol por ID."""
    try:
        rol_crud = RolCRUD(db)
        rol = rol_crud.obtener_rol(rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )
        return rol
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rol: {str(e)}",
        )


@router.get("/buscar/{nombre}", response_model=List[RolesResponse])
async def buscar_roles_por_nombre(nombre: str, db: Session = Depends(get_db)):
    """Buscar roles por nombre (búsqueda parcial)."""
    try:
        rol_crud = RolCRUD(db)
        roles = rol_crud.buscar_roles_por_nombre(nombre)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar roles: {str(e)}",
        )


@router.post("/", response_model=RolesResponse, status_code=status.HTTP_201_CREATED)
async def crear_rol(rol_data: RolesCreate, db: Session = Depends(get_db)):
    """Crear un nuevo rol."""
    try:
        rol_crud = RolCRUD(db)

        rol = rol_crud.crear_rol(
            nombre=rol_data.nombre,
            descripcion=rol_data.descripcion,
            permisos=rol_data.permisos,
        )
        return rol
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear rol: {str(e)}",
        )


@router.delete("/{rol_id}", response_model=RespuestaAPI)
async def eliminar_rol(rol_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un rol."""
    try:
        rol_crud = RolCRUD(db)

        rol_existente = rol_crud.obtener_rol(rol_id)
        if not rol_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )

        rol_eliminado = rol_crud.eliminar_rol(rol_id)
        if rol_eliminado:
            return RespuestaAPI(mensaje="Rol eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar rol",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar rol: {str(e)}",
        )
