from __future__ import annotations
"""
API REST con FastAPI.

Endpoints:
  POST /auditar          — Audita una factura (PDF upload o JSON demo).
  GET  /siniestros       — Lista los siniestros disponibles.
  GET  /siniestros/{id}  — Detalle de un siniestro.
  GET  /auditorias       — Historial de auditorías.
  GET  /health           — Health check.
"""
import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, listar_auditorias, listar_siniestros, obtener_siniestro
from app.orquestador import auditar_factura

app = FastAPI(
    title="Agente de Auditoría de Facturas",
    description="Auditoría automatizada de facturas de talleres automotrices mediante IA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    init_db()


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["sistema"])
def health():
    return {"status": "ok"}


# ─── Siniestros ───────────────────────────────────────────────────────────────

@app.get("/siniestros", tags=["siniestros"])
def get_siniestros():
    return listar_siniestros()


@app.get("/siniestros/{siniestro_id}", tags=["siniestros"])
def get_siniestro(siniestro_id: str):
    s = obtener_siniestro(siniestro_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Siniestro no encontrado")
    return s


# ─── Auditorías ───────────────────────────────────────────────────────────────

@app.get("/auditorias", tags=["auditorias"])
def get_auditorias(limit: int = 50):
    return listar_auditorias(limit)


# ─── Auditar ──────────────────────────────────────────────────────────────────

@app.post("/auditar", tags=["auditorias"])
async def auditar(
    siniestro_id: str = Form(..., description="ID del siniestro asociado"),
    factura_pdf: UploadFile | None = File(default=None, description="PDF de la factura (opcional)"),
    factura_json: str | None = Form(default=None, description="Factura en JSON (modo demo)"),
):
    """
    Audita una factura contra el siniestro y el tarifario.

    - Si se sube un PDF, Claude lo procesa con visión.
    - Si se pasa `factura_json` (string JSON), se usa directamente (modo demo).
    """
    siniestro = obtener_siniestro(siniestro_id)
    if siniestro is None:
        raise HTTPException(status_code=404, detail=f"Siniestro '{siniestro_id}' no encontrado")

    pdf_bytes = None
    factura_dict = None

    if factura_pdf is not None:
        pdf_bytes = await factura_pdf.read()
    elif factura_json is not None:
        try:
            factura_dict = json.loads(factura_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail=f"factura_json inválido: {exc}") from exc
    else:
        raise HTTPException(
            status_code=422,
            detail="Debes proveer 'factura_pdf' o 'factura_json'.",
        )

    try:
        dictamen = auditar_factura(
            siniestro,
            pdf_bytes=pdf_bytes,
            factura_json=factura_dict,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return dictamen
