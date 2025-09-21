"""
Módulo de configuración de base de datos
========================================

Este módulo contiene la configuración y conexión a la base de datos
usando SQLAlchemy.
"""

from .database import get_engine, get_session, create_tables
from .config import DATABASE_URL

__all__ = ["get_engine", "get_session", "create_tables", "DATABASE_URL"]
