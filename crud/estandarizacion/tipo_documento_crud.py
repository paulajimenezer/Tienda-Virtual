"""Operaciones de normalización y consulta para Tipo de Documento.

Objetivo:
- Solo normalizar entradas a CC/TI/PP y consultar (sin crear/editar/eliminar).
"""

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from Entities.tipo_documento import Tipo_documento as TIPO_DOCUMENTO


class TipoDocumentoCRUD:
    """
    Utilidades de normalización y consulta para Tipo de Documento.
    """

    TIPOS_VALIDOS = {"CC", "TI", "PP"}

    def __init__(self, db: Session):
        self.db = db

    def _normalizar_nombre(self, nombre: str) -> str:
        return (nombre or "").strip().upper()

    def normalizar_nombre_valido(self, nombre: str) -> str:
        """
        Normaliza y valida el nombre. Retorna nombre en UPPER si es válido.
        Permitidos: CC, TI, PP.
        """
        nombre_norm = self._normalizar_nombre(nombre)
        if nombre_norm not in self.TIPOS_VALIDOS:
            raise ValueError("El tipo de documento debe ser 'CC', 'TI' o 'PP'")
        return nombre_norm

    def normalizar_payload(self, data: Dict) -> Dict:
        """
        Normaliza un payload antes de persistir:
        - data['nombre'] -> 'CC'|'TI'|'PP'
        """
        if data is None:
            return {}
        d = dict(data)
        if "nombre" in d and d["nombre"] is not None:
            d["nombre"] = self.normalizar_nombre_valido(d["nombre"])
        return d

    def obtener_tipo_documento(
        self, tipo_documento_id: UUID
    ) -> Optional[TIPO_DOCUMENTO]:
        return self.db.get(TIPO_DOCUMENTO, tipo_documento_id)

    def obtener_tipo_documento_por_nombre(
        self, nombre: str
    ) -> Optional[TIPO_DOCUMENTO]:
        nombre_norm = self._normalizar_nombre(nombre)
        return (
            self.db.query(TIPO_DOCUMENTO)
            .filter(func.upper(TIPO_DOCUMENTO.nombre) == nombre_norm)
            .first()
        )

    def buscar_tipos_documento(
        self, texto: str, skip: int = 0, limit: int = 100
    ) -> List[TIPO_DOCUMENTO]:
        term = f"%{(texto or '').strip().upper()}%"
        return (
            self.db.query(TIPO_DOCUMENTO)
            .filter(func.upper(TIPO_DOCUMENTO.nombre).like(term))
            .order_by(TIPO_DOCUMENTO.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_tipos_documento(
        self, skip: int = 0, limit: int = 100
    ) -> List[TIPO_DOCUMENTO]:
        """
        Lista tipos de documento con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de instancias de TIPO_DOCUMENTO.
        """
        return (
            self.db.query(TIPO_DOCUMENTO)
            .order_by(TIPO_DOCUMENTO.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
