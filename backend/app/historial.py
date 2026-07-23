"""Historial de consultas (auditoria LOPDP), persistido en data/historial.json."""
import json
import os
import threading

from .config import DATA_DIR

HISTORIAL_FILE = os.path.join(DATA_DIR, "historial.json")
HISTORIAL_LOCK = threading.Lock()
HISTORIAL_MAX = 200


def registrar_historial(entrada):
    """Agrega una consulta al historial (persistido en JSON, ultimas 200)."""
    with HISTORIAL_LOCK:
        historial = leer_historial()
        historial.insert(0, entrada)
        historial = historial[:HISTORIAL_MAX]
        try:
            with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
                json.dump(historial, f, ensure_ascii=False)
        except OSError:
            pass


def leer_historial():
    """Lee el historial de consultas desde disco (lista, mas reciente primero)."""
    try:
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []
