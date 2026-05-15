"""
AuditaAuto — Dashboard Streamlit
Sistema de auditoría inteligente de facturas automotrices con IA.
"""
from __future__ import annotations

import json
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px

from app.database import (
    init_db,
    listar_auditorias,
    listar_siniestros,
    obtener_siniestro,
    crear_siniestro,
    eliminar_siniestro,
    listar_tarifario,
    agregar_item_tarifario,
    eliminar_item_tarifario,
)
from app.orquestador import auditar_factura
from data.demo_data import FACTURAS_DEMO, DEMO_SINIESTRO_MAP

# ─── Config ───────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AuditaAuto",
    page_icon="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzE4NTZiNCIgZD0iTTEyIDJMMyA3djVjMCA1LjU1IDMuODQgMTAuNzQgOSAxMiA1LjE2LTEuMjYgOS02LjQ1IDktMTJWN3oiLz48L3N2Zz4=",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# Forzar tema claro siempre
st._config.set_option("theme.base", "light")

init_db()

# ─── CSS global ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1b2d 0%, #1a2e4a 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .sidebar-brand {
    padding: 1.5rem 1rem 1rem 1rem;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 0.5rem;
}
[data-testid="stSidebar"] .sidebar-brand h1 {
    color: #ffffff !important;
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0.4rem 0 0.1rem 0;
    letter-spacing: -0.02em;
}
[data-testid="stSidebar"] .sidebar-brand p {
    color: #64748b !important;
    font-size: 0.75rem;
    margin: 0;
}
[data-testid="stSidebar"] .nav-section {
    padding: 0.25rem 0.75rem;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569 !important;
    margin-top: 1rem;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    text-align: left !important;
    padding: 0.55rem 1rem !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
}
[data-testid="metric-container"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    color: #64748b !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}
.page-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
}
.page-header h2 { margin:0; font-size:1.5rem; font-weight:700; color:#0f172a; }
.page-header p  { margin:0; font-size:0.85rem; color:#64748b; }
.badge { display:inline-flex; align-items:center; gap:0.4rem; padding:0.3rem 1rem; border-radius:9999px; font-weight:700; font-size:0.9rem; }
.badge-APROBADA  { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.badge-OBSERVADA { background:#fef9c3; color:#854d0e; border:1px solid #fde047; }
.badge-RECHAZADA { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }
.dictamen-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:16px;
    padding:1.5rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.06);
}
.alerta-revision {
    background:#fff7ed; border:1px solid #fed7aa; border-left:4px solid #f97316;
    border-radius:8px; padding:0.75rem 1rem; color:#9a3412; font-size:0.875rem; margin:0.75rem 0;
}
.alerta-ok {
    background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #22c55e;
    border-radius:8px; padding:0.75rem 1rem; color:#166534; font-size:0.875rem; margin:0.75rem 0;
}
@media (max-width: 768px) {
    .page-header h2 { font-size:1.2rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:1.2rem !important; }
}
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid #e2e8f0 !important; border-radius:10px !important; }
.stButton > button[kind="primary"] {
    background:#1856b4 !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
}
.stButton > button[kind="primary"]:hover { background:#1447a0 !important; }
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Constantes ───────────────────────────────────────────────────────────────

TIPO_DISC_LABEL = {
    "precio_excedido":      "Precio excedido",
    "codigo_no_encontrado": "Codigo no registrado",
    "duplicado":            "Item duplicado",
    "item_incoherente":     "Incoherente con siniestro",
}
CATEGORIAS_TAR = ["insumo", "mano_obra", "servicio"]
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36">
  <path fill="#3b82f6" d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7z"/>
  <path fill="white" d="M10 17l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9z"/>
</svg>"""
NAV_ITEMS = [
    ("auditar",    "Auditar Factura",  "&#x2713;"),
    ("historial",  "Historial",        "&#x1F4C4;"),
    ("metricas",   "Metricas",         "&#x1F4CA;"),
    ("siniestros", "Siniestros",       "&#x26A0;"),
    ("tarifario",  "Tarifario",        "&#x24;"),
]

# ─── Session state ────────────────────────────────────────────────────────────

if "pagina" not in st.session_state:
    st.session_state.pagina = "auditar"
if "modo_prueba" not in st.session_state:
    st.session_state.modo_prueba = False
if "mostrar_equipo" not in st.session_state:
    st.session_state.mostrar_equipo = False

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand">
        {LOGO_SVG}
        <h1>AuditaAuto</h1>
        <p>Sistema de auditoria inteligente</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Navegacion</div>', unsafe_allow_html=True)
    for key, label, icon in NAV_ITEMS:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.pagina = key
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="nav-section">Configuracion</div>', unsafe_allow_html=True)
    modo_prueba = st.toggle("Modo prueba", value=st.session_state.modo_prueba,
                            help="Muestra expedientes y facturas de demostracion precargadas")
    st.session_state.modo_prueba = modo_prueba
    if modo_prueba:
        st.markdown('<span style="font-size:0.72rem;color:#f59e0b">Datos de demo visibles</span>',
                    unsafe_allow_html=True)
    st.markdown("---")
    if st.button("&#x1F465;  Acerca del equipo", key="nav_equipo", use_container_width=True):
        st.session_state.mostrar_equipo = True
        st.rerun()
    st.markdown("""
    <a href="https://github.com/tomvargasd/facturase_HACKIATHON" target="_blank"
       style="display:flex;align-items:center;gap:0.5rem;padding:0.45rem 1rem;border-radius:8px;
              color:#94a3b8 !important;text-decoration:none;font-size:0.8rem;font-weight:500;
              transition:background 0.15s" 
       onmouseover="this.style.background='rgba(255,255,255,0.07)'"
       onmouseout="this.style.background='transparent'">
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="#94a3b8">
            <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
        </svg>
        Ver en GitHub
    </a>
    <div style="padding:0.4rem 1rem">
        <span style="font-size:0.7rem;color:#334155">v1.0.0 · Gemini 2.0 Flash</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Modal equipo ────────────────────────────────────────────────────────────

@st.dialog("HackIAThon — Equipo participante")
def modal_equipo():
    st.markdown("""
    <div style="text-align:center;padding:0.5rem 0 1.25rem 0">
        <div style="display:inline-block;background:#1856b4;border-radius:50%;width:56px;height:56px;line-height:56px;font-size:1.6rem;color:#fff;margin-bottom:0.75rem">H</div>
        <div style="font-size:1rem;font-weight:700;color:#0f172a">HackIAThon 2026</div>
        <div style="font-size:0.8rem;color:#64748b;margin-top:0.2rem">Esta solucion fue desarrollada como parte de la prueba oficial del HackIAThon.</div>
    </div>
    <hr style="border:none;border-top:1px solid #e2e8f0;margin:0.5rem 0 1rem 0">
    <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#94a3b8;margin-bottom:0.75rem">Integrantes del equipo</div>
    """, unsafe_allow_html=True)

    miembros = [
        ("Lider",   "Tomas Vargas Drouet",    "tomvargasd@gmail.com"),
        ("Miembro", "Alexa Granizo Ramirez",   "alexagranizo06@gmail.com"),
        ("Miembro", "Angie Granizo Ramirez",   "angiegranizor@gmail.com"),
    ]
    for rol, nombre, correo in miembros:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.75rem;padding:0.6rem 0.75rem;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:0.5rem">
            <div style="flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#dbeafe;display:flex;align-items:center;justify-content:center;font-weight:700;color:#1856b4;font-size:0.9rem">{nombre[0]}</div>
            <div style="flex:1;min-width:0">
                <div style="font-weight:600;color:#0f172a;font-size:0.875rem">{nombre} {'<span style="background:#dcfce7;color:#166534;font-size:0.65rem;font-weight:700;padding:1px 7px;border-radius:9999px;margin-left:6px;vertical-align:middle">LIDER</span>' if rol=='Lider' else ''}</div>
                <div style="font-size:0.78rem;color:#64748b;margin-top:1px">
                    <a href="mailto:{correo}" style="color:#1856b4;text-decoration:none">{correo}</a>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1rem;padding:0.75rem 1rem;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;display:flex;align-items:center;gap:0.75rem">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#25d366"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.124.558 4.118 1.528 5.845L0 24l6.335-1.507A11.945 11.945 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.898 0-3.664-.53-5.166-1.44l-.371-.22-3.762.895.942-3.655-.242-.38A9.945 9.945 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
        <div>
            <div style="font-size:0.75rem;font-weight:600;color:#166534">Contacto del equipo</div>
            <a href="https://wa.me/593960745756" target="_blank" style="font-size:0.85rem;color:#25d366;font-weight:700;text-decoration:none">+593 960 745 756 (WhatsApp)</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.mostrar_equipo:
    modal_equipo()
    st.session_state.mostrar_equipo = False

# ─── Helpers UI ───────────────────────────────────────────────────────────────

def page_header(title, subtitle, icon_svg):
    st.markdown(f"""
    <div class="page-header">
        {icon_svg}
        <div><h2>{title}</h2><p>{subtitle}</p></div>
    </div>""", unsafe_allow_html=True)

def badge_resultado(resultado):
    icons = {"APROBADA": "✓", "OBSERVADA": "!", "RECHAZADA": "✕"}
    return f'<span class="badge badge-{resultado}">{icons.get(resultado,"")} {resultado}</span>'

def render_dictamen(dictamen):
    resultado = dictamen["resultado"]
    st.markdown(f"""
    <div class="dictamen-card">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem">
            <div>
                <div style="font-size:0.75rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.25rem">Dictamen</div>
                {badge_resultado(resultado)}
            </div>
            <div style="text-align:right;font-size:0.8rem;color:#94a3b8">
                Factura: <strong style="color:#0f172a">{dictamen.get('factura_id','—')}</strong><br>
                Siniestro: <strong style="color:#0f172a">{dictamen.get('siniestro_id','—')}</strong>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Confianza IA",      f"{dictamen['confianza']:.0%}")
    c2.metric("Items aprobados",   dictamen["items_aprobados"])
    c3.metric("Items observados",  dictamen["items_observados"])
    c4.metric("Discrepancias $",   f"${dictamen['monto_discrepancias']:,.2f}")

    if dictamen["requiere_revision_humana"]:
        st.markdown('<div class="alerta-revision"><strong>Requiere revision humana</strong> — Este caso debe ser revisado por un ajustador antes de proceder.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alerta-ok"><strong>Sin revision adicional requerida</strong> — El dictamen puede procesarse automaticamente.</div>', unsafe_allow_html=True)

    with st.expander("Razonamiento del agente", expanded=True):
        st.write(dictamen["razonamiento"])
        st.info(f"**Recomendacion:** {dictamen['recomendacion']}")

    discs = dictamen.get("discrepancias", [])
    if discs:
        st.subheader("Discrepancias detectadas")
        rows = []
        for d in discs:
            tipo = TIPO_DISC_LABEL.get(d.get("tipo",""), d.get("tipo",""))
            item = d.get("item") or d.get("descripcion") or d.get("codigo","")
            if d.get("tipo") == "precio_excedido":
                det = f"Cobrado ${d['cobrado']:,.2f} / Max ${d['tarifario_max']:,.2f} / Dif ${d['diferencia']:,.2f}"
            elif d.get("tipo") == "duplicado":
                det = f"Aparece {d['ocurrencias']} veces"
            elif d.get("tipo") == "codigo_no_encontrado":
                det = f"Codigo: {d.get('codigo','')}"
            else:
                det = d.get("razon","")
            rows.append({"Tipo": tipo, "Item": item, "Detalle": det})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        tipo_counts = pd.Series([d.get("tipo","") for d in discs]).value_counts()
        tipo_counts.index = [TIPO_DISC_LABEL.get(t,t) for t in tipo_counts.index]
        fig = px.pie(values=tipo_counts.values, names=tipo_counts.index,
                     color_discrete_sequence=["#ef4444","#f59e0b","#3b82f6","#a855f7"], hole=0.45)
        fig.update_layout(height=260, margin=dict(t=10,b=10,l=10,r=10),
                          legend=dict(orientation="h",y=-0.15))
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div class="alerta-ok">Sin discrepancias detectadas en esta factura.</div>', unsafe_allow_html=True)

    with st.expander("JSON completo del dictamen"):
        st.json(dictamen)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════════════════════

pagina = st.session_state.pagina

# ─── Auditar ──────────────────────────────────────────────────────────────────
if pagina == "auditar":
    page_header("Auditar Factura",
                "Analiza una factura de taller contra el tarifario y el expediente del siniestro",
                '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>')

    siniestros = listar_siniestros()
    siniestros_visibles = siniestros if st.session_state.modo_prueba else [
        s for s in siniestros if not s["id"].startswith("SIN-2025")
    ] or siniestros

    if not siniestros_visibles:
        st.warning("No hay siniestros disponibles. Activa el **Modo prueba** o registra uno en la seccion Siniestros.")
        st.stop()

    st.markdown("#### 1. Expediente del siniestro")
    labels = {s["id"]: f"{s['id']} — {s['tipo_accidente']} · {s['vehiculo'][:45]}" for s in siniestros_visibles}
    siniestro_id = st.selectbox("Expediente", options=list(labels.keys()),
                                format_func=lambda x: labels[x], label_visibility="collapsed")
    siniestro = obtener_siniestro(siniestro_id)
    if siniestro:
        with st.expander("Ver detalle del expediente"):
            ca, cb = st.columns(2)
            ca.markdown(f"**Vehiculo:** {siniestro['vehiculo']}")
            ca.markdown(f"**Tipo:** {siniestro['tipo_accidente']}")
            ca.markdown(f"**Fecha:** {siniestro['fecha_accidente']}")
            cb.markdown(f"**Poliza:** {siniestro['poliza']}")
            cb.markdown(f"**Partes afectadas:** {', '.join(siniestro['partes_afectadas'])}")
            st.markdown(f"**Descripcion:** {siniestro['descripcion']}")

    st.markdown("#### 2. Factura a auditar")
    tab_pdf, tab_demo = st.tabs(["Subir PDF", "Factura de demostracion"])
    factura_json = None
    pdf_bytes = None

    with tab_pdf:
        uploaded = st.file_uploader("Archivo PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            pdf_bytes = uploaded.read()
            st.success(f"Archivo listo: {uploaded.name}  ({len(pdf_bytes):,} bytes)")

    with tab_demo:
        if not st.session_state.modo_prueba:
            st.info("Activa el **Modo prueba** en el sidebar para ver las facturas de demostracion.")
        else:
            demo_key = st.selectbox(
                "Factura demo", options=list(FACTURAS_DEMO.keys()),
                format_func=lambda k: f"{k} — {FACTURAS_DEMO[k]['numero_factura']} ({FACTURAS_DEMO[k]['taller']})",
                label_visibility="collapsed",
            )
            if demo_key in DEMO_SINIESTRO_MAP and DEMO_SINIESTRO_MAP[demo_key] != siniestro_id:
                st.warning(f"Esta factura demo corresponde al siniestro {DEMO_SINIESTRO_MAP[demo_key]}.")
            fp = FACTURAS_DEMO[demo_key]
            with st.expander(f"Vista previa: {fp['numero_factura']}"):
                df_prev = pd.DataFrame(fp["items"])
                df_prev.columns = ["Codigo","Descripcion","Cantidad","P. Unitario","Total","Tipo"]
                df_prev["P. Unitario"] = df_prev["P. Unitario"].apply(lambda x: f"${x:,.2f}")
                df_prev["Total"] = df_prev["Total"].apply(lambda x: f"${x:,.2f}")
                st.dataframe(df_prev, use_container_width=True, hide_index=True)
                st.metric("Total factura", f"${fp['total_factura']:,.2f}")
            factura_json = FACTURAS_DEMO[demo_key]

    st.markdown("#### 3. Ejecutar")
    if st.button("Ejecutar auditoria", type="primary", use_container_width=True):
        if factura_json is None and pdf_bytes is None:
            st.error("Selecciona una factura demo o sube un PDF.")
        else:
            with st.spinner("Analizando con IA..."):
                try:
                    dictamen = auditar_factura(siniestro, pdf_bytes=pdf_bytes, factura_json=factura_json)
                    st.session_state["ultimo_dictamen"] = dictamen
                except Exception as e:
                    st.error(f"Error durante la auditoria: {e}")
                    st.exception(e)

    if "ultimo_dictamen" in st.session_state:
        st.divider()
        render_dictamen(st.session_state["ultimo_dictamen"])

# ─── Historial ────────────────────────────────────────────────────────────────
elif pagina == "historial":
    page_header("Historial de Auditorias",
                "Registro completo de todas las auditorias ejecutadas",
                '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>')

    auditorias = listar_auditorias()
    if not auditorias:
        st.info("Aun no se han realizado auditorias.")
    else:
        rows = [{
            "#": a["id"], "Factura": a["factura_id"], "Siniestro": a["siniestro_id"],
            "Resultado": a["resultado"], "Confianza": f"{a['confianza']:.0%}",
            "Disc.": a["items_observados"], "Total": f"${a['monto_total_factura']:,.2f}",
            "Dif. $": f"${a['monto_discrepancias']:,.2f}",
            "Rev. humana": "Si" if a["requiere_revision_humana"] else "No",
            "Fecha": a["timestamp"][:19].replace("T"," "),
        } for a in auditorias]
        df = pd.DataFrame(rows)

        def _color(val):
            m = {"APROBADA":"background:#dcfce7;color:#166534",
                 "OBSERVADA":"background:#fef9c3;color:#854d0e",
                 "RECHAZADA":"background:#fee2e2;color:#991b1b"}
            return m.get(val,"")

        st.dataframe(df.style.applymap(_color, subset=["Resultado"]),
                     use_container_width=True, hide_index=True)

        sel_id = st.selectbox("Ver detalle", [a["id"] for a in auditorias],
                              format_func=lambda x: f"#{x} — {next(a['factura_id'] for a in auditorias if a['id']==x)}")
        if sel_id:
            render_dictamen(next(a for a in auditorias if a["id"] == sel_id))

# ─── Métricas ─────────────────────────────────────────────────────────────────
elif pagina == "metricas":
    page_header("Metricas del Sistema",
                "Indicadores de desempeno del agente de auditoria",
                '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>')

    auditorias = listar_auditorias(500)
    if not auditorias:
        st.info("Aun no hay datos suficientes.")
    else:
        total      = len(auditorias)
        aprobadas  = sum(1 for a in auditorias if a["resultado"] == "APROBADA")
        observadas = sum(1 for a in auditorias if a["resultado"] == "OBSERVADA")
        rechazadas = sum(1 for a in auditorias if a["resultado"] == "RECHAZADA")
        ahorro     = sum(a["monto_discrepancias"] for a in auditorias)
        rev_hum    = sum(1 for a in auditorias if a["requiere_revision_humana"])

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Total auditadas", total)
        c2.metric("Aprobadas",  aprobadas,  f"{aprobadas/total:.0%}")
        c3.metric("Observadas", observadas, f"{observadas/total:.0%}")
        c4.metric("Rechazadas", rechazadas, f"{rechazadas/total:.0%}")
        c5.metric("Rev. humana", rev_hum)
        c6.metric("Ahorro detectado", f"${ahorro:,.0f}")

        st.divider()
        cl, cr = st.columns(2)
        with cl:
            fig_pie = px.pie(
                values=[aprobadas,observadas,rechazadas],
                names=["Aprobada","Observada","Rechazada"],
                color_discrete_map={"Aprobada":"#22c55e","Observada":"#f59e0b","Rechazada":"#ef4444"},
                hole=0.45, title="Distribucion de resultados",
            )
            fig_pie.update_layout(height=300, margin=dict(t=40,b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        with cr:
            df_conf = pd.DataFrame([{"Resultado":a["resultado"],"Confianza":a["confianza"]} for a in auditorias])
            fig_box = px.box(df_conf, x="Resultado", y="Confianza", color="Resultado",
                             color_discrete_map={"APROBADA":"#22c55e","OBSERVADA":"#f59e0b","RECHAZADA":"#ef4444"},
                             title="Confianza por resultado")
            fig_box.update_layout(height=300, margin=dict(t=40,b=10), showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)

        tipo_counts: dict = {}
        for a in auditorias:
            for d in a.get("discrepancias",[]):
                t = TIPO_DISC_LABEL.get(d.get("tipo",""), d.get("tipo",""))
                tipo_counts[t] = tipo_counts.get(t,0) + 1
        if tipo_counts:
            st.subheader("Tipos de discrepancia mas frecuentes")
            fig_bar = px.bar(x=list(tipo_counts.keys()), y=list(tipo_counts.values()),
                             labels={"x":"Tipo","y":"Frecuencia"},
                             color=list(tipo_counts.values()),
                             color_continuous_scale=["#fef9c3","#f97316","#ef4444"])
            fig_bar.update_layout(height=300, coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

# ─── Siniestros ───────────────────────────────────────────────────────────────
elif pagina == "siniestros":
    page_header("Gestion de Siniestros",
                "Registra, consulta y administra los expedientes de siniestros",
                '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>')

    tab_lista, tab_nuevo = st.tabs(["Lista de siniestros", "Registrar nuevo"])

    with tab_lista:
        siniestros = listar_siniestros()
        visibles = siniestros if st.session_state.modo_prueba else [
            s for s in siniestros if not s["id"].startswith("SIN-2025")
        ]
        if not visibles:
            st.info("No hay siniestros registrados. Usa 'Registrar nuevo' o activa el Modo prueba.")
        else:
            rows = [{"ID":s["id"],"Tipo":s["tipo_accidente"],"Vehiculo":s["vehiculo"][:50],
                     "Poliza":s["poliza"],"Fecha":s["fecha_accidente"],
                     "Partes afectadas":", ".join(s["partes_afectadas"])} for s in visibles]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with st.expander("Ver detalle de un siniestro"):
                sid = st.selectbox("Seleccionar", [s["id"] for s in visibles], key="sel_sin_detail")
                s = obtener_siniestro(sid)
                if s:
                    ca, cb = st.columns(2)
                    ca.markdown(f"**ID:** {s['id']}")
                    ca.markdown(f"**Tipo:** {s['tipo_accidente']}")
                    ca.markdown(f"**Fecha:** {s['fecha_accidente']}")
                    cb.markdown(f"**Vehiculo:** {s['vehiculo']}")
                    cb.markdown(f"**Poliza:** {s['poliza']}")
                    st.markdown(f"**Partes afectadas:** {', '.join(s['partes_afectadas'])}")
                    st.markdown(f"**Descripcion:** {s['descripcion']}")

            st.markdown("---")
            with st.expander("Eliminar siniestro"):
                sid_del = st.selectbox("Siniestro a eliminar", [s["id"] for s in visibles], key="sel_sin_del")
                if st.button("Eliminar siniestro", type="primary", key="btn_del_sin"):
                    eliminar_siniestro(sid_del)
                    st.success(f"Siniestro {sid_del} eliminado.")
                    st.rerun()

    with tab_nuevo:
        with st.form("form_nuevo_siniestro", clear_on_submit=True):
            st.markdown("##### Datos del expediente")
            c1, c2 = st.columns(2)
            nuevo_id     = c1.text_input("ID del siniestro *", placeholder="SIN-2026-001")
            nueva_poliza = c2.text_input("Numero de poliza *", placeholder="POL-MX-00012345")
            c3, c4 = st.columns(2)
            tipo_acc  = c3.selectbox("Tipo de accidente *", [
                "Colision frontal","Colision trasera","Impacto lateral",
                "Volcadura","Robo parcial","Granizo","Inundacion","Otro"])
            fecha_acc = c4.date_input("Fecha del accidente *", value=date.today())
            vehiculo_str = st.text_input("Descripcion del vehiculo *",
                                         placeholder="Toyota Corolla 2023 LE, color blanco, placas ABC-123")
            partes_str = st.text_input("Partes afectadas (separadas por coma) *",
                                       placeholder="cofre, defensa delantera, faro derecho")
            descripcion_str = st.text_area("Descripcion del accidente",
                                           placeholder="Describe brevemente como ocurrio el siniestro...",
                                           height=100)
            submitted = st.form_submit_button("Registrar siniestro", type="primary", use_container_width=True)
            if submitted:
                errs = []
                if not nuevo_id.strip():      errs.append("El ID es obligatorio.")
                if not nueva_poliza.strip():  errs.append("La poliza es obligatoria.")
                if not vehiculo_str.strip():  errs.append("El vehiculo es obligatorio.")
                if not partes_str.strip():    errs.append("Las partes afectadas son obligatorias.")
                if obtener_siniestro(nuevo_id.strip()):
                    errs.append(f"Ya existe un siniestro con ID '{nuevo_id.strip()}'.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    partes = [p.strip() for p in partes_str.split(",") if p.strip()]
                    crear_siniestro({
                        "id": nuevo_id.strip(),
                        "tipo_accidente": tipo_acc,
                        "partes_afectadas": partes,
                        "vehiculo": vehiculo_str.strip(),
                        "poliza": nueva_poliza.strip(),
                        "fecha_accidente": str(fecha_acc),
                        "descripcion": descripcion_str.strip(),
                    })
                    st.success(f"Siniestro **{nuevo_id.strip()}** registrado correctamente.")
                    st.rerun()

# ─── Tarifario ────────────────────────────────────────────────────────────────
elif pagina == "tarifario":
    page_header("Gestion del Tarifario",
                "Administra los precios de referencia para la auditoria de facturas",
                '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1856b4" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>')

    tab_ver, tab_nuevo, tab_eliminar = st.tabs(["Lista de precios", "Agregar item", "Eliminar item"])

    with tab_ver:
        items = listar_tarifario()
        if not items:
            st.info("El tarifario esta vacio.")
        else:
            cat_filter = st.selectbox("Filtrar por categoria", ["Todas"] + CATEGORIAS_TAR, key="tar_filter")
            df_tar = pd.DataFrame(items)
            if cat_filter != "Todas":
                df_tar = df_tar[df_tar["categoria"] == cat_filter]
            df_tar = df_tar.rename(columns={
                "codigo":"Codigo","descripcion":"Descripcion",
                "precio_min":"P. Min","precio_max":"P. Max",
                "unidad":"Unidad","categoria":"Categoria",
                "vigente_desde":"Desde","vigente_hasta":"Hasta",
            })
            df_tar["P. Min"] = df_tar["P. Min"].apply(lambda x: f"${x:,.2f}")
            df_tar["P. Max"] = df_tar["P. Max"].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_tar, use_container_width=True, hide_index=True)
            st.caption(f"{len(df_tar)} items mostrados")

    with tab_nuevo:
        with st.form("form_nuevo_tar", clear_on_submit=True):
            st.markdown("##### Nuevo item en el tarifario")
            c1, c2 = st.columns(2)
            tar_cod  = c1.text_input("Codigo *", placeholder="HOJ-007")
            tar_desc = c2.text_input("Descripcion *", placeholder="Tapa de cajuela")
            c3, c4, c5 = st.columns(3)
            tar_pmin = c3.number_input("Precio minimo *", min_value=0.0, step=50.0, format="%.2f")
            tar_pmax = c4.number_input("Precio maximo *", min_value=0.0, step=50.0, format="%.2f")
            tar_uni  = c5.text_input("Unidad", value="pieza")
            c6, c7, c8 = st.columns(3)
            tar_cat   = c6.selectbox("Categoria *", CATEGORIAS_TAR)
            tar_desde = c7.date_input("Vigente desde", value=date.today())
            tar_hasta = c8.date_input("Vigente hasta", value=date(2026,12,31))
            sub_tar = st.form_submit_button("Agregar al tarifario", type="primary", use_container_width=True)
            if sub_tar:
                errs = []
                if not tar_cod.strip():  errs.append("El codigo es obligatorio.")
                if not tar_desc.strip(): errs.append("La descripcion es obligatoria.")
                if tar_pmax <= 0:        errs.append("El precio maximo debe ser mayor a 0.")
                if tar_pmax < tar_pmin:  errs.append("El precio maximo no puede ser menor al minimo.")
                if errs:
                    for e in errs: st.error(e)
                else:
                    agregar_item_tarifario({
                        "codigo":       tar_cod.strip().upper(),
                        "descripcion":  tar_desc.strip(),
                        "precio_min":   tar_pmin,
                        "precio_max":   tar_pmax,
                        "unidad":       tar_uni.strip() or "pieza",
                        "categoria":    tar_cat,
                        "vigente_desde": str(tar_desde),
                        "vigente_hasta": str(tar_hasta),
                    })
                    st.success(f"Item **{tar_cod.strip().upper()}** agregado al tarifario.")
                    st.rerun()

    with tab_eliminar:
        items = listar_tarifario()
        if not items:
            st.info("El tarifario esta vacio.")
        else:
            cod_del = st.selectbox(
                "Seleccionar item a eliminar", [i["codigo"] for i in items],
                format_func=lambda c: f"{c} — {next(i['descripcion'] for i in items if i['codigo']==c)}",
            )
            st.warning(f"Esta accion eliminara permanentemente el item **{cod_del}** del tarifario.")
            if st.button("Eliminar item", type="primary", key="btn_del_tar"):
                eliminar_item_tarifario(cod_del)
                st.success(f"Item {cod_del} eliminado.")
                st.rerun()
