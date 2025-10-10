"""
API de Carritos - Endpoints para gestión de carritos
"""

from crud.compras.carritos_crud import CarritoCRUD
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from crud.compras.carritos_crud import (
    get_carrito,
    get_carrito_activo_usuario,
    get_or_create_carrito_activo,
    list_carritos_usuario,
    cerrar_carrito,
    update_carrito,
)
from schemas import CarritoResponse, RespuestaAPI

router = APIRouter(prefix="/carritos", tags=["carritos"])


@router.get("/", response_model=List[CarritoResponse])
async def obtener_carritos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los carritos con paginación."""
    try:
        carrito_crud = CarritoCRUD(db)
        carritos = carrito_crud.obtener_carritos(skip=skip, limit=limit)
        return carritos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carritos: {str(e)}",
        )


@router.get("/{carrito_id}", response_model=CarritoResponse)
async def obtener_carrito(carrito_id: UUID, db: Session = Depends(get_db)):
    """Obtener un carrito por ID."""
    try:
        carrito_crud = CarritoCRUD(db)
        carrito = carrito_crud.obtener_carrito(carrito_id)
        if not carrito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )
        return carrito
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carrito: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[CarritoResponse])
async def listar_carritos_usuario(
    usuario_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los carritos de un usuario con paginación."""
    try:
        return list_carritos_usuario(db, usuario_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar carritos: {str(e)}"
        )


@router.patch("/{carrito_id}/cerrar", response_model=CarritoResponse)
async def cerrar(carrito_id: UUID, db: Session = Depends(get_db)):
    try:
        """Inactivar Carrito."""
        inactivar_carrito = cerrar_carrito(db, carrito_id)
        if not inactivar_carrito:
            raise HTTPException(status_code=404, detail="Carrito no encontrado")
        return inactivar_carrito
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al inactivar carrito: {str(e)}"
        )


@router.post("/", response_model=CarritoResponse, status_code=status.HTTP_201_CREATED)
async def crear_carrito(carrito_data: CarritoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo carrito."""
    try:
        carrito_crud = CarritoCRUD(db)

        carrito = carrito_crud.crear_carrito(
            nombre=carrito_data.nombre,
            descripcion=carrito_data.descripcion,
            precio=carrito_data.precio,
            stock=carrito_data.stock,
            categoria_id=carrito_data.categoria_id,
            usuario_id=carrito_data.usuario_id,
        )
        return carrito
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear carrito: {str(e)}",
        )


@router.put("/{carrito_id}", response_model=CarritoResponse)
async def actualizar_carrito(
    carrito_id: UUID, carrito_data: CarritoUpdate, db: Session = Depends(get_db)
):
    """Actualizar un carrito existente."""
    try:
        carrito_crud = CarritoCRUD(db)

        carrito_existente = carrito_crud.obtener_carrito(carrito_id)
        if not carrito_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in carrito_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return carrito_existente

        carrito_actualizado = carrito_crud.actualizar_carrito(
            carrito_id, **campos_actualizacion
        )
        return carrito_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar carrito: {str(e)}",
        )


@router.delete("/{carrito_id}", response_model=RespuestaAPI)
async def eliminar_carrito(carrito_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un carrito."""
    try:
        carrito_crud = CarritoCRUD(db)

        carrito_existente = carrito_crud.obtener_carrito(carrito_id)
        if not carrito_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )

        carrito_eliminado = carrito_crud.eliminar_carrito(carrito_id)
        if carrito_eliminado:
            return RespuestaAPI(mensaje="Carrito eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar carrito",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar carrito: {str(e)}",
        )
