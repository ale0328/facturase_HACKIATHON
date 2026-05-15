from __future__ import annotations
"""
Los tres motores de verificación de facturas.

1. Motor de precios     — compara cada ítem contra el tarifario vigente.
2. Motor de duplicados  — detecta ítems con el mismo código repetidos.
3. Motor de coherencia  — valida que los insumos correspondan al siniestro (via Claude).
"""
import json
import sqlite3
from collections import Counter

from app.extractor import get_client, _extraer_json
from app.config import GEMINI_MODEL


# ─── 1. Motor de precios ──────────────────────────────────────────────────────

def verificar_precios(items: list[dict], conn: sqlite3.Connection, fecha_factura: str) -> list[dict]:
    """
    Compara cada ítem de la factura contra el tarifario vigente en fecha_factura.
    Retorna lista de discrepancias de tipo 'precio_excedido' o 'codigo_no_encontrado'.
    """
    discrepancias: list[dict] = []

    for item in items:
        codigo = item.get("codigo", "").strip()
        if not codigo:
            continue

        row = conn.execute("""
            SELECT precio_min, precio_max, descripcion
            FROM tarifario
            WHERE codigo = ?
              AND ? BETWEEN vigente_desde AND vigente_hasta
        """, (codigo, fecha_factura)).fetchone()

        if row is None:
            discrepancias.append({
                "tipo": "codigo_no_encontrado",
                "item": item["descripcion"],
                "codigo": codigo,
            })
        elif item["precio_unitario"] > row["precio_max"]:
            discrepancias.append({
                "tipo": "precio_excedido",
                "item": item["descripcion"],
                "codigo": codigo,
                "cobrado": round(item["precio_unitario"], 2),
                "tarifario_max": round(row["precio_max"], 2),
                "diferencia": round(item["precio_unitario"] - row["precio_max"], 2),
            })

    return discrepancias


# ─── 2. Motor de duplicados ───────────────────────────────────────────────────

def detectar_duplicados(items: list[dict]) -> list[dict]:
    """
    Detecta ítems con el mismo código que aparecen más de una vez.
    Excluye códigos vacíos o nulos para evitar falsos positivos.
    """
    codigos_validos = [i["codigo"].strip() for i in items if i.get("codigo", "").strip()]
    conteo = Counter(codigos_validos)

    # Mapear código → descripción para el reporte
    desc_map = {i["codigo"].strip(): i["descripcion"] for i in items if i.get("codigo", "").strip()}

    return [
        {
            "tipo": "duplicado",
            "codigo": cod,
            "descripcion": desc_map.get(cod, cod),
            "ocurrencias": n,
        }
        for cod, n in conteo.items()
        if n > 1
    ]


# ─── 3. Motor de coherencia (Claude) ─────────────────────────────────────────

_PROMPT_COHERENCIA = """Eres un auditor experto en seguros automotrices.

SINIESTRO REPORTADO:
- Tipo de accidente: {tipo_accidente}
- Partes afectadas según perito: {partes_afectadas}
- Vehículo: {vehiculo}
- Descripción: {descripcion}

ÍTEMS COBRADOS POR EL TALLER:
{items_json}

Analiza si los ítems cobrados son coherentes con las partes afectadas en el siniestro.
Identifica cualquier ítem que NO pueda justificarse por el tipo de accidente o las partes dañadas.

Responde SOLO con un objeto JSON, sin texto adicional:
{{
  "coherente": true,
  "items_inconsistentes": [
    {{
      "tipo": "item_incoherente",
      "item": "nombre del ítem",
      "razon": "por qué no corresponde al siniestro"
    }}
  ],
  "razonamiento": "explicación breve del análisis general"
}}"""


def verificar_coherencia_siniestro(
    items: list[dict],
    siniestro: dict,
) -> dict:
    """
    Usa Gemini para validar que los ítems de la factura sean coherentes
    con las partes afectadas reportadas en el siniestro.

    Retorna un dict con:
      - coherente: bool
      - items_inconsistentes: list[dict]
      - razonamiento: str
    """
    client = get_client()

    prompt = _PROMPT_COHERENCIA.format(
        tipo_accidente=siniestro.get("tipo_accidente", ""),
        partes_afectadas=", ".join(siniestro.get("partes_afectadas", [])),
        vehiculo=siniestro.get("vehiculo", ""),
        descripcion=siniestro.get("descripcion", ""),
        items_json=json.dumps(items, ensure_ascii=False, indent=2),
    )

    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    resultado = _extraer_json(resp.text)
    # Garantizamos que los campos existan
    resultado.setdefault("coherente", True)
    resultado.setdefault("items_inconsistentes", [])
    resultado.setdefault("razonamiento", "")
    return resultado
