from __future__ import annotations
"""
Gestión de la base de datos SQLite.
Usa un context manager para conexiones seguras.
"""
import sqlite3
import json
from contextlib import contextmanager
from app.config import DB_PATH


@contextmanager
def get_db():
    """Context manager que garantiza cierre de conexión."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Crea las tablas si no existen."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tarifario (
                codigo          TEXT PRIMARY KEY,
                descripcion     TEXT NOT NULL,
                precio_min      REAL NOT NULL,
                precio_max      REAL NOT NULL,
                unidad          TEXT NOT NULL,
                categoria       TEXT NOT NULL,
                vigente_desde   TEXT NOT NULL,
                vigente_hasta   TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS siniestros (
                id                  TEXT PRIMARY KEY,
                tipo_accidente      TEXT NOT NULL,
                partes_afectadas    TEXT NOT NULL,   -- JSON array
                vehiculo            TEXT NOT NULL,
                poliza              TEXT NOT NULL,
                fecha_accidente     TEXT NOT NULL,
                descripcion         TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auditorias (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id              TEXT NOT NULL,
                siniestro_id            TEXT NOT NULL,
                resultado               TEXT NOT NULL,
                confianza               REAL NOT NULL,
                items_aprobados         INTEGER NOT NULL,
                items_observados        INTEGER NOT NULL,
                monto_total_factura     REAL NOT NULL,
                monto_discrepancias     REAL NOT NULL,
                discrepancias           TEXT NOT NULL,  -- JSON
                requiere_revision_humana INTEGER NOT NULL,
                razonamiento            TEXT NOT NULL,
                recomendacion           TEXT NOT NULL,
                timestamp               TEXT NOT NULL
            );
        """)


# ─── Tarifario ────────────────────────────────────────────────────────────────

def upsert_item_tarifario(conn: sqlite3.Connection, item: dict) -> None:
    conn.execute("""
        INSERT OR REPLACE INTO tarifario
            (codigo, descripcion, precio_min, precio_max, unidad, categoria,
             vigente_desde, vigente_hasta)
        VALUES (:codigo, :descripcion, :precio_min, :precio_max, :unidad,
                :categoria, :vigente_desde, :vigente_hasta)
    """, item)


def buscar_en_tarifario(conn: sqlite3.Connection, codigo: str, fecha: str) -> sqlite3.Row | None:
    """Devuelve el ítem vigente en la fecha dada, o None."""
    return conn.execute("""
        SELECT precio_min, precio_max, descripcion, categoria
        FROM tarifario
        WHERE codigo = ?
          AND ? BETWEEN vigente_desde AND vigente_hasta
    """, (codigo, fecha)).fetchone()


# ─── Siniestros ───────────────────────────────────────────────────────────────

def upsert_siniestro(conn: sqlite3.Connection, s: dict) -> None:
    conn.execute("""
        INSERT OR REPLACE INTO siniestros
            (id, tipo_accidente, partes_afectadas, vehiculo, poliza,
             fecha_accidente, descripcion)
        VALUES (:id, :tipo_accidente, :partes_afectadas, :vehiculo, :poliza,
                :fecha_accidente, :descripcion)
    """, {**s, "partes_afectadas": json.dumps(s["partes_afectadas"], ensure_ascii=False)})


def obtener_siniestro(siniestro_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM siniestros WHERE id = ?", (siniestro_id,)
        ).fetchone()
    if row is None:
        return None
    d = dict(row)
    d["partes_afectadas"] = json.loads(d["partes_afectadas"])
    return d


def listar_siniestros() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM siniestros ORDER BY fecha_accidente DESC").fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["partes_afectadas"] = json.loads(d["partes_afectadas"])
        result.append(d)
    return result


# ─── Auditorías ───────────────────────────────────────────────────────────────

def guardar_auditoria(dictamen: dict) -> int:
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO auditorias
                (factura_id, siniestro_id, resultado, confianza,
                 items_aprobados, items_observados, monto_total_factura,
                 monto_discrepancias, discrepancias, requiere_revision_humana,
                 razonamiento, recomendacion, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dictamen["factura_id"],
            dictamen["siniestro_id"],
            dictamen["resultado"],
            dictamen["confianza"],
            dictamen["items_aprobados"],
            dictamen["items_observados"],
            dictamen["monto_total_factura"],
            dictamen["monto_discrepancias"],
            json.dumps(dictamen["discrepancias"], ensure_ascii=False),
            int(dictamen["requiere_revision_humana"]),
            dictamen["razonamiento"],
            dictamen["recomendacion"],
            dictamen["timestamp"],
        ))
        return cursor.lastrowid


def listar_auditorias(limit: int = 50) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM auditorias ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["discrepancias"] = json.loads(d["discrepancias"])
        d["requiere_revision_humana"] = bool(d["requiere_revision_humana"])
        result.append(d)
    return result


# ─── Tarifario: lectura y gestión ────────────────────────────────────────────

def listar_tarifario() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM tarifario ORDER BY categoria, codigo"
        ).fetchall()
    return [dict(r) for r in rows]


def agregar_item_tarifario(item: dict) -> None:
    with get_db() as conn:
        upsert_item_tarifario(conn, item)


def eliminar_item_tarifario(codigo: str) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM tarifario WHERE codigo = ?", (codigo,))


# ─── Siniestros: crear y editar ───────────────────────────────────────────────

def crear_siniestro(s: dict) -> None:
    with get_db() as conn:
        upsert_siniestro(conn, s)


def eliminar_siniestro(siniestro_id: str) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM siniestros WHERE id = ?", (siniestro_id,))
