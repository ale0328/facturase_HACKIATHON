"""
Datos sintéticos realistas para demostración.

Incluye:
- Tarifario con 30+ ítems del mercado automotriz mexicano.
- 3 siniestros de referencia.
- 3 facturas de demo con escenarios distintos:
    DEMO-001 → APROBADA   (todo en orden)
    DEMO-002 → OBSERVADA  (precios excedidos y duplicado)
    DEMO-003 → RECHAZADA  (ítems incoherentes + múltiples discrepancias)
"""

# ─── Tarifario ────────────────────────────────────────────────────────────────

TARIFARIO: list[dict] = [
    # Cristales
    {"codigo": "CRIS-001", "descripcion": "Parabrisas delantero OEM", "precio_min": 2800.00, "precio_max": 3200.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "CRIS-002", "descripcion": "Parabrisas delantero genérico", "precio_min": 1500.00, "precio_max": 1900.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "CRIS-003", "descripcion": "Vidrio lateral delantero izquierdo", "precio_min": 800.00, "precio_max": 1100.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "CRIS-004", "descripcion": "Vidrio lateral trasero derecho", "precio_min": 750.00, "precio_max": 1050.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Hojalatería
    {"codigo": "HOJ-001", "descripcion": "Cofre delantero", "precio_min": 2200.00, "precio_max": 3500.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "HOJ-002", "descripcion": "Defensa delantera", "precio_min": 1800.00, "precio_max": 2800.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "HOJ-003", "descripcion": "Salpicadera delantera derecha", "precio_min": 900.00, "precio_max": 1400.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "HOJ-004", "descripcion": "Salpicadera delantera izquierda", "precio_min": 900.00, "precio_max": 1400.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "HOJ-005", "descripcion": "Puerta delantera derecha completa", "precio_min": 3500.00, "precio_max": 5200.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "HOJ-006", "descripcion": "Fascia trasera", "precio_min": 1400.00, "precio_max": 2200.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Pintura
    {"codigo": "PIN-001", "descripcion": "Mano de obra pintura cofre", "precio_min": 800.00, "precio_max": 1200.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "PIN-002", "descripcion": "Mano de obra pintura salpicadera", "precio_min": 500.00, "precio_max": 800.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "PIN-003", "descripcion": "Mano de obra pintura puerta completa", "precio_min": 900.00, "precio_max": 1400.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "PIN-004", "descripcion": "Mano de obra pintura fascia", "precio_min": 600.00, "precio_max": 900.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "PIN-005", "descripcion": "Material de pintura (base + acabado)", "precio_min": 400.00, "precio_max": 650.00, "unidad": "litros", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Mecánica y suspensión
    {"codigo": "SUS-001", "descripcion": "Amortiguador delantero (c/u)", "precio_min": 1200.00, "precio_max": 1800.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "SUS-002", "descripcion": "Rotula inferior delantera (c/u)", "precio_min": 400.00, "precio_max": 650.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "SUS-003", "descripcion": "Mano de obra suspensión delantera", "precio_min": 600.00, "precio_max": 900.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "SUS-004", "descripcion": "Alineación y balanceo", "precio_min": 350.00, "precio_max": 500.00, "unidad": "servicio", "categoria": "servicio", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Iluminación
    {"codigo": "ILU-001", "descripcion": "Faro delantero derecho (asamblea completa)", "precio_min": 2200.00, "precio_max": 3200.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "ILU-002", "descripcion": "Faro delantero izquierdo (asamblea completa)", "precio_min": 2200.00, "precio_max": 3200.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "ILU-003", "descripcion": "Calavera trasera derecha", "precio_min": 600.00, "precio_max": 950.00, "unidad": "pieza", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Mano de obra general
    {"codigo": "MOG-001", "descripcion": "Hora taller general", "precio_min": 350.00, "precio_max": 550.00, "unidad": "hora", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "MOG-002", "descripcion": "Desmontaje y montaje cofre", "precio_min": 300.00, "precio_max": 450.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "MOG-003", "descripcion": "Desmontaje y montaje parabrisas", "precio_min": 400.00, "precio_max": 600.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "MOG-004", "descripcion": "Desmontaje y montaje defensa delantera", "precio_min": 250.00, "precio_max": 400.00, "unidad": "trabajo", "categoria": "mano_obra", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    # Consumibles
    {"codigo": "CON-001", "descripcion": "Silicón automotriz y selladores", "precio_min": 80.00, "precio_max": 150.00, "unidad": "kit", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "CON-002", "descripcion": "Abrasivos y lijas (set completo)", "precio_min": 120.00, "precio_max": 200.00, "unidad": "set", "categoria": "insumo", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
    {"codigo": "CON-003", "descripcion": "Limpieza y entrega del vehículo", "precio_min": 200.00, "precio_max": 350.00, "unidad": "servicio", "categoria": "servicio", "vigente_desde": "2024-01-01", "vigente_hasta": "2026-12-31"},
]


# ─── Siniestros ───────────────────────────────────────────────────────────────

SINIESTROS: list[dict] = [
    {
        "id": "SIN-2025-001",
        "tipo_accidente": "Colisión frontal",
        "partes_afectadas": ["cofre", "defensa delantera", "faros delanteros", "salpicadera delantera derecha", "parabrisas"],
        "vehiculo": "Nissan Versa 2022 Advance CVT, color blanco, placas ABC-123-4",
        "poliza": "POL-MX-00045231",
        "fecha_accidente": "2025-04-10",
        "descripcion": "El asegurado impactó frontalmente contra un muro de contención a baja velocidad. Daños concentrados en zona frontal: cofre, defensa, ambos faros y salpicadera derecha. El parabrisas presentó fractura diagonal.",
    },
    {
        "id": "SIN-2025-002",
        "tipo_accidente": "Impacto lateral",
        "partes_afectadas": ["puerta delantera derecha", "salpicadera trasera derecha", "vidrio lateral derecho"],
        "vehiculo": "Toyota Corolla 2021 LE, color gris, placas XYZ-789-0",
        "poliza": "POL-MX-00038710",
        "fecha_accidente": "2025-03-22",
        "descripcion": "Otro vehículo impactó el lateral derecho del asegurado en un crucero. Daños en puerta delantera derecha (deformación severa), salpicadera trasera derecha y vidrio lateral roto.",
    },
    {
        "id": "SIN-2025-003",
        "tipo_accidente": "Colisión trasera",
        "partes_afectadas": ["fascia trasera", "cajuela", "calaveras traseras"],
        "vehiculo": "Volkswagen Jetta 2023 Comfortline, color negro, placas DEF-456-7",
        "poliza": "POL-MX-00051892",
        "fecha_accidente": "2025-05-01",
        "descripcion": "El asegurado fue impactado por detrás en una vialidad rápida. Daños en fascia trasera (rotura), cajuela (deformación leve) y calavera trasera derecha fracturada.",
    },
]


# ─── Facturas demo ────────────────────────────────────────────────────────────

FACTURAS_DEMO: dict[str, dict] = {

    # ── DEMO-001: APROBADA ────────────────────────────────────────────────────
    # Siniestro SIN-2025-001 (colisión frontal)
    # Todo dentro del tarifario, sin duplicados, coherente con el siniestro.
    "DEMO-001": {
        "numero_factura": "FAC-2025-00341",
        "fecha": "2025-04-18",
        "taller": "Taller Automotriz Ramírez e Hijos",
        "rfc_taller": "TARH830512AB3",
        "items": [
            {"codigo": "HOJ-001", "descripcion": "Cofre delantero", "cantidad": 1, "precio_unitario": 3100.00, "total": 3100.00, "tipo": "insumo"},
            {"codigo": "HOJ-002", "descripcion": "Defensa delantera", "cantidad": 1, "precio_unitario": 2500.00, "total": 2500.00, "tipo": "insumo"},
            {"codigo": "ILU-001", "descripcion": "Faro delantero derecho (asamblea completa)", "cantidad": 1, "precio_unitario": 3000.00, "total": 3000.00, "tipo": "insumo"},
            {"codigo": "ILU-002", "descripcion": "Faro delantero izquierdo (asamblea completa)", "cantidad": 1, "precio_unitario": 3000.00, "total": 3000.00, "tipo": "insumo"},
            {"codigo": "HOJ-003", "descripcion": "Salpicadera delantera derecha", "cantidad": 1, "precio_unitario": 1200.00, "total": 1200.00, "tipo": "insumo"},
            {"codigo": "CRIS-001", "descripcion": "Parabrisas delantero OEM", "cantidad": 1, "precio_unitario": 3100.00, "total": 3100.00, "tipo": "insumo"},
            {"codigo": "PIN-001", "descripcion": "Mano de obra pintura cofre", "cantidad": 1, "precio_unitario": 1000.00, "total": 1000.00, "tipo": "mano_obra"},
            {"codigo": "PIN-002", "descripcion": "Mano de obra pintura salpicadera", "cantidad": 1, "precio_unitario": 700.00, "total": 700.00, "tipo": "mano_obra"},
            {"codigo": "MOG-002", "descripcion": "Desmontaje y montaje cofre", "cantidad": 1, "precio_unitario": 400.00, "total": 400.00, "tipo": "mano_obra"},
            {"codigo": "MOG-003", "descripcion": "Desmontaje y montaje parabrisas", "cantidad": 1, "precio_unitario": 550.00, "total": 550.00, "tipo": "mano_obra"},
            {"codigo": "MOG-004", "descripcion": "Desmontaje y montaje defensa delantera", "cantidad": 1, "precio_unitario": 350.00, "total": 350.00, "tipo": "mano_obra"},
            {"codigo": "PIN-005", "descripcion": "Material de pintura (base + acabado)", "cantidad": 2, "precio_unitario": 600.00, "total": 1200.00, "tipo": "insumo"},
            {"codigo": "CON-001", "descripcion": "Silicón automotriz y selladores", "cantidad": 1, "precio_unitario": 130.00, "total": 130.00, "tipo": "insumo"},
            {"codigo": "CON-002", "descripcion": "Abrasivos y lijas (set completo)", "cantidad": 1, "precio_unitario": 180.00, "total": 180.00, "tipo": "insumo"},
            {"codigo": "CON-003", "descripcion": "Limpieza y entrega del vehículo", "cantidad": 1, "precio_unitario": 300.00, "total": 300.00, "tipo": "servicio"},
        ],
        "total_factura": 20710.00,
    },

    # ── DEMO-002: OBSERVADA ───────────────────────────────────────────────────
    # Siniestro SIN-2025-002 (impacto lateral derecho)
    # 2 precios excedidos + 1 duplicado.
    "DEMO-002": {
        "numero_factura": "FAC-2025-00892",
        "fecha": "2025-04-01",
        "taller": "Carrocería & Pintura El Águila",
        "rfc_taller": "CAEA910320XY7",
        "items": [
            {"codigo": "HOJ-005", "descripcion": "Puerta delantera derecha completa", "cantidad": 1, "precio_unitario": 5800.00, "total": 5800.00, "tipo": "insumo"},   # excede max 5200
            {"codigo": "CRIS-003", "descripcion": "Vidrio lateral delantero izquierdo", "cantidad": 1, "precio_unitario": 1050.00, "total": 1050.00, "tipo": "insumo"},  # dentro del rango
            {"codigo": "PIN-003", "descripcion": "Mano de obra pintura puerta completa", "cantidad": 1, "precio_unitario": 1600.00, "total": 1600.00, "tipo": "mano_obra"},  # excede max 1400
            {"codigo": "PIN-003", "descripcion": "Mano de obra pintura puerta completa", "cantidad": 1, "precio_unitario": 1600.00, "total": 1600.00, "tipo": "mano_obra"},  # duplicado
            {"codigo": "MOG-001", "descripcion": "Hora taller general", "cantidad": 3, "precio_unitario": 500.00, "total": 1500.00, "tipo": "mano_obra"},
            {"codigo": "CON-002", "descripcion": "Abrasivos y lijas (set completo)", "cantidad": 1, "precio_unitario": 190.00, "total": 190.00, "tipo": "insumo"},
            {"codigo": "CON-003", "descripcion": "Limpieza y entrega del vehículo", "cantidad": 1, "precio_unitario": 320.00, "total": 320.00, "tipo": "servicio"},
        ],
        "total_factura": 12060.00,
    },

    # ── DEMO-003: RECHAZADA ───────────────────────────────────────────────────
    # Siniestro SIN-2025-003 (colisión trasera)
    # Ítems del motor y frenos que no corresponden a un choque trasero leve.
    # + precios excedidos + código no registrado.
    "DEMO-003": {
        "numero_factura": "FAC-2025-01147",
        "fecha": "2025-05-08",
        "taller": "Servicio Automotriz Velázquez",
        "rfc_taller": "SAVE780901CD2",
        "items": [
            {"codigo": "HOJ-006", "descripcion": "Fascia trasera", "cantidad": 1, "precio_unitario": 2100.00, "total": 2100.00, "tipo": "insumo"},
            {"codigo": "ILU-003", "descripcion": "Calavera trasera derecha", "cantidad": 1, "precio_unitario": 920.00, "total": 920.00, "tipo": "insumo"},
            {"codigo": "PIN-004", "descripcion": "Mano de obra pintura fascia", "cantidad": 1, "precio_unitario": 850.00, "total": 850.00, "tipo": "mano_obra"},
            # Ítems incoherentes: suspensión y frenos no corresponden a colisión trasera leve
            {"codigo": "SUS-001", "descripcion": "Amortiguador delantero (c/u)", "cantidad": 2, "precio_unitario": 1900.00, "total": 3800.00, "tipo": "insumo"},  # precio excedido + incoherente
            {"codigo": "SUS-003", "descripcion": "Mano de obra suspensión delantera", "cantidad": 1, "precio_unitario": 950.00, "total": 950.00, "tipo": "mano_obra"},  # precio excedido + incoherente
            {"codigo": "SUS-004", "descripcion": "Alineación y balanceo", "cantidad": 1, "precio_unitario": 480.00, "total": 480.00, "tipo": "servicio"},  # incoherente con daño trasero leve
            # Código no registrado en tarifario
            {"codigo": "MISC-999", "descripcion": "Diagnóstico electrónico avanzado", "cantidad": 1, "precio_unitario": 1200.00, "total": 1200.00, "tipo": "servicio"},
            {"codigo": "CON-003", "descripcion": "Limpieza y entrega del vehículo", "cantidad": 1, "precio_unitario": 350.00, "total": 350.00, "tipo": "servicio"},
        ],
        "total_factura": 10650.00,
    },
}


# Mapeo de qué factura demo corresponde a qué siniestro
DEMO_SINIESTRO_MAP: dict[str, str] = {
    "DEMO-001": "SIN-2025-001",
    "DEMO-002": "SIN-2025-002",
    "DEMO-003": "SIN-2025-003",
}
