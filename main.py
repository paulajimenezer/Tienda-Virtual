"""
Punto de entrada de la aplicación Tienda Virtual.

Este módulo inicia la aplicación de consola, gestiona el login de usuarios y
despliega los menús correspondientes según el rol (admin o cliente).
"""

import sys

from Utilities.auth import login_prompt, register_client_prompt
from Utilities.menus import admin_menu, cliente_menu

from database.config import SessionLocal, check_connection


def main():
    """
    Ejecuta el flujo principal de la aplicación:
    - Verifica la conexión a la base de datos.
    - Solicita login de usuario o registro de cuenta de cliente.
    - Redirige al menú de administrador o cliente según el rol.
    """
    if not check_connection():
        print("Error de conexión a la base de datos")
        sys.exit(1)

    print("\n=== Tienda Virtual ===")
    while True:
        with SessionLocal() as db:
            print("\n1) Iniciar sesión")
            print("2) Crear cuenta (cliente)")
            print("9) Salir")
            opt = input("Seleccione: ").strip()
            if opt == "9":
                print("Saliendo...")
                break
            if opt == "2":
                register_client_prompt(db)
                continue
            if opt != "1":
                print("Opción inválida")
                continue

            user, is_admin = login_prompt(db)
            if not user:
                print("No autenticado.")
                continue

            if is_admin:
                admin_menu(db, user)
            else:
                cliente_menu(db, user)


if __name__ == "__main__":
    main()
