"""
API de Pedidos - Endpoints para gestión de pedidos
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud.pedidos.pedidos_crud import PedidoCRUD
from database.config import get_db
from Entities.pedidos import PedidoCreate, PedidoResponse, PedidoUpdate
from schemas import RespuestaAPI, PedidoEnriquecido
from auth.jwt_utils import get_current_user

router = APIRouter(
    prefix="/api/pedidos",
    tags=["pedidos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[PedidoEnriquecido])
async def obtener_pedidos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los pedidos con paginación. Respuesta enriquecida con usuario y items."""
    try:
        pedido_crud = PedidoCRUD(db)
        pedidos = pedido_crud.obtener_pedidos(skip=skip, limit=limit)

        results = []
        for p in pedidos:
            data = (
                p.to_dict()
                if hasattr(p, "to_dict")
                else {k: getattr(p, k) for k in p.__dict__}
            )
            usuario = getattr(p, "usuario", None)
            data["usuario"] = (
                usuario.to_dict()
                if usuario and hasattr(usuario, "to_dict")
                else (usuario.__dict__ if usuario else None)
            )
            items = getattr(p, "pedido_item", None)
            data["items"] = (
                [
                    it.to_dict() if hasattr(it, "to_dict") else it.__dict__
                    for it in items
                ]
                if items
                else []
            )
            direccion = getattr(p, "direccion", None)
            data["direccion"] = (
                direccion.to_dict()
                if direccion and hasattr(direccion, "to_dict")
                else (direccion.__dict__ if direccion else None)
            )
            results.append(data)
        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[PedidoEnriquecido])
async def obtener_pedidos_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Obtener pedidos por usuario (enriquecidos)."""
    try:
        pedido_crud = PedidoCRUD(db)
        pedidos = pedido_crud.obtener_pedidos_por_usuario(usuario_id)
        results = []
        for p in pedidos:
            data = (
                p.to_dict()
                if hasattr(p, "to_dict")
                else {k: getattr(p, k) for k in p.__dict__}
            )
            items = getattr(p, "pedido_item", None)
            data["items"] = (
                [
                    it.to_dict() if hasattr(it, "to_dict") else it.__dict__
                    for it in items
                ]
                if items
                else []
            )
            direccion = getattr(p, "direccion", None)
            data["direccion"] = (
                direccion.to_dict()
                if direccion and hasattr(direccion, "to_dict")
                else (direccion.__dict__ if direccion else None)
            )
            results.append(data)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos por usuario: {str(e)}",
        )


@router.get("/{pedido_id}", response_model=PedidoEnriquecido)
async def obtener_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Obtener un pedido por ID (enriquecido con usuario, items y dirección)."""
    try:
        pedido_crud = PedidoCRUD(db)
        pedido = pedido_crud.obtener_pedido(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        data = (
            pedido.to_dict()
            if hasattr(pedido, "to_dict")
            else {k: getattr(pedido, k) for k in pedido.__dict__}
        )
        usuario = getattr(pedido, "usuario", None)
        data["usuario"] = (
            usuario.to_dict()
            if usuario and hasattr(usuario, "to_dict")
            else (usuario.__dict__ if usuario else None)
        )
        items = getattr(pedido, "pedido_item", None)
        data["items"] = (
            [it.to_dict() if hasattr(it, "to_dict") else it.__dict__ for it in items]
            if items
            else []
        )
        direccion = getattr(pedido, "direccion", None)
        data["direccion"] = (
            direccion.to_dict()
            if direccion and hasattr(direccion, "to_dict")
            else (direccion.__dict__ if direccion else None)
        )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el pedido: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[PedidoEnriquecido])
async def obtener_pedidos_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Obtener pedidos por usuario (enriquecidos)."""
    try:
        pedido_crud = PedidoCRUD(db)
        pedidos = pedido_crud.obtener_pedidos_por_usuario(usuario_id)
        results = []
        for p in pedidos:
            data = (
                p.to_dict()
                if hasattr(p, "to_dict")
                else {k: getattr(p, k) for k in p.__dict__}
            )
            items = getattr(p, "pedido_item", None)
            data["items"] = (
                [
                    it.to_dict() if hasattr(it, "to_dict") else it.__dict__
                    for it in items
                ]
                if items
                else []
            )
            direccion = getattr(p, "direccion", None)
            data["direccion"] = (
                direccion.to_dict()
                if direccion and hasattr(direccion, "to_dict")
                else (direccion.__dict__ if direccion else None)
            )
            results.append(data)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pedidos por usuario: {str(e)}",
        )


@router.get("/buscar/{nombre}", response_model=List[PedidoResponse])
async def buscar_pedidos_por_nombre(
    nombre: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Buscar pedidos por nombre (búsqueda parcial)."""
    try:
        pedido_crud = PedidoCRUD(db)
        pedidos = pedido_crud.buscar_pedidos_por_nombre(
            nombre, skip=max(skip, 0), limit=limit
        )
        return pedidos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar pedidos: {str(e)}",
        )


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pedido(pedido_data: PedidoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo pedido."""
    try:
        pedido_crud = PedidoCRUD(db)

        pedido = pedido_crud.crear_pedido(
            id_usuario=pedido_data.id_usuario,
            id_direccion=pedido_data.id_direccion,
            total=pedido_data.total,
            estado=getattr(pedido_data, "estado", "Creado"),
            id_descuento=getattr(pedido_data, "id_descuento", None),
            fecha_pedido=getattr(pedido_data, "fecha_pedido", None),
            id_usuario_crea=getattr(pedido_data, "id_usuario_crea", None),
        )
        return pedido
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el pedido: {str(e)}",
        )


@router.put("/{pedido_id}", response_model=PedidoResponse)
async def actualizar_pedido(
    pedido_id: UUID, pedido_data: PedidoUpdate, db: Session = Depends(get_db)
):
    """Actualizar un pedido existente."""
    try:
        pedido_crud = PedidoCRUD(db)

        pedido_existente = pedido_crud.obtener_pedido(pedido_id)
        if not pedido_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in pedido_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return pedido_existente

        pedido_actualizado = pedido_crud.actualizar_pedido(
            pedido_id, **campos_actualizacion
        )
        return pedido_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar pedido: {str(e)}",
        )


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
async def actualizar_estado_pedido(
    pedido_id: UUID, nuevo_estado: str, db: Session = Depends(get_db)
):
    """Actualizar el estado de un pedido."""
    try:
        pedido_crud = PedidoCRUD(db)

        pedido_existente = pedido_crud.obtener_pedido(pedido_id)
        if not pedido_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        if nuevo_estado not in [
            "Creado",
            "Pagado",
            "Enviado",
            "Entregado",
            "Cancelado",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estado no válido",
            )

        pedido_actualizado = pedido_crud.cambiar_estado(pedido_id, nuevo_estado)
        return pedido_actualizado
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado no es válido",
        )


@router.delete("/{pedido_id}", response_model=RespuestaAPI)
async def eliminar_pedido(pedido_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un pedido."""
    try:
        pedido_crud = PedidoCRUD(db)

        pedido_existente = pedido_crud.obtener_pedido(pedido_id)
        if not pedido_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
            )

        pedido_eliminado = pedido_crud.eliminar_pedido(pedido_id)
        if pedido_eliminado:
            return RespuestaAPI(mensaje="Pedido eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el pedido",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el pedido: {str(e)}",
        )
