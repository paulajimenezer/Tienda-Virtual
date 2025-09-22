"""Operaciones de normalización y consulta para Roles.

Objetivo:
- Solo normalizar entradas y consultar (sin crear/editar/eliminar).
- Roles permitidos: dos variantes mapeadas por el flag admin:
  admin=True  -> "Admin"
  admin=False -> "Cliente"
"""

from typing import List, Optional, Union, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from Entities.roles import Roles as ROLES


class RolCRUD:
    """CRUD de solo lectura + utilidades de normalización para Roles."""

    ROLE_BOOL_TO_NAME = {True: "Admin", False: "Cliente"}
    ROLE_NAME_TO_BOOL = {"ADMIN": True, "CLIENTE": False}
    ROLES_VALIDOS = {"Admin", "Cliente"}

    def __init__(self, db: Session):
        self.db = db

    def _normalizar_nombre_valido(self, nombre: str) -> str:
        """Normaliza nombre a Title y valida que sea Admin o Cliente."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")
        nombre_norm = nombre.strip().title()
        if nombre_norm not in self.ROLES_VALIDOS:
            raise ValueError("Rol inválido. Valores permitidos: Admin, Cliente")
        return nombre_norm

    def normalizar_desde_flag(self, admin: bool) -> str:
        """Convierte admin=True/False al nombre de rol normalizado."""
        if admin not in (True, False):
            raise ValueError("El flag admin debe ser booleano")
        return self.ROLE_BOOL_TO_NAME[admin]

    def normalizar_entrada(self, entrada: Union[str, bool]) -> str:
        """
        Acepta un nombre ('Admin'/'Cliente') o un booleano (True/False) y
        retorna el nombre normalizado del rol.
        """
        if isinstance(entrada, bool):
            return self.normalizar_desde_flag(entrada)
        return self._normalizar_nombre_valido(str(entrada))

    def normalizar_payload(self, data: Dict) -> Dict:
        """
        Normaliza un payload antes de persistir:
        - Si viene 'admin' (bool), setea 'nombre' acorde y mantiene 'admin'.
        - Si viene 'nombre', lo normaliza a Admin/Cliente.
        """
        if data is None:
            return {}
        d = dict(data)
        if "admin" in d and d["admin"] is not None:
            d["nombre"] = self.normalizar_desde_flag(bool(d["admin"]))
        elif "nombre" in d and d["nombre"] is not None:
            d["nombre"] = self._normalizar_nombre_valido(d["nombre"])
            d.setdefault("admin", self.ROLE_NAME_TO_BOOL[d["nombre"].upper()])
        return d

    def obtener_rol_por_nombre(self, nombre: str) -> Optional[ROLES]:
        """Obtiene un rol por nombre (Admin/Cliente)."""
        nom = self._normalizar_nombre_valido(nombre)
        return (
            self.db.query(ROLES).filter(func.lower(ROLES.nombre) == nom.lower()).first()
        )

    def obtener_rol_por_flag(self, admin: bool) -> Optional[ROLES]:
        """Obtiene un rol usando admin=True/False."""
        nom = self.normalizar_desde_flag(admin)
        return (
            self.db.query(ROLES).filter(func.lower(ROLES.nombre) == nom.lower()).first()
        )

    def obtener_rol(self, rol_id: UUID) -> Optional[ROLES]:
        """Obtiene un rol por su UUID."""
        return self.db.get(ROLES, rol_id)

    def obtener_roles(self, skip: int = 0, limit: int = 100) -> List[ROLES]:
        """Lista roles con paginación."""
        return (
            self.db.query(ROLES)
            .order_by(ROLES.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def buscar_roles(self, texto: str, skip: int = 0, limit: int = 100) -> List[ROLES]:
        """Busca roles por coincidencia parcial en el nombre."""
        term = f"%{(texto or '').strip().lower()}%"
        return (
            self.db.query(ROLES)
            .filter(func.lower(ROLES.nombre).like(term))
            .order_by(ROLES.nombre.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
