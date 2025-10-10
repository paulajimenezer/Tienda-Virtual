"""
API de Sexo - Endpoints para gestión de sexo
"""

from typing import List
from uuid import UUID

from crud.estandarizacion.sexo_crud import SexoCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas import SexoCreate, SexoResponse, SexoUpdate, RespuestaAPI
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sexo", tags=["sexo"])


@router.get("/", response_model=List[SexoResponse])
async def obtener_sexos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todos los sexos con paginación."""
    try:
        sexo_crud = SexoCRUD(db)
        sexos = sexo_crud.obtener_sexos(skip=skip, limit=limit)
        return sexos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sexos: {str(e)}",
        )


@router.get("/{sexo_id}", response_model=SexoResponse)
async def obtener_sexo(sexo_id: UUID, db: Session = Depends(get_db)):
    """Obtener un sexo por ID."""
    try:
        sexo_crud = SexoCRUD(db)
        sexo = sexo_crud.obtener_sexo(sexo_id)
        if not sexo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sexo no encontrado"
            )
        return sexo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sexo: {str(e)}",
        )


@router.post("/", response_model=SexoResponse, status_code=status.HTTP_201_CREATED)
async def crear_sexo(sexo_data: SexoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo sexo."""
    try:
        sexo_crud = SexoCRUD(db)

        sexo = sexo_crud.crear_sexo(
            nombre=sexo_data.nombre,
            descripcion=sexo_data.descripcion,
            permisos=sexo_data.permisos,
        )
        return sexo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear sexo: {str(e)}",
        )


@router.delete("/{sexo_id}", response_model=RespuestaAPI)
async def eliminar_sexo(sexo_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un sexo."""
    try:
        sexo_crud = SexoCRUD(db)

        sexo_existente = sexo_crud.obtener_sexo(sexo_id)
        if not sexo_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sexo no encontrado"
            )

        sexo_eliminado = sexo_crud.eliminar_sexo(sexo_id)
        if sexo_eliminado:
            return RespuestaAPI(mensaje="Sexo eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar sexo",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar sexo: {str(e)}",
        )
