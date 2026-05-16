"""
Script para agregar un usuario al sistema Facturase.

Uso:
    python -m scripts.add_user
"""
import sys
import os
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, agregar_usuario, listar_usuarios_count


def main() -> None:
    print("=" * 40)
    print("  Facturase — Agregar Usuario")
    print("=" * 40)

    init_db()

    total = listar_usuarios_count()
    if total > 0:
        print(f"[INFO] Ya existen {total} usuario(s) en el sistema.\n")

    username = input("Nombre de usuario: ").strip()
    if not username:
        print("[ERROR] El nombre de usuario no puede estar vacio.")
        sys.exit(1)

    if len(username) < 3:
        print("[ERROR] El nombre de usuario debe tener al menos 3 caracteres.")
        sys.exit(1)

    password = getpass.getpass("Contrasena (min. 6 caracteres): ")
    if len(password) < 6:
        print("[ERROR] La contrasena debe tener al menos 6 caracteres.")
        sys.exit(1)

    confirm = getpass.getpass("Confirmar contrasena: ")
    if password != confirm:
        print("[ERROR] Las contrasenas no coinciden.")
        sys.exit(1)

    ok = agregar_usuario(username, password)
    if ok:
        print(f"\n[OK] Usuario '{username}' creado exitosamente.")
    else:
        print(f"\n[ERROR] Ya existe un usuario con el nombre '{username}'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
