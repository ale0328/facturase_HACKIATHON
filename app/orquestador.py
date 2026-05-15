from __future__ import annotations
"""
Orquestador principal de auditoría.

Coordina los tres motores de verificación y le pide a Claude
que emita un dictamen razonado con toda la evidencia recopilada.
"""
import json
from datetime import datetime, timezone

from app.config import GEMINI_MODEL, CONFIANZA_REVISION_HUMANA, MONTO_REVISION_HUMANA
from app.database import get_db, guardar_auditoria
from app.extractor import extraer_factura, get_client, _extraer_json
from app.verificadores import (
    detectar_duplicados,
    verificar_coherencia_siniestro,
    verificar_precios,
)


# ─── Prompt del dictamen final ────────────────────────────────────────────────

_PROMPT_DICTAMEN = """Eres un auditor senior experto en seguros automotrices con 15 años de experiencia.

FACTURA A AUDITAR:
{factura_json}

EXPEDIENTE DEL SINIESTRO:
{siniestro_json}

HALLAZGOS DE LOS MOTORES DE VERIFICACIÓN:
{discrepancias_json}

Con base en toda la información anterior, emite un dictamen de auditoría.
Responde SOLO con un objeto JSON, sin texto adicional:
{{
  "resultado": "APROBADA",
  "confianza": 0.95,
  "razonamiento": "Explicación concisa del dictamen (2-4 oraciones).",
  "recomendacion": "Acción específica sugerida al ajustador."
}}

Reglas para "resultado":
- "APROBADA":  sin discrepancias significativas y coherente con el siniestro.
- "OBSERVADA": 1-2 discrepancias menores o un precio ligeramente excedido.
- "RECHAZADA": múltiples discrepancias graves, duplicados, o ítems incoherentes con el siniestro.

Para "confianza" usa un valor entre 0.0 y 1.0 según tu certeza en el dictamen."""


# ─── Orquestador ─────────────────────────────────────────────────────────────

def auditar_factura(
    siniestro: dict,
    *,
    pdf_bytes: bytes | None = None,
    imagen_bytes: bytes | None = None,
    imagen_media_type: str = "image/jpeg",
    factura_json: dict | None = None,
    guardar: bool = True,
) -> dict:
    """
    Pipeline completo de auditoría.

    1. Extrae los datos de la factura (PDF, imagen o JSON directo).
    2. Ejecuta los tres motores de verificación.
    3. Pide a Claude el dictamen razonado.
    4. Construye y persiste el resultado final.

    Retorna el dict del dictamen.
    """

    # ── Paso 1: Extracción ────────────────────────────────────────────────────
    factura = extraer_factura(
        pdf_bytes=pdf_bytes,
        imagen_bytes=imagen_bytes,
        imagen_media_type=imagen_media_type,
        factura_json=factura_json,
    )

    fecha_factura: str = factura.get("fecha", datetime.now().strftime("%Y-%m-%d"))

    # ── Paso 2: Verificaciones ────────────────────────────────────────────────
    with get_db() as conn:
        disc_precios = verificar_precios(factura["items"], conn, fecha_factura)

    disc_duplicados = detectar_duplicados(factura["items"])
    resultado_coherencia = verificar_coherencia_siniestro(factura["items"], siniestro)
    disc_coherencia = resultado_coherencia.get("items_inconsistentes", [])

    todas_discrepancias = disc_precios + disc_duplicados + disc_coherencia

    # ── Paso 3: Dictamen Claude ───────────────────────────────────────────────
    client = get_client()
    prompt = _PROMPT_DICTAMEN.format(
        factura_json=json.dumps(factura, ensure_ascii=False, indent=2),
        siniestro_json=json.dumps(siniestro, ensure_ascii=False, indent=2),
        discrepancias_json=json.dumps(todas_discrepancias, ensure_ascii=False, indent=2),
    )

    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    dictamen_claude = _extraer_json(resp.text)

    # ── Paso 4: Ensamblar resultado ───────────────────────────────────────────
    monto_discrepancias = sum(
        d.get("diferencia", 0.0)
        for d in todas_discrepancias
        if d.get("tipo") == "precio_excedido"
    )

    items_observados = len(todas_discrepancias)
    items_aprobados = max(0, len(factura["items"]) - items_observados)

    confianza: float = float(dictamen_claude.get("confianza", 0.5))
    requiere_revision = (
        confianza < CONFIANZA_REVISION_HUMANA
        or monto_discrepancias > MONTO_REVISION_HUMANA
        or dictamen_claude.get("resultado") == "RECHAZADA"
    )

    dictamen = {
        "factura_id": factura.get("numero_factura", "SIN-NUMERO"),
        "siniestro_id": siniestro["id"],
        "resultado": dictamen_claude.get("resultado", "OBSERVADA"),
        "confianza": confianza,
        "items_aprobados": items_aprobados,
        "items_observados": items_observados,
        "monto_total_factura": float(factura.get("total_factura", 0.0)),
        "monto_discrepancias": round(monto_discrepancias, 2),
        "discrepancias": todas_discrepancias,
        "requiere_revision_humana": requiere_revision,
        "razonamiento": dictamen_claude.get("razonamiento", ""),
        "recomendacion": dictamen_claude.get("recomendacion", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # ── Paso 5: Persistencia ──────────────────────────────────────────────────
    if guardar:
        guardar_auditoria(dictamen)

    return dictamen
