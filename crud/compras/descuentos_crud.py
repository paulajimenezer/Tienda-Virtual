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
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from Entities.descuentos import Descuentos as DESCUENTOS
from datetime import datetime  # asegurado
from sqlalchemy.orm import Session as SASession


class DescuentoCRUD:
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
        """
        Busca un descuento por código exacto (case-insensitive).
        """
        if not codigo:
            return None
        cod = (codigo or "").strip().upper()
        return (
            self.db.query(DESCUENTOS)
            .filter(func.upper(DESCUENTOS.codigo) == cod)
            .first()
        )

    def buscar_por_codigo(
        self, texto: str, skip: int = 0, limit: int = 100
    ) -> List[DESCUENTOS]:
        """
        Búsqueda parcial por código (case-insensitive).
        """
        term = f"%{(texto or '').strip().upper()}%"
        return (
            self.db.query(DESCUENTOS)
            .filter(func.upper(DESCUENTOS.codigo).like(term))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _parse_fecha(self, value: Optional[object]) -> Optional[datetime]:
        """Permite fecha como datetime o ISO string."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except Exception:
                return None
        return None

    def validar_codigo(
        self,
        codigo: object,
        fecha: Optional[object] = None,
        en_fecha: Optional[object] = None,
    ) -> Optional[DESCUENTOS]:
        """
        Valida un código de descuento en una fecha dada.
        - código debe ser str (case-insensitive).
        - fecha o en_fecha pueden ser datetime o string ISO ('YYYY-MM-DD').
        Nota: No pase la Session como primer argumento; use instancia.validar_codigo(codigo, en_fecha=...).
        """
        # Si por error pasan la sesión como primer argumento, reacomodar parámetros
        if isinstance(codigo, SASession):
            codigo, fecha = fecha, en_fecha

        # Mitigar mal uso posicional: si 'codigo' no es str y 'fecha' sí lo es
        if not isinstance(codigo, str) and isinstance(fecha, str):
            codigo, fecha = fecha, None

        if not isinstance(codigo, str) or not codigo.strip():
            return None

        cod = codigo.strip().upper()
        ref_dt = (
            self._parse_fecha(en_fecha) or self._parse_fecha(fecha) or datetime.utcnow()
        )

        desc = (
            self.db.query(DESCUENTOS)
            .filter(func.upper(DESCUENTOS.codigo) == cod, DESCUENTOS.activo == True)
            .first()
        )
        if not desc:
            return None

        ini = getattr(desc, "fecha_inicio", None)
        fin = getattr(desc, "fecha_fin", None)

        # Comparación por día (inclusive) para evitar errores de hora/zonas
        ref_d = ref_dt.date()
        ini_d = (
            ini.date()
            if isinstance(ini, datetime)
            else getattr(ini, "date", lambda: ini)()
        )
        fin_d = (
            fin.date()
            if isinstance(fin, datetime)
            else getattr(fin, "date", lambda: fin)()
        )

        if ini_d and fin_d and not (ini_d <= ref_d <= fin_d):
            return None
        return desc

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


# Alias para compatibilidad con imports existentes
DescuentosCRUD = DescuentoCRUD
