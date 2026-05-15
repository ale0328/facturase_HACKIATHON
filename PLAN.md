## Agente de Auditoría de Facturas para Aseguradoras

### ¿Qué construirás?

Un pipeline automatizado donde Claude actúa como **orquestador inteligente**: recibe documentos del taller, los compara contra el tarifario y el siniestro, y produce un dictamen estructurado antes de que el humano vea un solo papel.

---

## Fase 1 — Fundamentos y diseño (Semana 1)

**1.1 Define las fuentes de datos**

Tienes tres entradas:
- **Factura del taller**: puede llegar como PDF, imagen escaneada, Excel o XML.
- **Tarifario acordado**: documento contractual entre aseguradora y red de talleres. Conviértelo en una base de datos estructurada (PostgreSQL o incluso un JSON/CSV versionado en S3).
- **Expediente del siniestro**: los datos del accidente (piezas afectadas, mano de obra estimada, fotos del perito).

**1.2 Define el schema de salida**

Antes de escribir código, decide qué produce el agente. Un ejemplo:

```json
{
  "factura_id": "FAC-2025-00341",
  "resultado": "OBSERVADA",
  "confianza": 0.87,
  "discrepancias": [
    {
      "tipo": "precio_excedido",
      "item": "Parabrisas delantero OEM",
      "cobrado": 420.00,
      "tarifario": 310.00,
      "diferencia": 110.00
    },
    {
      "tipo": "duplicado",
      "item": "Mano de obra pintura capó",
      "ocurrencias": 2
    }
  ],
  "items_aprobados": 14,
  "items_observados": 2,
  "requiere_revision_humana": true,
  "razonamiento": "Se detectaron 2 ítems fuera del tarifario..."
}
```

---

## Fase 2 — Extracción de datos (Semana 1–2)

**2.1 OCR y parsing de facturas**

Usa la API de Claude con visión para extraer datos de PDFs o imágenes:

```python
import anthropic, base64

client = anthropic.Anthropic()

def extraer_items_factura(pdf_bytes: bytes) -> dict:
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode()
    
    respuesta = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64
                    }
                },
                {
                    "type": "text",
                    "text": """Extrae todos los ítems de esta factura de taller automotriz.
                    Devuelve SOLO un JSON con la siguiente estructura:
                    {
                      "numero_factura": "...",
                      "fecha": "YYYY-MM-DD",
                      "taller": "...",
                      "items": [
                        {
                          "codigo": "...",
                          "descripcion": "...",
                          "cantidad": 1,
                          "precio_unitario": 0.00,
                          "total": 0.00,
                          "tipo": "insumo|mano_obra|servicio"
                        }
                      ],
                      "total_factura": 0.00
                    }"""
                }
            ]
        }]
    )
    
    import json
    texto = respuesta.content[0].text
    return json.loads(texto)
```

**2.2 Carga del tarifario en base de datos**

```sql
CREATE TABLE tarifario (
    codigo          VARCHAR(50) PRIMARY KEY,
    descripcion     TEXT,
    precio_min      DECIMAL(10,2),
    precio_max      DECIMAL(10,2),
    unidad          VARCHAR(20),
    categoria       VARCHAR(50),
    vigente_desde   DATE,
    vigente_hasta   DATE
);
```

---

## Fase 3 — Los motores de verificación (Semana 2–3)

**3.1 Motor de precios** — compara cada ítem contra el tarifario:

```python
def verificar_precios(items_factura: list, cursor_db) -> list:
    discrepancias = []
    for item in items_factura:
        cursor_db.execute("""
            SELECT precio_min, precio_max 
            FROM tarifario 
            WHERE codigo = %s AND NOW() BETWEEN vigente_desde AND vigente_hasta
        """, (item['codigo'],))
        
        row = cursor_db.fetchone()
        if not row:
            discrepancias.append({
                "tipo": "codigo_no_encontrado",
                "item": item['descripcion'],
                "codigo": item['codigo']
            })
        elif item['precio_unitario'] > row['precio_max']:
            discrepancias.append({
                "tipo": "precio_excedido",
                "item": item['descripcion'],
                "cobrado": item['precio_unitario'],
                "tarifario_max": row['precio_max'],
                "diferencia": item['precio_unitario'] - row['precio_max']
            })
    return discrepancias
```

**3.2 Motor de duplicados** — detecta ítems repetidos:

```python
from collections import Counter

def detectar_duplicados(items: list) -> list:
    conteo = Counter(item['codigo'] for item in items)
    return [
        {"tipo": "duplicado", "codigo": cod, "ocurrencias": n}
        for cod, n in conteo.items() if n > 1
    ]
```

**3.3 Motor de coherencia** — valida que los insumos correspondan al siniestro:

