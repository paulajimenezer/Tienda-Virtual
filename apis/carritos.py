"""
API de Carritos - Endpoints para gestión de carritos
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud.compras.carritos_crud import CarritoCRUD
from database.config import get_db
from Entities.carritos import CarritoCreate, CarritoUpdate
from schemas import CarritoResponse, RespuestaAPI
from auth.jwt_utils import get_current_user

router = APIRouter(
    prefix="/carritos",
    tags=["carritos"],
    dependencies=[Depends(get_current_user)],
)


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
        carrito = carrito_crud.get_carrito(carrito_id)
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
        carrito_crud = CarritoCRUD(db)
        # CORRECCIÓN: no pasar 'db' como argumento
        return carrito_crud.list_carritos_usuario(usuario_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar carritos: {str(e)}"
        )


@router.patch("/{carrito_id}/cerrar", response_model=CarritoResponse)
async def cerrar(carrito_id: UUID, db: Session = Depends(get_db)):
    try:
        """Inactivar Carrito."""
        carrito_crud = CarritoCRUD(db)
        inactivar_carrito = carrito_crud.cerrar_carrito(carrito_id)
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
    """Crear u obtener el carrito activo del usuario."""
    try:
        carrito_crud = CarritoCRUD(db)
        obj = carrito_crud.get_or_create_carrito_activo(
            id_usuario=carrito_data.id_usuario,
            id_usuario_crea=getattr(carrito_data, "id_usuario_crea", None),
        )
        return obj
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
        carrito_existente = carrito_crud.get_carrito(carrito_id)
        if not carrito_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )
        # Mapear 'estado' -> 'activo' si viene en el body
        payload = {k: v for k, v in carrito_data.dict().items() if v is not None}
        if "estado" in payload:
            estado_val = (payload["estado"] or "").strip().lower()
            payload["activo"] = estado_val in ("activo", "abierto", "true", "1")
            del payload["estado"]

        obj = carrito_crud.update_carrito(
            carrito_id,
            activo=payload.get("activo"),
            id_usuario_edita=payload.get("id_usuario_edita"),
        )
        return obj
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
        carrito_existente = carrito_crud.get_carrito(carrito_id)
        if not carrito_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )
        ok = carrito_crud.eliminar_carrito(carrito_id)
        if ok:
            return RespuestaAPI(mensaje="Carrito eliminado exitosamente", exito=True)
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
