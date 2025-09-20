import sys
import os

# Añadimos el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from entities import *  # Asegúrate de que las entidades estén correctamente definidas aquí.
from database.database import create_tables

if __name__ == "__main__":
    create_tables()
    print("✅ Tablas creadas en Neon")
