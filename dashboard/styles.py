def rawStyles():
    return """
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090f1a 0%, #0d1829 40%, #0b1422 100%) !important;
    border-right: 1px solid #162236;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #8fadc8 !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: transparent !important; border: none !important;
    color: #5a7d9a !important; text-align: left !important;
    padding: 0.58rem 1.4rem !important; border-radius: 0 !important;
    font-size: 0.84rem !important; font-weight: 500 !important;
    transition: all 0.12s ease !important; margin-bottom: 0 !important;
    border-left: 3px solid transparent !important; letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59,130,246,0.08) !important;
    color: #c8ddf0 !important; border-left-color: #3b82f6 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1rem 1.25rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.74rem !important; color: #64748b !important;
    font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important; font-weight: 700 !important; color: #0f172a !important;
}

/* ── Page elements ── */
.page-header {
    display: flex; align-items: center; gap: 0.75rem;
    margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #e2e8f0;
}
.page-header h2 { margin:0; font-size:1.35rem; font-weight:700; color:#0f172a; }
.page-header p  { margin:0; font-size:0.82rem; color:#64748b; }

.badge { display:inline-flex; align-items:center; gap:0.35rem; padding:0.28rem 0.9rem; border-radius:9999px; font-weight:700; font-size:0.84rem; }
.badge-APROBADA  { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.badge-OBSERVADA { background:#fef9c3; color:#854d0e; border:1px solid #fde047; }
.badge-RECHAZADA { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }

.dictamen-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:14px;
    padding:1.25rem; margin-bottom:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.alerta-revision {
    background:#fff7ed; border:1px solid #fed7aa; border-left:4px solid #f97316;
    border-radius:8px; padding:0.65rem 1rem; color:#9a3412; font-size:0.85rem; margin:0.6rem 0;
}
.alerta-ok {
    background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #22c55e;
    border-radius:8px; padding:0.65rem 1rem; color:#166534; font-size:0.85rem; margin:0.6rem 0;
}
.quick-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:1.1rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);
    margin-bottom:0.25rem;
}
.queue-item {
    background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
    padding:0.65rem 1rem; margin-bottom:0.4rem;
}

/* ── Login ── */
.login-card {
    background:#fff; border-radius:20px; padding:2.5rem 2rem;
    box-shadow:0 20px 60px rgba(0,0,0,0.10); border:1px solid #e2e8f0;
}

/* ── Misc ── */
@media (max-width:768px) {
    .page-header h2 { font-size:1.1rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size:1.1rem !important; }
}
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
[data-testid="stExpander"]  { border:1px solid #e2e8f0 !important; border-radius:10px !important; }
.stButton > button[kind="primary"] {
    background:#1856b4 !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
}
.stButton > button[kind="primary"]:hover { background:#1447a0 !important; }
#MainMenu, footer { visibility:hidden; }

.altbuton .stButton > button[kind="secondary"]{
    background: #3b82f6!important;;
    color: #ffffff!important;
}
.navmenu button div{
    display: inline!important;
}

</style>
"""