```python
def verificar_coherencia_siniestro(items_factura: list, datos_siniestro: dict, client) -> dict:
    prompt = f"""
    Siniestro reportado:
    - Tipo de accidente: {datos_siniestro['tipo']}
    - Partes afectadas según perito: {datos_siniestro['partes_afectadas']}
    - Vehículo: {datos_siniestro['vehiculo']}

    Ítems cobrados por el taller:
    {json.dumps(items_factura, ensure_ascii=False, indent=2)}

    Analiza si los ítems cobrados son coherentes con el siniestro reportado.
    Identifica cualquier ítem que NO corresponda a las partes afectadas.
    Responde SOLO en JSON:
    {{
      "coherente": true/false,
      "items_inconsistentes": [...],
      "razonamiento": "..."
    }}
    """
    
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(resp.content[0].text)
```

---

## Fase 4 — El orquestador Claude (Semana 3)

Este es el corazón del agente. Claude recibe todos los hallazgos y emite un **dictamen razonado**:

```python
def orquestar_auditoria(factura_raw: bytes, siniestro: dict, db_cursor) -> dict:
    # Paso 1: Extraer
    factura = extraer_items_factura(factura_raw)
    
    # Paso 2: Verificar
    disc_precios = verificar_precios(factura['items'], db_cursor)
    disc_duplicados = detectar_duplicados(factura['items'])
    disc_coherencia = verificar_coherencia_siniestro(
        factura['items'], siniestro, client
    )
    
    # Paso 3: Dictamen final con Claude
    todas_discrepancias = disc_precios + disc_duplicados + disc_coherencia.get('items_inconsistentes', [])
    
    prompt_dictamen = f"""
    Eres un auditor experto de seguros automotrices.
    
    FACTURA: {json.dumps(factura, ensure_ascii=False)}
    SINIESTRO: {json.dumps(siniestro, ensure_ascii=False)}
    DISCREPANCIAS DETECTADAS: {json.dumps(todas_discrepancias, ensure_ascii=False)}
    
    Emite un dictamen de auditoría en JSON con:
    - resultado: "APROBADA" | "OBSERVADA" | "RECHAZADA"
    - confianza: 0.0 a 1.0
    - requiere_revision_humana: true si hay casos ambiguos o monto > $500
    - razonamiento: explicación concisa del dictamen
    - recomendacion: acción sugerida al ajustador
    """
    
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt_dictamen}]
    )
    
    dictamen = json.loads(resp.content[0].text)
    dictamen['discrepancias'] = todas_discrepancias
    dictamen['factura_id'] = factura['numero_factura']
    
    return dictamen
```

---

## Fase 5 — Infraestructura y despliegue (Semana 4)

**Stack recomendado:**

| Capa | Tecnología | Por qué |
|---|---|---|
| Backend | FastAPI (Python) | Async, fácil de escalar |
| Base de datos | PostgreSQL | Tarifario + historial de auditorías |
| Almacenamiento | AWS S3 / MinIO | Facturas originales |
| Cola de trabajo | Redis + Celery | Procesamiento asíncrono |
| LLM | Claude API (Anthropic) | Extracción + dictamen |
| Notificaciones | SendGrid / webhook | Alertas a ajustadores |
| Dashboard | Streamlit o React | Vista de resultados |

**Endpoint principal:**

```python
from fastapi import FastAPI, UploadFile
app = FastAPI()

@app.post("/auditar")
async def auditar_factura(
    factura: UploadFile,
    siniestro_id: str
):
    factura_bytes = await factura.read()
    siniestro = obtener_siniestro(siniestro_id)  # desde tu sistema
    
    resultado = orquestar_auditoria(factura_bytes, siniestro, db_cursor)
    
    guardar_resultado(resultado)
    
    if resultado['requiere_revision_humana']:
        notificar_ajustador(resultado)
    
    return resultado
```

---

## Fase 6 — Evaluación y mejora continua

Para que el sistema mejore con el tiempo:

1. **Feedback loop**: el ajustador humano marca si el dictamen fue correcto → entrena ejemplos.
2. **Métricas clave a medir**: tasa de falsos positivos, tasa de falsos negativos, ahorro monetario detectado, tiempo promedio de auditoría.
3. **Versionado del tarifario**: guarda historial para que facturas antiguas se validen contra el tarifario vigente en esa fecha.
4. **Umbral de confianza configurable**: si `confianza < 0.75`, siempre va a revisión humana.

---

## Orden de ejecución sugerido

1. **Semana 1**: Estructura el tarifario en BD + prueba extracción con Claude en 10 facturas reales.
2. **Semana 2**: Implementa los 3 motores de verificación + tests unitarios.
3. **Semana 3**: Integra el orquestador y valida el dictamen contra casos conocidos.
4. **Semana 4**: Despliega el API, conecta notificaciones, construye el dashboard mínimo.
5. **Semana 5+**: Iteración basada en feedback del equipo de ajustadores.

¿Quieres que profundice en alguna de estas fases? Por ejemplo, puedo generarte el código completo del orquestador, el schema de base de datos detallado, o la lógica de puntuación de riesgo.