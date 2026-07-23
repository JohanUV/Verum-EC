"""Utilidades transversales: validacion de cedula, formato de resultados,
score de riesgo y folio consecutivo de informes."""
import json
import os
import threading
from datetime import datetime

from .config import DATA_DIR

# --- Folio consecutivo de informes -----------------------------------------
FOLIO_FILE = os.path.join(DATA_DIR, "folio.json")
_FOLIO_LOCK = threading.Lock()


def siguiente_folio():
    """Genera un folio consecutivo unico por informe (VRM-AAAA-NNNNNN)."""
    with _FOLIO_LOCK:
        try:
            with open(FOLIO_FILE, "r", encoding="utf-8") as f:
                n = json.load(f).get("n", 0)
        except (OSError, ValueError):
            n = 0
        n += 1
        try:
            with open(FOLIO_FILE, "w", encoding="utf-8") as f:
                json.dump({"n": n}, f)
        except OSError:
            pass
        return f"VRM-{datetime.now().year}-{n:06d}"


def cedula_valida(cedula):
    """Valida una cedula ecuatoriana de 10 digitos (algoritmo modulo 10)."""
    if not cedula or len(cedula) != 10 or not cedula.isdigit():
        return False
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        return False
    coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for i in range(9):
        val = int(cedula[i]) * coef[i]
        if val >= 10:
            val -= 9
        total += val
    digito = (10 - (total % 10)) % 10
    return digito == int(cedula[9])


def resultado(fuente, icono, estado, resumen, datos=None, nivel="limpio",
              enlace=None, tipo="real", clave=None):
    """Estructura normalizada que devuelve cada modulo de fuente."""
    return {
        "fuente": fuente,
        "icono": icono,
        "estado": estado,          # ok | sin_resultados | no_disponible | error
        "resumen": resumen,
        "datos": datos or [],
        "nivel": nivel,            # limpio | atencion | alerta
        "enlace": enlace,
        "tipo": tipo,              # real | informativo | captcha
        "clave": clave,            # id de fuente con relay de captcha (bachiller/senescyt)
    }


def calcular_riesgo(resultados):
    """Calcula un score de riesgo 0-100 a partir de los niveles de cada fuente.

    0 = limpio total; 100 = riesgo maximo. Cada alerta suma fuerte, cada
    atencion suma moderado. Devuelve (score, etiqueta).
    """
    score = 0
    for r in resultados:
        if r.get("nivel") == "alerta":
            score += 35
        elif r.get("nivel") == "atencion":
            score += 15
    score = min(score, 100)
    if score >= 60:
        etiqueta = "Riesgo alto"
    elif score >= 25:
        etiqueta = "Riesgo medio"
    elif score > 0:
        etiqueta = "Riesgo bajo"
    else:
        etiqueta = "Sin riesgo detectado"
    return score, etiqueta
