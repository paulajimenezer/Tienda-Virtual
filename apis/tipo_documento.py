"""
API de Tipo de Documento - Endpoints para gestión de tipos de documento
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.jwt_utils import get_current_user
from crud.estandarizacion.tipo_documento_crud import TipoDocumentoCRUDCRUD
from database.config import get_db
from schemas import (
    RespuestaAPI,
    TipoDocumentoCreate,
    TipoDocumentoResponse,
    TipoDocumentoUpdate,
)

router = APIRouter(
    prefix="/tipo_documento",
    tags=["tipo_documento"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[TipoDocumentoResponse])
async def obtener_tipos_documento(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los tipos de documento con paginación."""
    try:
        tipo_documento_crud = TipoDocumentoCRUDCRUD(db)
        tipos_documento = tipo_documento_crud.obtener_tipos_documento(
            skip=skip, limit=limit
        )
        return tipos_documento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipos de documento: {str(e)}",
        )


@router.get("/{tipo_documento_id}", response_model=TipoDocumentoResponse)
async def obtener_tipo_documento(
    tipo_documento_id: UUID, db: Session = Depends(get_db)
):
    """Obtener un tipo de documento por ID."""
    try:
        tipo_documento_crud = TipoDocumentoCRUDCRUD(db)
        tipo_documento = tipo_documento_crud.obtener_tipo_documento(tipo_documento_id)
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )
        return tipo_documento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipo de documento: {str(e)}",
        )


@router.post(
    "/", response_model=TipoDocumentoResponse, status_code=status.HTTP_201_CREATED
)
async def crear_tipo_documento(
    tipo_documento_data: TipoDocumentoCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo tipo de documento."""
    try:
        tipo_documento_crud = TipoDocumentoCRUDCRUD(db)

        tipo_documento = tipo_documento_crud.crear_tipo_documento(
            nombre=tipo_documento_data.nombre,
            descripcion=tipo_documento_data.descripcion,
            permisos=tipo_documento_data.permisos,
        )
        return tipo_documento
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el tipo de documento: {str(e)}",
        )


@router.delete("/{tipo_documento_id}", response_model=RespuestaAPI)
async def eliminar_tipo_documento(
    tipo_documento_id: UUID, db: Session = Depends(get_db)
):
    """Eliminar un tipo de documento."""
    try:
        tipo_documento_crud = TipoDocumentoCRUDCRUD(db)

        tipo_documento_existente = tipo_documento_crud.obtener_tipo_documento(
            tipo_documento_id
        )
        if not tipo_documento_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )

        tipo_documento_eliminado = tipo_documento_crud.eliminar_tipo_documento(
            tipo_documento_id
        )
        if tipo_documento_eliminado:
            return RespuestaAPI(
                mensaje="Tipo de documento eliminado exitosamente", exito=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar tipo de documento",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo de documento: {str(e)}",
        )
