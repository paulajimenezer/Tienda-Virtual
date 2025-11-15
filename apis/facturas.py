"""
API de Facturas - Endpoints para gestión de facturas
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.jwt_utils import get_current_user
from crud.pedidos.facturas_crud import FacturaCRUD
from database.config import get_db
from Entities.facturas import FacturaCreate, FacturaResponse, FacturaUpdate
from schemas import RespuestaAPI, FacturaEnriquecida

router = APIRouter(
    prefix="/api/facturas",
    tags=["facturas"],
    dependencies=[Depends(get_current_user)],
)


def _serialize_factura_enriquecida(factura):
    data = (
        factura.to_dict()
        if hasattr(factura, "to_dict")
        else {k: getattr(factura, k) for k in factura.__dict__}
    )
    pedido = getattr(factura, "pedido", None)
    data["pedido"] = (
        pedido.to_dict()
        if pedido and hasattr(pedido, "to_dict")
        else (pedido.__dict__ if pedido else None)
    )
    usuario = getattr(pedido, "usuario", None) if pedido else None
    data["usuario"] = (
        usuario.to_dict()
        if usuario and hasattr(usuario, "to_dict")
        else (usuario.__dict__ if usuario else None)
    )
    return data


@router.get("/", response_model=List[FacturaEnriquecida])
async def listar_facturas(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Listar facturas con paginación opcional. La respuesta incluye datos relacionados
    (pedido y usuario propietario) para evitar múltiples llamadas desde el frontend.
    """
    try:
        factura_crud = FacturaCRUD(db)
        facturas = factura_crud.obtener_facturas(skip=skip, limit=limit)
        return [_serialize_factura_enriquecida(f) for f in facturas]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener facturas: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[FacturaEnriquecida])
async def listar_facturas_por_usuario(
    usuario_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Listar facturas pertenecientes a los pedidos de un usuario específico."""
    try:
        factura_crud = FacturaCRUD(db)
        facturas = factura_crud.obtener_facturas_por_usuario(
            usuario_id, skip=skip, limit=limit
        )
        return [_serialize_factura_enriquecida(f) for f in facturas]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener facturas del usuario: {str(e)}",
        )


@router.get("/{factura_id}", response_model=FacturaEnriquecida)
async def obtener_factura(factura_id: UUID, db: Session = Depends(get_db)):
    """Obtener factura por ID, incluyendo datos relacionados (pedido y usuario)."""
    try:
        factura_crud = FacturaCRUD(db)
        factura = factura_crud.obtener_factura(factura_id)
        if not factura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada"
            )
        return _serialize_factura_enriquecida(factura)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener factura: {str(e)}",
        )


@router.post("/", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def crear_factura(factura_data: FacturaCreate, db: Session = Depends(get_db)):
    """Crear un nuevo factura."""
    try:
        factura_crud = FacturaCRUD(db)

        factura = factura_crud.crear_factura(
            id_pedido=factura_data.id_pedido,
            numero_factura=factura_data.numero_factura,
            subtotal=factura_data.subtotal,
            impuesto=factura_data.impuesto,
            total=factura_data.total,
            fecha_emision=getattr(factura_data, "fecha_emision", None),
            id_usuario_crea=getattr(factura_data, "id_usuario_crea", None),
        )
        return factura
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear factura: {str(e)}",
        )


@router.put("/{factura_id}", response_model=FacturaResponse)
async def actualizar_factura(
    factura_id: UUID, factura_data: FacturaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una factura existente."""
    try:
        factura_crud = FacturaCRUD(db)

        factura_existente = factura_crud.obtener_factura(factura_id)
        if not factura_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada"
            )

        campos_actualizacion = {
            k: v for k, v in factura_data.dict().items() if v is not None
        }

        if not campos_actualizacion:
            return factura_existente

        factura_actualizada = factura_crud.actualizar_factura(
            factura_id, **campos_actualizacion
        )
        return factura_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar factura: {str(e)}",
        )


@router.delete("/{factura_id}", response_model=RespuestaAPI)
async def eliminar_factura(factura_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una factura."""
    try:
        factura_crud = FacturaCRUD(db)

        factura_existente = factura_crud.obtener_factura(factura_id)
        if not factura_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada"
            )

        factura_eliminada = factura_crud.eliminar_factura(factura_id)
        if factura_eliminada:
            return RespuestaAPI(mensaje="Factura eliminada exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar factura",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar factura: {str(e)}",
        )
