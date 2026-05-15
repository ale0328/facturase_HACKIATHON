from __future__ import annotations
"""
Extracción de datos de facturas.

Soporta dos modos:
- PDF/imagen: envía el archivo a Gemini con visión para extracción OCR.
- JSON directo: para demos y tests, acepta un dict ya estructurado.

Incluye parsing JSON defensivo: extrae el bloque JSON del texto de Gemini
aunque éste agregue texto introductorio o conclusivo.
"""
import json
import re

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL

# Cliente singleton para reutilizar la conexión HTTP
_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


# ─── Parser defensivo ─────────────────────────────────────────────────────────

def _extraer_json(texto: str) -> dict:
    """
    Extrae el primer bloque JSON válido del texto.
    Maneja los casos en que Claude agrega texto antes/después del JSON.
    """
    # Intento directo
    try:
        return json.loads(texto.strip())
    except json.JSONDecodeError:
        pass

    # Busca bloque ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Busca el primer { ... } balanceado
    start = texto.find("{")
    if start == -1:
        raise ValueError(f"No se encontró JSON en la respuesta de Gemini:\n{texto[:300]}")

    depth = 0
    for i, ch in enumerate(texto[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(texto[start : i + 1])
                except json.JSONDecodeError:
                    break

    raise ValueError(f"JSON malformado en respuesta de Gemini:\n{texto[:300]}")


# ─── Extracción desde PDF/imagen ──────────────────────────────────────────────

_PROMPT_EXTRACCION = """Extrae todos los ítems de esta factura de taller automotriz.
Devuelve SOLO un objeto JSON con la siguiente estructura, sin texto adicional:
{
  "numero_factura": "...",
  "fecha": "YYYY-MM-DD",
  "taller": "...",
  "rfc_taller": "...",
  "items": [
    {
      "codigo": "código o SKU del ítem",
      "descripcion": "descripción del ítem",
      "cantidad": 1,
      "precio_unitario": 0.00,
      "total": 0.00,
      "tipo": "insumo|mano_obra|servicio"
    }
  ],
  "total_factura": 0.00
}
Si algún campo no está disponible en el documento usa null.
Para "tipo" clasifica: insumo=piezas/materiales, mano_obra=horas taller, servicio=otros servicios."""


def extraer_items_factura_pdf(pdf_bytes: bytes) -> dict:
    """Extrae ítems de un PDF usando Gemini con visión."""
    client = get_client()
    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            _PROMPT_EXTRACCION,
        ],
    )
    return _extraer_json(respuesta.text)


def extraer_items_factura_imagen(imagen_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    """Extrae ítems de una imagen (JPG/PNG) usando Gemini con visión."""
    client = get_client()
    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=imagen_bytes, mime_type=media_type),
            _PROMPT_EXTRACCION,
        ],
    )
    return _extraer_json(respuesta.text)


def extraer_items_factura_json(factura_dict: dict) -> dict:
    """
    Modo demo/test: recibe el dict ya estructurado y lo devuelve normalizado.
    No consume tokens de Claude para extracción.
    """
    return factura_dict


def extraer_factura(
    *,
    pdf_bytes: bytes | None = None,
    imagen_bytes: bytes | None = None,
    imagen_media_type: str = "image/jpeg",
    factura_json: dict | None = None,
) -> dict:
    """
    Punto de entrada unificado para extraer datos de una factura.
    Prioridad: factura_json > pdf_bytes > imagen_bytes.
    """
    if factura_json is not None:
        return extraer_items_factura_json(factura_json)
    if pdf_bytes is not None:
        return extraer_items_factura_pdf(pdf_bytes)
    if imagen_bytes is not None:
        return extraer_items_factura_imagen(imagen_bytes, imagen_media_type)
    raise ValueError("Debes proveer pdf_bytes, imagen_bytes o factura_json.")
