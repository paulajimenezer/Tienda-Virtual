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

class DescuentosCRUD:
    def __init__(self, db: Session):
        self.db = db

    def obtener_descuento(self, descuento_id: UUID) -> Optional[DESCUENTOS]:
        return self.db.get(DESCUENTOS, descuento_id)

    def obtener_descuentos(self, skip: int = 0, limit: int = 100) -> List[DESCUENTOS]:
        return (
            self.db.query(DESCUENTOS)
            .order_by(DESCUENTOS.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_por_codigo(self, codigo: str) -> Optional[DESCUENTOS]:
        if not codigo:
            return None
        codigo_norm = (codigo or "").strip().upper()
        return (
            self.db.query(DESCUENTOS)
            .filter(func.upper(DESCUENTOS.codigo) == codigo_norm)
            .first()
        )

    def validar_codigo(self, codigo: str, en_fecha: Optional[datetime] = None) -> Optional[DESCUENTOS]:
        d = self.obtener_por_codigo(codigo)
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

    def crear_descuento(
        self,
        *,
        codigo: str,
        porcentaje: float,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        activo: bool = True,
        id_usuario_crea: UUID,
    ) -> DESCUENTOS:
        if not codigo or not codigo.strip():
            raise ValueError("El código es obligatorio")
        codigo_norm = codigo.strip().upper()
        if len(codigo_norm) > 50:
            raise ValueError("El código no puede exceder 50 caracteres")
        if porcentaje is None or porcentaje <= 0 or porcentaje > 100:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
        if not fecha_inicio or not fecha_fin or fecha_fin <= fecha_inicio:
            raise ValueError("El rango de fechas es inválido")
        if self.obtener_por_codigo(codigo_norm):
            raise ValueError("El código de descuento ya existe")

        obj = DESCUENTOS(
            codigo=codigo_norm,
            porcentaje=float(porcentaje),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activo=bool(activo),
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def actualizar_descuento(
        self,
        descuento_id: UUID,
        *,
        codigo: Optional[str] = None,
        porcentaje: Optional[float] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        activo: Optional[bool] = None,
        id_usuario_edita: Optional[UUID] = None,
    ) -> Optional[DESCUENTOS]:
        obj = self.db.get(DESCUENTOS, descuento_id)
        if not obj:
            return None

        if codigo is not None:
            cod_norm = (codigo or "").strip().upper()
            if not cod_norm:
                raise ValueError("El código es obligatorio")
            if len(cod_norm) > 50:
                raise ValueError("El código no puede exceder 50 caracteres")
            existente = self.obtener_por_codigo(cod_norm)
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

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def eliminar_descuento(self, descuento_id: UUID) -> bool:
        obj = self.db.get(DESCUENTOS, descuento_id)
        if not obj:
            return False
        if hasattr(obj, "activo"):
            obj.activo = False
            self.db.commit()
            self.db.refresh(obj)
            return True
        self.db.delete(obj)
        self.db.commit()
        return True