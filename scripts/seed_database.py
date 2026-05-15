"""
Inicializa la base de datos con el tarifario y los siniestros de demo.
Ejecutar una sola vez antes de levantar el servidor.

Uso:
    python -m scripts.seed_database
"""
import sys
import os

# Permite ejecutar desde la raíz del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db, upsert_item_tarifario, upsert_siniestro
from data.demo_data import TARIFARIO, SINIESTROS


def seed() -> None:
    print("Inicializando base de datos...")
    init_db()

    with get_db() as conn:
        print(f"  Insertando {len(TARIFARIO)} ítems en el tarifario...")
        for item in TARIFARIO:
            upsert_item_tarifario(conn, item)

        print(f"  Insertando {len(SINIESTROS)} siniestros de demo...")
        for s in SINIESTROS:
            upsert_siniestro(conn, s)

    print("✓ Base de datos lista.")
    print(f"  Archivo: {os.path.abspath('auditoria.db')}")


if __name__ == "__main__":
    seed()
