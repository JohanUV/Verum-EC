"""Funcion Judicial: procesos judiciales por cedula o nombre, y detalle de
litigantes de cada proceso (servicio CLEX). API REAL."""
import re
import unicodedata

import requests
from datetime import datetime

from ..config import PROVINCIAS, USER_AGENT
from ..utils import resultado

JUDICIAL_BASE = "https://api.funcionjudicial.gob.ec/EXPEL-CONSULTA-CAUSAS-SERVICE/api/consulta-causas/informacion"
# Servicio CLEX: expone los litigantes (actores/demandados) y la judicatura de cada proceso
CLEX_BASE = "https://api.funcionjudicial.gob.ec/EXPEL-CONSULTA-CAUSAS-CLEX-SERVICE/api/consulta-causas-clex/informacion"
JUDICIAL_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://procesosjudiciales.funcionjudicial.gob.ec",
    "Referer": "https://procesosjudiciales.funcionjudicial.gob.ec/causas",
    "User-Agent": USER_AGENT,
}


def _buscar_causas(cedula="", nombre="", rol="actor", timeout=15):
    """POST a buscarCausas para un rol (actor/demandado) por cedula o nombre."""
    if rol == "actor":
        payload = {"actor": {"cedulaActor": cedula, "nombreActor": nombre},
                   "demandado": {"cedulaDemandado": "", "nombreDemandado": ""}}
    else:
        payload = {"actor": {"cedulaActor": "", "nombreActor": ""},
                   "demandado": {"cedulaDemandado": cedula, "nombreDemandado": nombre}}
    payload.update({
        "numeroCausa": "", "provincia": "", "numeroFiscalia": "",
        "recaptcha": "verdad", "first": 1, "pageSize": 50
    })
    r = requests.post(f"{JUDICIAL_BASE}/buscarCausas", json=payload,
                      headers=JUDICIAL_HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _anio_ingreso(fecha):
    if not fecha:
        return ""
    try:
        return datetime.fromisoformat(fecha.replace("+00:00", "")).year
    except (ValueError, TypeError):
        return ""


def consultar_judicial(cedula):
    """Procesos judiciales donde la persona es actor o demandado. API REAL."""
    try:
        causas = []
        vistos = set()
        for rol in ("actor", "demandado"):
            for c in _buscar_causas(cedula=cedula, rol=rol):
                jid = c.get("idJuicio", "")
                if jid in vistos:
                    continue
                vistos.add(jid)
                anio = _anio_ingreso(c.get("fechaIngreso", ""))
                num = c.get("idJuicio", "") or ""
                prov = PROVINCIAS.get(num[:2], "") if len(num) >= 2 else ""
                causas.append({
                    "numero": num or "N/A",
                    "tipo": c.get("nombreDelito") or c.get("nombreMateria") or "N/A",
                    "fecha": str(anio) if anio else "N/A",
                    "rol": rol.capitalize(),
                    "provincia": prov,
                    "estado": "Activo" if c.get("estadoActual") == "A" else (c.get("nombreEstadoJuicio") or ""),
                })
        total = len(causas)
        if total == 0:
            return resultado("Procesos Judiciales", "fa-scale-balanced", "sin_resultados",
                             "Sin procesos judiciales registrados.", nivel="limpio")
        nivel = "alerta" if total >= 5 else "atencion"
        return resultado("Procesos Judiciales", "fa-scale-balanced", "ok",
                         f"{total} proceso(s) judicial(es) encontrado(s).",
                         datos=causas, nivel=nivel,
                         enlace="https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")
    except requests.RequestException as e:
        return resultado("Procesos Judiciales", "fa-scale-balanced", "error",
                         f"No se pudo consultar la Funcion Judicial: {e}", nivel="atencion")


def buscar_procesos_por_nombre(nombre):
    """Procesos judiciales por nombre (actor y/o demandado), ordenados por anio.

    Limitacion conocida: la API de la Funcion Judicial NO expone la cedula ni el
    nombre completo de las partes en el listado, por lo que no es posible separar
    a distintas personas que compartan el mismo nombre.
    Lanza requests.RequestException si el servicio no responde.
    """
    procesos, vistos = [], set()
    for rol in ("actor", "demandado"):
        for c in _buscar_causas(nombre=nombre, rol=rol, timeout=20):
            jid = c.get("idJuicio", "")
            if not jid or jid in vistos:
                continue
            vistos.add(jid)
            anio = _anio_ingreso(c.get("fechaIngreso"))
            procesos.append({
                "numero": jid,
                "tipo": c.get("nombreDelito") or c.get("nombreMateria") or "N/A",
                "anio": str(anio) if anio else "N/A",
                "provincia": PROVINCIAS.get(jid[:2], "") if len(jid) >= 2 else "",
                "rol": rol.capitalize(),
                "estado": "Activo" if c.get("estadoActual") == "A" else "Inactivo",
            })
    procesos.sort(key=lambda p: p["anio"], reverse=True)
    return procesos


def obtener_litigantes(id_juicio):
    """Devuelve actores, demandados, judicatura y ciudad de un proceso (servicio CLEX).

    Retorna None si el proceso es reservado o el servicio no responde.
    """
    try:
        r = requests.get(f"{CLEX_BASE}/getIncidenteJudicatura/{id_juicio}",
                         headers=JUDICIAL_HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        # La respuesta puede ser un dict (una judicatura) o una lista (varias)
        bloques = data if isinstance(data, list) else [data]
        actores, demandados = [], []
        judicatura, ciudad = "", ""
        for bloque in bloques:
            if not isinstance(bloque, dict):
                continue
            if not judicatura:
                judicatura = bloque.get("nombreJudicatura", "") or ""
                ciudad = bloque.get("ciudad", "") or ""
            for inc in bloque.get("lstIncidenteJudicatura", []) or []:
                for a in (inc.get("lstLitiganteActor") or []):
                    n = (a.get("nombresLitigante") or "").strip()
                    if n and n not in actores:
                        actores.append(n)
                for dm in (inc.get("lstLitiganteDemandado") or []):
                    n = (dm.get("nombresLitigante") or "").strip()
                    if n and n not in demandados:
                        demandados.append(n)
        return {
            "judicatura": judicatura,
            "ciudad": ciudad,
            "actores": actores,
            "demandados": demandados,
        }
    except (requests.RequestException, ValueError):
        return None


def _clave_nombre(nombre):
    """Clave canonica de un nombre para agrupar variantes.

    Los portales devuelven la misma persona con distinto orden de palabras
    ("UNTUNA LICERO ANGEL PAUL" y "ANGEL PAUL UNTUNA LICERO"), por lo que la
    clave son sus tokens normalizados (sin tildes) y ordenados alfabeticamente.
    """
    t = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z ]", " ", t).upper()
    return " ".join(sorted(t.split()))


def nombre_titular_desde_judicial(causas):
    """Deduce el nombre de la persona a partir de sus procesos.

    Agrupa las variantes del mismo nombre (distinto orden de palabras) y cuenta
    en cuantas causas aparece cada persona dentro del rol consultado. Solo
    devuelve un nombre si gana SIN empate: ante un empate (p. ej. co-actores de
    una misma causa, como un divorcio) devuelve None, porque es mejor no
    mostrar nombre que mostrar el de un co-litigante.
    """
    from collections import Counter
    conteo = Counter()
    variantes = {}
    for causa in causas[:4]:
        det = obtener_litigantes(causa.get("numero", ""))
        if not det:
            continue
        pool = det["actores"] if causa.get("rol") == "Actor" else det["demandados"]
        for nombre in pool:
            clave = _clave_nombre(nombre)
            if not clave:
                continue
            conteo[clave] += 1
            # conserva la variante mas completa para mostrarla
            if len(nombre) > len(variantes.get(clave, "")):
                variantes[clave] = nombre.strip()
    top = conteo.most_common(2)
    if not top:
        return None
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None
    return variantes[top[0][0]]
