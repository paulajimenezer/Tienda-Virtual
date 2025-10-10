"""
API de Descuentos - Endpoints para gestión de descuentos
"""

from typing import List, Optional
from uuid import UUID
from crud.compras.descuentos_crud import DescuentosCRUD
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.config import get_db
from schemas import RespuestaAPI
from Entities.descuentos import DescuentoCreate, DescuentoResponse, DescuentoUpdate

router = APIRouter(prefix="/descuentos", tags=["descuentos"])


@router.get("/", response_model=List[DescuentoResponse])
async def obtener_descuentos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los descuentos con paginación."""
    try:
        descuentos_crud = DescuentosCRUD(db)
        descuentos = descuentos_crud.obtener_descuentos(skip=skip, limit=limit)
        return descuentos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener descuentos: {str(e)}",
        )


@router.get("/{descuento_id}", response_model=DescuentoResponse)
async def obtener_descuento(descuento_id: UUID, db: Session = Depends(get_db)):
    """Obtener un descuento por ID."""
    try:
        descuentos_crud = DescuentosCRUD(db)
        descuento = descuentos_crud.obtener_descuento(descuento_id)
        if not descuento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Descuento no encontrado"
            )
        return descuento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener descuento: {str(e)}",
        )


@router.get("/{descuento_codigo}", response_model=DescuentoResponse)
async def obtener_descuento(descuento_codigo: str, db: Session = Depends(get_db)):
    """Obtener un descuento por código."""
    try:
        descuentos_crud = DescuentosCRUD(db)
        descuento = descuentos_crud.obtener_descuento(descuento_codigo)
        if not descuento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Descuento no encontrado"
            )
        return descuento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener descuento: {str(e)}",
        )


@router.get("/validar/{codigo}", response_model=DescuentoResponse)
async def validar(
    codigo: str, fecha: Optional[datetime] = Query(None), db: Session = Depends(get_db)
):
    try:
        descuentos_crud = DescuentosCRUD(db)
        validacion_codigo = descuentos_crud.validar_codigo(db, codigo, en_fecha=fecha)
        if not validacion_codigo:
            raise HTTPException(status_code=404, detail="Descuento no válido")
        return validacion_codigo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al validar descuento: {str(e)}"
        )


@router.post("/", response_model=DescuentoResponse, status_code=status.HTTP_201_CREATED)
async def crear_descuento(
    descuento_data: DescuentoCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo descuento."""
    try:
        descuentos_crud = DescuentosCRUD(db)

        descuento = descuentos_crud.crear_descuento(
            codigo=descuento_data.codigo,
            porcentaje=descuento_data.porcentaje,
            fecha_inicio=descuento_data.fecha_inicio,
            fecha_fin=descuento_data.fecha_fin,
            activo=getattr(descuento_data, "activo", True),
            id_usuario_crea=descuento_data.id_usuario_crea,
        )
        return descuento
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear descuento: {str(e)}",
        )


@router.put("/{descuento_id}", response_model=DescuentoResponse)
async def actualizar_descuento(
    descuento_id: UUID, descuento_data: DescuentoUpdate, db: Session = Depends(get_db)
):
    """Actualizar un descuento existente."""
    try:
        descuentos_crud = DescuentosCRUD(db)

        descuento_existente = descuentos_crud.obtener_descuento(descuento_id)
        if not descuento_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Descuento no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in descuento_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return descuento_existente

        descuento_actualizado = descuentos_crud.actualizar_descuento(
            descuento_id, **campos_actualizacion
        )
        return descuento_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar descuento: {str(e)}",
        )


@router.delete("/{descuento_id}", response_model=RespuestaAPI)
async def eliminar_descuento(descuento_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un descuento."""
    try:
        descuentos_crud = DescuentosCRUD(db)

        descuento_existente = descuentos_crud.obtener_descuento(descuento_id)
        if not descuento_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Descuento no encontrado"
            )

        descuento_eliminado = descuentos_crud.eliminar_descuento(descuento_id)
        if descuento_eliminado:
            return RespuestaAPI(mensaje="Descuento eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar descuento",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar descuento: {str(e)}",
        )
