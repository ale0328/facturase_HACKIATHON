import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-2.5-flash"
DB_PATH: str = "auditoria.db"

# Umbral de confianza por debajo del cual siempre se manda a revisión humana
CONFIANZA_REVISION_HUMANA: float = 0.75

# Monto de discrepancia acumulada que dispara revisión humana
MONTO_REVISION_HUMANA: float = 500.0
