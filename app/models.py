from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime


# ─── Tarifario ────────────────────────────────────────────────────────────────

class ItemTarifario(BaseModel):
    codigo: str
    descripcion: str
    precio_min: float
    precio_max: float
    unidad: str
    categoria: Literal["insumo", "mano_obra", "servicio"]
    vigente_desde: date
    vigente_hasta: date


# ─── Siniestro ────────────────────────────────────────────────────────────────

class Siniestro(BaseModel):
    id: str
    tipo_accidente: str
    partes_afectadas: list[str]
    vehiculo: str
    poliza: str
    fecha_accidente: date
    descripcion: str


# ─── Factura ──────────────────────────────────────────────────────────────────

class ItemFactura(BaseModel):
    codigo: str
    descripcion: str
    cantidad: float
    precio_unitario: float
    total: float
    tipo: Literal["insumo", "mano_obra", "servicio"]


class Factura(BaseModel):
    numero_factura: str
    fecha: date
    taller: str
    rfc_taller: Optional[str] = None
    items: list[ItemFactura]
    total_factura: float


# ─── Discrepancias ────────────────────────────────────────────────────────────

class DiscrepanciaPrecio(BaseModel):
    tipo: Literal["precio_excedido"] = "precio_excedido"
    item: str
    codigo: str
    cobrado: float
    tarifario_max: float
    diferencia: float


class DiscrepanciaCodigo(BaseModel):
    tipo: Literal["codigo_no_encontrado"] = "codigo_no_encontrado"
    item: str
    codigo: str


class DiscrepanciaDuplicado(BaseModel):
    tipo: Literal["duplicado"] = "duplicado"
    codigo: str
    descripcion: str
    ocurrencias: int


class DiscrepanciaCoherencia(BaseModel):
    tipo: Literal["item_incoherente"] = "item_incoherente"
    item: str
    razon: str


# ─── Dictamen ─────────────────────────────────────────────────────────────────

class Dictamen(BaseModel):
    factura_id: str
    siniestro_id: str
    resultado: Literal["APROBADA", "OBSERVADA", "RECHAZADA"]
    confianza: float = Field(ge=0.0, le=1.0)
    items_aprobados: int
    items_observados: int
    monto_total_factura: float
    monto_discrepancias: float
    discrepancias: list[dict]
    requiere_revision_humana: bool
    razonamiento: str
    recomendacion: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ─── Request/Response API ─────────────────────────────────────────────────────

class AuditarRequest(BaseModel):
    siniestro_id: str
    factura_json: Optional[dict] = None  # Para modo demo (sin PDF)


class AuditarResponse(BaseModel):
    ok: bool
    dictamen: Optional[Dictamen] = None
    error: Optional[str] = None
