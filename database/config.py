"""
Configuración de la base de datos PostgreSQL con Neon
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Se requiere DATABASE_URL en las variables de entorno")

# Crear el motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver consultas SQL
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
    connect_args={"sslmode": "require"},  # Requerir SSL para Neon
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas definidas en los modelos
    """
    # Asegurar que todos los modelos estén registrados en Base.metadata
    import Entities  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_connection():
    """
    Verifica la conexión a la base de datos.
    Retorna True si la conexión es exitosa, False si falla.
    """
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False


def init_db(run_seed: bool = True):
    """
    Crea tablas (si no existen) y ejecuta los seeders.
    """
    create_tables()
    # Asegurar que columnas de auditoría permitan NULL para el bootstrap del seeder
    ensure_bootstrap_nullable()
    if run_seed:
        try:
            from seed import run_seed as _run_seed

            _run_seed()
        except Exception as e:
            print(f"Error ejecutando seeders: {e}")


def ensure_bootstrap_nullable():
    """
    Ajusta columnas id_usuario_crea / id_usuario_edita a NULLABLE en tablas conocidas.
    Necesario cuando la base ya existe con NOT NULL por esquemas previos.
    Es idempotente: ignora errores si ya está ajustado.
    """
    stmts = [
        # Estandarización
        "ALTER TABLE roles ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE roles ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE sexo ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE sexo ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE tipo_documento ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE tipo_documento ALTER COLUMN id_usuario_edita DROP NOT NULL",
        # Usuarios (faltaba)
        "ALTER TABLE usuarios ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE usuarios ALTER COLUMN id_usuario_edita DROP NOT NULL",
        # Catálogo y productos
        "ALTER TABLE categorias ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE categorias ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE productos ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE productos ALTER COLUMN id_usuario_edita DROP NOT NULL",
        # Direcciones y compras
        "ALTER TABLE direcciones ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE direcciones ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE carritos ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE carritos ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE carrito_items ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE carrito_items ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE descuentos ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE descuentos ALTER COLUMN id_usuario_edita DROP NOT NULL",
        # Pedidos y facturación
        "ALTER TABLE pedidos ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE pedidos ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE pedido_items ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE pedido_items ALTER COLUMN id_usuario_edita DROP NOT NULL",
        "ALTER TABLE facturas ALTER COLUMN id_usuario_crea DROP NOT NULL",
        "ALTER TABLE facturas ALTER COLUMN id_usuario_edita DROP NOT NULL",
    ]
    try:
        with engine.begin() as conn:
            for stmt in stmts:
                try:
                    conn.execute(text(stmt))
                except Exception:
                    # Ignorar si ya es NULLABLE o si la tabla/columna aún no existe
                    pass
    except Exception as e:
        print(f"Advertencia: no fue posible ajustar nullability de auditoría: {e}")
