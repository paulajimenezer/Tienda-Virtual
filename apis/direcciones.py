"""
API de Direcciones - Endpoints para gestión de direcciones
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud.usuarios.direcciones_crud import DireccionCRUD
from database.config import get_db
from Entities.direcciones import DireccionCreate, DireccionResponse, DireccionUpdate
from schemas import RespuestaAPI
from auth.jwt_utils import get_current_user

router = APIRouter(
    prefix="/direcciones",
    tags=["direcciones"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[DireccionResponse])
async def obtener_direcciones(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todas las direcciones con paginación."""
    try:
        direccion_crud = DireccionCRUD(db)
        direcciones = direccion_crud.obtener_direcciones(skip=skip, limit=limit)
        return direcciones

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener direcciones: {str(e)}",
        )


@router.get("/{direccion_id}", response_model=DireccionResponse)
async def obtener_direccion(direccion_id: UUID, db: Session = Depends(get_db)):
    """Obtener una dirección por ID."""
    try:
        direccion_crud = DireccionCRUD(db)
        direccion = direccion_crud.obtener_direccion(direccion_id)
        if not direccion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dirección no encontrada"
            )
        return direccion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la dirección: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[DireccionResponse])
async def obtener_direcciones_por_usuario(
    usuario_id: UUID, db: Session = Depends(get_db)
):
    """Obtener dirección por usuario."""
    try:
        direccion_crud = DireccionCRUD(db)
        direcciones = direccion_crud.obtener_direcciones_por_usuario(usuario_id)
        return direcciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las direcciones del usuario: {str(e)}",
        )


@router.get("/buscar/{nombre_direccion}", response_model=List[DireccionResponse])
async def buscar_direccion_por_nombre(nombre: str, db: Session = Depends(get_db)):
    """Buscar direcciones por nombre (búsqueda parcial)."""
    try:
        direccion_crud = DireccionCRUD(db)
        direcciones = direccion_crud.buscar_direccion_por_nombre(nombre)
        return direcciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar direcciones: {str(e)}",
        )


@router.post("/", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
async def crear_direccion(
    direccion_data: DireccionCreate, db: Session = Depends(get_db)
):
    """Crear un nueva dirección."""
    try:
        direccion_crud = DireccionCRUD(db)

        direccion = direccion_crud.crear_direccion(
            id_usuario=direccion_data.id_usuario,
            direccion=direccion_data.direccion,
            ciudad=direccion_data.ciudad,
            departamento=getattr(direccion_data, "departamento", ""),
            pais=direccion_data.pais,
            id_usuario_crea=getattr(direccion_data, "id_usuario_crea", None),
        )
        return direccion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear dirección: {str(e)}",
        )


@router.put("/{direccion_id}", response_model=DireccionResponse)
async def actualizar_direccion(
    direccion_id: UUID, direccion_data: DireccionUpdate, db: Session = Depends(get_db)
):
    """Actualizar una dirección existente."""
    try:
        direccion_crud = DireccionCRUD(db)
        direccion_existente = direccion_crud.obtener_direccion(direccion_id)
        if not direccion_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dirección no encontrada"
            )

        campos_actualizacion = {
            k: v for k, v in direccion_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return direccion_existente

        direccion_actualizada = direccion_crud.actualizar_direccion(
            direccion_id, **campos_actualizacion
        )
        return direccion_actualizada

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la dirección: {str(e)}",
        )


@router.delete("/{direccion_id}", response_model=RespuestaAPI)
async def eliminar_direccion(direccion_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una dirección."""
    try:
        direccion_crud = DireccionCRUD(db)
        direccion_existente = direccion_crud.obtener_direccion(direccion_id)

        if not direccion_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dirección no encontrada"
            )

        direccion_eliminada = direccion_crud.eliminar_direccion(direccion_id)
        if direccion_eliminada:
            return RespuestaAPI(mensaje="Dirección eliminada exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la dirección",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar dirección: {str(e)}",
        )
