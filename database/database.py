"""
Configuración y conexión a la base de datos
===========================================

Este módulo maneja la conexión a la base de datos usando SQLAlchemy.
"""

from __future__ import annotations
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import logging

from .config import DATABASE_URL, DB_ECHO, DB_POOL_SIZE, DB_MAX_OVERFLOW

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Crear la clase base para los modelos
class Base(DeclarativeBase):
    """Base declarativa común a todas las entidades."""

    pass


# Configurar el motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    # Configuraciones específicas para SQLite
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_engine():
    """Retorna el motor de base de datos"""
    return engine


def get_session() -> Session:
    """
    Crea y retorna una nueva sesión de base de datos

    Returns:
        Session: Sesión de SQLAlchemy
    """
    return SessionLocal()


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager para manejar sesiones de base de datos

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        with get_session_context() as session:
            user = session.query(Usuario).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Error en la sesión: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """
    Crea todas las tablas definidas en los modelos

    Esta función debe ser llamada después de importar todos los modelos
    para que SQLAlchemy pueda detectarlos.
    """
    try:
        logger.info("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        raise


def drop_tables():
    """
    Elimina todas las tablas de la base de datos

    ⚠️ CUIDADO: Esta función elimina TODOS los datos
    """
    try:
        logger.warning("Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Tablas eliminadas exitosamente")
    except Exception as e:
        logger.error(f"Error al eliminar tablas: {e}")
        raise


def check_connection():
    """
    Verifica la conexión a la base de datos

    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        return False
