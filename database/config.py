"""
Configuración de la base de datos
=================================

Configuraciones centralizadas para la conexión a la base de datos.
"""

from dotenv import load_dotenv

# Para cargar la credencial de la BD
load_dotenv()
import os
from typing import Optional

# URL de la base de datos
# Por defecto usa SQLite, pero puede cambiarse por PostgreSQL, MySQL, etc.
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ejemplo_orm.db")

# Configuraciones adicionales
DB_ECHO: bool = os.getenv("DB_ECHO", "True").lower() == "true"
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))


# Configuraciones específicas para diferentes entornos
class DatabaseConfig:
    """Configuración de base de datos para diferentes entornos"""

    @staticmethod
    def get_sqlite_config(db_name: str = "ejemplo_orm.db") -> str:
        """Configuración para SQLite (desarrollo)"""
        return f"sqlite:///./{db_name}"

    @staticmethod
    def get_postgresql_config(
        host: str = "localhost",
        port: int = 5432,
        database: str = "ejemplo_orm",
        username: str = "postgres",
        password: str = "password",
    ) -> str:
        """Configuración para PostgreSQL (producción)"""
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

    @staticmethod
    def get_mysql_config(
        host: str = "localhost",
        port: int = 3306,
        database: str = "ejemplo_orm",
        username: str = "root",
        password: str = "password",
    ) -> str:
        """Configuración para MySQL"""
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
