import sys
from database.config import check_connection, init_db

# Importar las entidades para registrar todos los modelos en Base.metadata
import Entities  # noqa: F401


def main():
    if not check_connection():
        print("Error de conexión a la base de datos")
        sys.exit(1)

    init_db(run_seed=True)
    print("Conexión OK. Tablas creadas/actualizadas y seeders ejecutados.")


if __name__ == "__main__":
    main()
