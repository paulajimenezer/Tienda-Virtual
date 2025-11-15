"""
API de los Items del Carrito - Endpoints para gestión de los ítems del carrito
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud.compras.carrito_items_crud import CarritoItemsCRUD
from database.config import get_db
from Entities.carrito_items import (
    CarritoItemCreate,
    CarritoItemResponse,
    CarritoItemUpdate,
)
from schemas import RespuestaAPI
from auth.jwt_utils import get_current_user

router = APIRouter(
    prefix="/api/carrito-items",
    tags=["carrito_items"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[CarritoItemResponse])
async def obtener_carrito_items(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los ítems del carrito con paginación."""
    try:
        carrito_items_crud = CarritoItemsCRUD(db)
        items = carrito_items_crud.obtener_items(skip=skip, limit=limit)
        return items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ítems del carrito: {str(e)}",
        )


@router.get("/{item_id}", response_model=CarritoItemResponse)
async def obtener_item(item_id: UUID, db: Session = Depends(get_db)):
    """Obtener un ítem del carrito por ID."""
    try:
        carrito_items_crud = CarritoItemsCRUD(db)
        item = carrito_items_crud.obtener_item(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado"
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ítem: {str(e)}",
        )


@router.post(
    "/", response_model=CarritoItemResponse, status_code=status.HTTP_201_CREATED
)
async def crear_item(item_data: CarritoItemCreate, db: Session = Depends(get_db)):
    """Crear un nuevo ítem del carrito."""
    try:
        carrito_items_crud = CarritoItemsCRUD(db)

        item = carrito_items_crud.crear_item(
            id_carrito=item_data.id_carrito,
            id_producto=item_data.id_producto,
            cantidad=item_data.cantidad,
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear ítem: {str(e)}",
        )


@router.put("/{item_id}", response_model=CarritoItemResponse)
async def actualizar_item(
    item_id: UUID, carrito_item_data: CarritoItemUpdate, db: Session = Depends(get_db)
):
    try:
        if carrito_item_data.cantidad is None:
            raise HTTPException(status_code=400, detail="Digite una cantidad válida")

        carrito_items_crud = CarritoItemsCRUD(db)
        obj = carrito_items_crud.actualizar_item_cantidad(
            item_id,
            cantidad=carrito_item_data.cantidad,
            id_usuario_edita=getattr(carrito_item_data, "id_usuario_edita", None),
        )
        if not obj:
            raise HTTPException(status_code=404, detail="Ítem no encontrado")
        return obj
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar ítem: {str(e)}",
        )


@router.delete("/{carrito_items_id}", response_model=RespuestaAPI)
async def eliminar_item(carrito_items_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un ítem del carrito."""
    try:
        carrito_items_crud = CarritoItemsCRUD(db)

        item_existente = carrito_items_crud.obtener_item(carrito_items_id)
        if not item_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado"
            )

        item_eliminado = carrito_items_crud.eliminar_item(carrito_items_id)
        if item_eliminado:
            return RespuestaAPI(mensaje="Ítem eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar ítem",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar ítem: {str(e)}",
        )
