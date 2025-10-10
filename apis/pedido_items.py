"""
API de Pedidos - Endpoints para gestión de pedidos
"""

from typing import List
from uuid import UUID

from crud.pedidos.pedido_items_crud import PedidoItemCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import RespuestaAPI
from Entities.pedido_items import PedidoItemCreate, PedidoItemResponse, PedidoItemUpdate

router = APIRouter(prefix="/pedido-items", tags=["pedido_items"])


@router.get("/{item_id}", response_model=PedidoItemResponse)
async def obtener_pedido_item(item_id: UUID, db: Session = Depends(get_db)):
    """Obtener un ítem de pedido por ID."""
    try:
        item_pedido_crud = PedidoItemCRUD(db)
        item = item_pedido_crud.obtener_pedido_item(item_id)
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


@router.get("/pedido/{pedido_id}", response_model=List[PedidoItemResponse])
async def listar_items(
    pedido_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    try:
        return PedidoItemCRUD(db).listar_items(pedido_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar ítems: {str(e)}")


@router.post(
    "/", response_model=PedidoItemResponse, status_code=status.HTTP_201_CREATED
)
async def crear_item(pedido_item_data: PedidoItemCreate, db: Session = Depends(get_db)):
    """Crear un nuevo ítem de pedido."""
    try:
        pedido_item_crud = PedidoItemCRUD(db)

        item = pedido_item_crud.crear_pedido_item(
            id_pedido=pedido_item_data.id_pedido,
            id_producto=pedido_item_data.id_producto,
            cantidad=pedido_item_data.cantidad,
            precio_unitario=getattr(pedido_item_data, "precio_unitario", None),
            id_usuario_crea=getattr(pedido_item_data, "id_usuario_crea", None),
        )
        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear ítem: {str(e)}",
        )


@router.put("/{item_id}", response_model=PedidoItemResponse)
async def actualizar_item(
    item_id: UUID, pedido_item_data: PedidoItemUpdate, db: Session = Depends(get_db)
):
    """Actualizar un ítem existente."""
    try:
        item_pedido_crud = PedidoItemCRUD(db)

        item_existente = item_pedido_crud.obtener_pedido_item(item_id)
        if not item_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in pedido_item_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return item_existente

        item_actualizado = item_pedido_crud.actualizar_pedido_item(
            item_id, **campos_actualizacion
        )
        return item_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el ítem: {str(e)}",
        )


@router.delete("/{pedido_item_id}", response_model=RespuestaAPI)
async def eliminar_item(pedido_item_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un ítem de pedido."""
    try:
        item_pedido_crud = PedidoItemCRUD(db)

        item_existente = item_pedido_crud.obtener_pedido_item(pedido_item_id)
        if not item_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado"
            )

        item_eliminado = item_pedido_crud.eliminar_pedido_item(pedido_item_id)
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
