"""Operaciones de normalización y consulta para Sexo.

Objetivo:
- Solo normalizar entradas a la BD y consultar (sin crear/editar/eliminar).
- Sexo permitido: M, F, O. El nombre se rellena automáticamente:
  M -> Masculino, F -> Femenino, O -> Otro.
"""

from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from Entities.sexo import Sexo as SEXO


class SexoCRUD:
    """CRUD de solo lectura + utilidades de normalización para Sexo."""

    CODIGOS_VALIDOS = {"M", "F", "O"}
    CODIGO_NOMBRE_MAP = {"M": "Masculino", "F": "Femenino", "O": "Otro"}

    def __init__(self, db: Session):
        self.db = db

    def normalizar_codigo(self, codigo: str) -> tuple[str, str]:
        """
        Normaliza y valida el código. Retorna (codigo_norm, nombre_norm).
        """
        if not codigo or not codigo.strip():
            raise ValueError("El código es obligatorio")
        codigo_norm = codigo.strip().upper()
        if codigo_norm not in self.CODIGOS_VALIDOS:
            raise ValueError("Código inválido. Valores permitidos: M, F, O")
        return codigo_norm, self.CODIGO_NOMBRE_MAP[codigo_norm]

    def normalizar_payload(self, data: Dict) -> Dict:
        """
        Normaliza un payload antes de persistir:
        - data['codigo'] -> 'M'|'F'|'O'
        - data['nombre'] -> correspondiente al código
        """
        if data is None:
            return {}
        d = dict(data)
        if "codigo" in d and d["codigo"] is not None:
            cod, nom = self.normalizar_codigo(d["codigo"])
            d["codigo"] = cod
            d["nombre"] = nom
        return d

    def obtener_por_codigo(self, codigo: str) -> Optional[SEXO]:
        """Obtiene un sexo por su código (case-insensitive)."""
        return (
            self.db.query(SEXO)
            .filter(func.upper(SEXO.codigo) == (codigo or "").strip().upper())
            .first()
        )

    def obtener_sexo(self, sexo_id: UUID) -> Optional[SEXO]:
        """Obtiene un sexo por su UUID."""
        return self.db.get(SEXO, sexo_id)

    def obtener_sexos(self, skip: int = 0, limit: int = 100) -> List[SEXO]:
        """Lista sexos con paginación."""
        return (
            self.db.query(SEXO)
            .order_by(SEXO.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def buscar_sexos(self, texto: str, skip: int = 0, limit: int = 100) -> List[SEXO]:
        """Busca sexos por coincidencia parcial en el nombre."""
        term = f"%{(texto or '').strip().title()}%"
        return (
            self.db.query(SEXO)
            .filter(SEXO.nombre.like(term))
            .order_by(SEXO.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        