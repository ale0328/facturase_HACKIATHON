# Agente de Auditoría de Facturas — IA con Claude

Pipeline automatizado que usa Claude (Anthropic) para auditar facturas de talleres automotrices contra el tarifario y el expediente del siniestro, emitiendo un dictamen estructurado antes de que el ajustador humano intervenga.

---

## Arquitectura

```
Factura (PDF / JSON)
        │
        ▼
┌───────────────────┐
│   Extractor       │  Claude Vision → JSON estructurado
└────────┬──────────┘
         │
    ┌────┴────────────────────────────────┐
    │                                     │
    ▼                                     ▼
Motor de Precios              Motor de Duplicados
(vs. tarifario SQLite)        (Counter por código)
    │                                     │
    └──────────────┬──────────────────────┘
                   │
                   ▼
         Motor de Coherencia
         (Claude analiza ítems vs. siniestro)
                   │
                   ▼
         Orquestador (Claude)
         → Dictamen final razonado
                   │
                   ▼
          SQLite (historial)
                   │
          ┌────────┴────────┐
          ▼                 ▼
     FastAPI REST      Streamlit Dashboard
```

---

## Requisitos

- Python 3.11+
- API Key de Anthropic (`claude-sonnet-4-20250514`)

---

## Instalación

```bash
# 1. Clonar / abrir el proyecto en VS Code

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Edita .env y agrega: ANTHROPIC_API_KEY=sk-ant-...

# 5. Inicializar la base de datos con datos de demo
python -m scripts.seed_database
```

---

## Uso

### Dashboard web (recomendado para demo)

```bash
streamlit run dashboard/streamlit_app.py
```

Abre `http://localhost:8501` en tu navegador.

**Flujo de demo (3 escenarios):**

| Factura   | Siniestro      | Resultado esperado |
|-----------|----------------|--------------------|
| DEMO-001  | SIN-2025-001   | ✅ APROBADA         |
| DEMO-002  | SIN-2025-002   | ⚠️ OBSERVADA        |
| DEMO-003  | SIN-2025-003   | ❌ RECHAZADA         |

### API REST

```bash
uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

**Auditar con factura JSON (modo demo):**
```bash
curl -X POST http://localhost:8000/auditar \
  -F "siniestro_id=SIN-2025-001" \
  -F 'factura_json={"numero_factura":"FAC-001","fecha":"2025-04-18","taller":"Taller X","items":[...],"total_factura":1000}'
```

**Auditar con PDF real:**
```bash
curl -X POST http://localhost:8000/auditar \
  -F "siniestro_id=SIN-2025-001" \
  -F "factura_pdf=@factura.pdf"
```

---

## Estructura del proyecto

```
.
├── app/
│   ├── config.py          # Variables de entorno y constantes
│   ├── database.py        # SQLite — conexiones y queries
│   ├── models.py          # Schemas Pydantic
│   ├── extractor.py       # Claude Vision — OCR de facturas
│   ├── verificadores.py   # 3 motores de verificación
│   ├── orquestador.py     # Pipeline principal + dictamen Claude
│   └── main.py            # FastAPI
├── dashboard/
│   └── streamlit_app.py   # Dashboard web
├── data/
│   └── demo_data.py       # Tarifario + siniestros + facturas demo
├── scripts/
│   └── seed_database.py   # Inicializa la BD
├── requirements.txt
├── .env.example
└── PLAN.md
```

---

## Schema del dictamen

```json
{
  "factura_id": "FAC-2025-00341",
  "siniestro_id": "SIN-2025-001",
  "resultado": "OBSERVADA",
  "confianza": 0.87,
  "items_aprobados": 14,
  "items_observados": 2,
  "monto_total_factura": 20710.00,
  "monto_discrepancias": 710.00,
  "discrepancias": [
    {
      "tipo": "precio_excedido",
      "item": "Parabrisas delantero OEM",
      "cobrado": 3800.00,
      "tarifario_max": 3200.00,
      "diferencia": 600.00
    }
  ],
  "requiere_revision_humana": true,
  "razonamiento": "Se detectó 1 ítem con precio fuera del tarifario...",
  "recomendacion": "Solicitar al taller factura rectificativa...",
  "timestamp": "2025-05-15T10:30:00Z"
}
```

---

## Umbral de revisión humana

El sistema escala automáticamente a revisión humana cuando:
- Confianza del agente < 75%
- Monto total de discrepancias > $500 MXN
- Resultado = `RECHAZADA`

Configurable en `app/config.py`.
