"""Listas de sanciones internacionales (OFAC / ONU). Cotejo por NOMBRE."""
import csv
import io
import re
import threading
import time
import unicodedata

import requests

from ..config import USER_AGENT
from ..utils import resultado

OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
OFAC_CONS_URL = "https://www.treasury.gov/ofac/downloads/consolidated/cons_prim.csv"
ONU_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
SANCIONES_TTL = 24 * 3600          # refresca las listas cada 24 h
_SANCIONES = {"entradas": None, "ts": 0}
_SANCIONES_LOCK = threading.Lock()
_PALABRAS_VACIAS = {"DE", "DEL", "LA", "LAS", "LOS", "EL", "Y", "DA", "DOS"}


def _normalizar_nombre(texto):
    """Mayusculas sin tildes ni signos, para cotejo robusto."""
    t = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z ]", " ", t).upper()
    return re.sub(r"\s+", " ", t).strip()


def _tokens_nombre(texto):
    return {p for p in _normalizar_nombre(texto).split() if len(p) >= 3 and p not in _PALABRAS_VACIAS}


def cargar_listas_sancion():
    """Descarga y cachea las listas OFAC (SDN) y ONU. Devuelve lista de
    (set_tokens, nombre_original, programa/fuente). Cache de 24 h."""
    with _SANCIONES_LOCK:
        if _SANCIONES["entradas"] is not None and (time.time() - _SANCIONES["ts"]) < SANCIONES_TTL:
            return _SANCIONES["entradas"]
        entradas = []
        headers = {"User-Agent": USER_AGENT}
        # OFAC SDN + consolidada (CSV: ent_num, nombre, tipo, programa, ...)
        for url in (OFAC_SDN_URL, OFAC_CONS_URL):
            try:
                r = requests.get(url, headers=headers, timeout=40)
                r.raise_for_status()
                for fila in csv.reader(io.StringIO(r.text)):
                    if len(fila) >= 2 and fila[1] and fila[1] != "-0-":
                        toks = _tokens_nombre(fila[1])
                        if toks:
                            prog = fila[3] if len(fila) > 3 and fila[3] != "-0-" else "OFAC"
                            entradas.append((toks, fila[1].strip(), f"OFAC ({prog})"))
            except (requests.RequestException, ValueError):
                pass
        # ONU lista consolidada (XML: nombres en etiquetas FIRST_NAME/SECOND_NAME...)
        try:
            r = requests.get(ONU_URL, headers=headers, timeout=40)
            r.raise_for_status()
            for bloque in re.findall(r"<INDIVIDUAL>(.*?)</INDIVIDUAL>", r.text, re.S):
                partes = re.findall(r"<(?:FIRST_NAME|SECOND_NAME|THIRD_NAME|FOURTH_NAME)>([^<]+)</", bloque)
                nombre = " ".join(p.strip() for p in partes if p.strip())
                toks = _tokens_nombre(nombre)
                if toks:
                    entradas.append((toks, nombre, "ONU"))
        except (requests.RequestException, ValueError):
            pass
        _SANCIONES["entradas"] = entradas
        _SANCIONES["ts"] = time.time()
        return entradas


def consultar_sanciones(nombre):
    """Coteja un nombre contra las listas de sanciones OFAC y ONU.

    Es una verificacion por NOMBRE (no por cedula), por lo que requiere que el
    titular ya este identificado.
    """
    fuente, icono = "Listas de Sancion (OFAC / ONU)", "fa-ban"
    enlace = "https://sanctionssearch.ofac.treas.gov/"
    consulta = _tokens_nombre(nombre)
    if len(consulta) < 2:
        return resultado(fuente, icono, "no_disponible",
                         "No se pudo cotejar: falta identificar el nombre del titular.",
                         nivel="limpio", enlace=enlace, tipo="real")
    try:
        listas = cargar_listas_sancion()
        if not listas:
            return resultado(fuente, icono, "no_disponible",
                             "No se pudieron descargar las listas de sancion en este momento.",
                             nivel="limpio", enlace=enlace, tipo="real")
        coincidencias = []
        for toks, original, origen in listas:
            # Coincide si todos los tokens del nombre consultado estan en la entrada
            if consulta.issubset(toks):
                coincidencias.append({"campo": origen, "valor": original})
                if len(coincidencias) >= 8:
                    break
        if coincidencias:
            return resultado(fuente, icono, "ok",
                             f"POSIBLE coincidencia en {len(coincidencias)} registro(s) de listas de sancion. "
                             f"Verificar identidad (homonimia).",
                             datos=coincidencias, nivel="alerta", enlace=enlace, tipo="real")
        return resultado(fuente, icono, "sin_resultados",
                         "No figura en las listas de sancion OFAC ni ONU.",
                         nivel="limpio", enlace=enlace, tipo="real")
    except Exception:
        return resultado(fuente, icono, "no_disponible",
                         "No se pudo completar el cotejo de sanciones.",
                         nivel="limpio", enlace=enlace, tipo="real")
