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
from schemas import CarritoResponse, RespuestaAPI, CarritoEnriquecido
from auth.jwt_utils import get_current_user

router = APIRouter(
    prefix="/api/carritos",
    tags=["carritos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[CarritoEnriquecido])
async def obtener_carritos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los carritos con paginación. Respuesta enriquecida con usuario y items."""
    try:
        carrito_crud = CarritoCRUD(db)
        carritos = carrito_crud.obtener_carritos(skip=skip, limit=limit)
        results = []
        for c in carritos:
            data = (
                c.to_dict()
                if hasattr(c, "to_dict")
                else {k: getattr(c, k) for k in c.__dict__}
            )
            usuario = getattr(c, "usuario", None)
            data["usuario"] = (
                usuario.to_dict()
                if usuario and hasattr(usuario, "to_dict")
                else (usuario.__dict__ if usuario else None)
            )
            items = getattr(c, "carrito_item", None)
            data["items"] = (
                [
                    it.to_dict() if hasattr(it, "to_dict") else it.__dict__
                    for it in items
                ]
                if items
                else []
            )
            results.append(data)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carritos: {str(e)}",
        )


@router.get("/{carrito_id}", response_model=CarritoEnriquecido)
async def obtener_carrito(carrito_id: UUID, db: Session = Depends(get_db)):
    """Obtener un carrito por ID (enriquecido con usuario e items)."""
    try:
        carrito_crud = CarritoCRUD(db)
        carrito = carrito_crud.get_carrito(carrito_id)
        if not carrito:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado"
            )
        data = (
            carrito.to_dict()
            if hasattr(carrito, "to_dict")
            else {k: getattr(carrito, k) for k in carrito.__dict__}
        )
        usuario = getattr(carrito, "usuario", None)
        data["usuario"] = (
            usuario.to_dict()
            if usuario and hasattr(usuario, "to_dict")
            else (usuario.__dict__ if usuario else None)
        )
        items = getattr(carrito, "carrito_item", None)
        data["items"] = (
            [it.to_dict() if hasattr(it, "to_dict") else it.__dict__ for it in items]
            if items
            else []
        )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carrito: {str(e)}",
        )


@router.get("/usuario/{usuario_id}", response_model=List[CarritoEnriquecido])
@router.get("/by-user/{usuario_id}", response_model=List[CarritoEnriquecido])
async def listar_carritos_usuario(
    usuario_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener todos los carritos de un usuario con paginación (enriquecidos)."""
    try:
        carrito_crud = CarritoCRUD(db)
        carritos = carrito_crud.list_carritos_usuario(
            usuario_id, skip=skip, limit=limit
        )
        results = []
        for c in carritos:
            data = (
                c.to_dict()
                if hasattr(c, "to_dict")
                else {k: getattr(c, k) for k in c.__dict__}
            )
            items = getattr(c, "carrito_item", None)
            data["items"] = (
                [
                    it.to_dict() if hasattr(it, "to_dict") else it.__dict__
                    for it in items
                ]
                if items
                else []
            )
            results.append(data)
        return results
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
