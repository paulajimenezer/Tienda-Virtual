"""CRUD para la entidad Descuentos.

Permite:
- Obtener descuento por ID.
- Listar descuentos.
- Obtener descuento por código (case-insensitive).
- Validar código de descuento (vigencia y estado).
- Crear descuento (código único, porcentaje, fechas).
- Actualizar descuento.
- Eliminar descuento.

Los códigos son strings de hasta 50 caracteres, aplicables al finalizar la compra.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime

from Entities.descuentos import Descuentos as DESCUENTOS


def get_descuento(db: Session, descuento_id: UUID) -> Optional[DESCUENTOS]:
    """Obtiene un descuento por su ID."""
    return db.get(DESCUENTOS, descuento_id)


def list_descuentos(db: Session, skip: int = 0, limit: int = 100) -> List[DESCUENTOS]:
    """Lista descuentos con paginación, ordenados por fecha de creación descendente."""
    return (
        db.query(DESCUENTOS)
        .order_by(DESCUENTOS.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_por_codigo(db: Session, codigo: str) -> Optional[DESCUENTOS]:
    """Obtiene un descuento por código (case-insensitive)."""
    if not codigo:
        return None
    codigo_norm = (codigo or "").strip().upper()
    return (
        db.query(DESCUENTOS)
        .filter(func.upper(DESCUENTOS.codigo) == codigo_norm)
        .first()
    )


def validar_codigo(
    db: Session, codigo: str, en_fecha: Optional[datetime] = None
) -> Optional[DESCUENTOS]:
    """
    Valida un código de descuento:
    - Existe
    - activo=True
    - fecha_inicio <= en_fecha <= fecha_fin
    Retorna el descuento válido o None si no aplica.

    Args:
        db: Sesión de base de datos.
        codigo: Código de descuento.
        en_fecha: Fecha de validación (opcional, por defecto ahora).

    Returns:
        Instancia de Descuentos válida o None.
    """
    d = get_por_codigo(db, codigo)
    if not d:
        return None
    if hasattr(d, "activo") and not bool(d.activo):
        return None
    ahora = en_fecha or datetime.utcnow()
    if getattr(d, "fecha_inicio", None) and d.fecha_inicio > ahora:
        return None
    if getattr(d, "fecha_fin", None) and d.fecha_fin < ahora:
        return None
    if getattr(d, "porcentaje", None) is None or d.porcentaje <= 0:
        return None
    return d


def create_descuento(
    db: Session,
    *,
    codigo: str,
    porcentaje: float,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    activo: bool = True,
    id_usuario_crea: UUID,
) -> DESCUENTOS:
    """
    Crea un descuento tipo código (<=50 chars).
    - porcentaje: 0 < p <= 100
    - Unicidad de código (case-insensitive).

    Args:
        db: Sesión de base de datos.
        codigo: Código de descuento.
        porcentaje: Porcentaje de descuento.
        fecha_inicio: Fecha de inicio de vigencia.
        fecha_fin: Fecha de fin de vigencia.
        activo: Estado del descuento.
        id_usuario_crea: UUID del usuario que crea.

    Returns:
        Instancia creada de Descuentos.
    """
    if not codigo or not codigo.strip():
        raise ValueError("El código es obligatorio")
    codigo_norm = codigo.strip().upper()
    if len(codigo_norm) > 50:
        raise ValueError("El código no puede exceder 50 caracteres")
    if porcentaje is None or porcentaje <= 0 or porcentaje > 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100")
    if not fecha_inicio or not fecha_fin or fecha_fin <= fecha_inicio:
        raise ValueError("El rango de fechas es inválido")
    if get_por_codigo(db, codigo_norm):
        raise ValueError("El código de descuento ya existe")

    obj = DESCUENTOS(
        codigo=codigo_norm,
        porcentaje=float(porcentaje),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        activo=bool(activo),
        id_usuario_crea=id_usuario_crea,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_descuento(
    db: Session,
    descuento_id: UUID,
    *,
    codigo: Optional[str] = None,
    porcentaje: Optional[float] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    activo: Optional[bool] = None,
    id_usuario_edita: Optional[UUID] = None,
) -> Optional[DESCUENTOS]:
    """
    Actualiza campos de un descuento.

    Args:
        db: Sesión de base de datos.
        descuento_id: UUID del descuento.
        codigo: Nuevo código (opcional).
        porcentaje: Nuevo porcentaje (opcional).
        fecha_inicio: Nueva fecha de inicio (opcional).
        fecha_fin: Nueva fecha de fin (opcional).
        activo: Nuevo estado (opcional).
        id_usuario_edita: UUID del usuario que edita (opcional).

    Returns:
        Instancia actualizada de Descuentos o None si no existe.
    """
    obj = db.get(DESCUENTOS, descuento_id)
    if not obj:
        return None

    if codigo is not None:
        cod_norm = (codigo or "").strip().upper()
        if not cod_norm:
            raise ValueError("El código es obligatorio")
        if len(cod_norm) > 50:
            raise ValueError("El código no puede exceder 50 caracteres")
        existente = get_por_codigo(db, cod_norm)
        if existente and existente.id != obj.id:
            raise ValueError("El código de descuento ya existe")
        obj.codigo = cod_norm

    if porcentaje is not None:
        if porcentaje <= 0 or porcentaje > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        obj.porcentaje = float(porcentaje)

    ini = fecha_inicio if fecha_inicio is not None else obj.fecha_inicio
    fin = fecha_fin if fecha_fin is not None else obj.fecha_fin
    if ini and fin and fin <= ini:
        raise ValueError("El rango de fechas es inválido")
    if fecha_inicio is not None:
        obj.fecha_inicio = fecha_inicio
    if fecha_fin is not None:
        obj.fecha_fin = fecha_fin

    if activo is not None:
        obj.activo = bool(activo)

    if hasattr(obj, "id_usuario_edita") and id_usuario_edita:
        obj.id_usuario_edita = id_usuario_edita

    db.commit()
    db.refresh(obj)
    return obj


def delete_descuento(db: Session, descuento_id: UUID) -> bool:
    """Desactiva (soft delete) un descuento por su ID."""
    obj = db.get(DESCUENTOS, descuento_id)
    if not obj:
        return False
    if hasattr(obj, "activo"):
        obj.activo = False
        db.commit()
        db.refresh(obj)
        return True
    db.delete(obj)
    db.commit()
    return True
