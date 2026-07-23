"""Orquestacion de la verificacion: ejecuta las fuentes en paralelo, identifica
al titular, coteja sanciones y consolida semaforo, score, folio e historial."""
import concurrent.futures
from datetime import datetime

from .fuentes import MODULOS
from .fuentes.judicial import nombre_titular_desde_judicial
from .fuentes.sanciones import consultar_sanciones
from .historial import registrar_historial
from .utils import calcular_riesgo, siguiente_folio


def verificacion_completa(cedula, proposito, usuario):
    """Barrido completo de fuentes para una cedula. Devuelve el informe (dict)."""
    # Ejecuta todos los modulos en paralelo
    resultados = [None] * len(MODULOS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(MODULOS)) as ex:
        futuros = {ex.submit(m, cedula): i for i, m in enumerate(MODULOS)}
        for fut in concurrent.futures.as_completed(futuros):
            resultados[futuros[fut]] = fut.result()

    # Nombre del titular: 1) razonSocial del SRI (si tiene RUC)
    titular = None
    for r in resultados:
        if r["fuente"].startswith("SRI - Contribuyente"):
            for d in r["datos"]:
                if d.get("campo") == "Razon Social" and d.get("valor") not in (None, "", "N/A"):
                    titular = d["valor"]

    # 2) Fallback: deducirlo de los procesos judiciales (sirve para quien no tiene RUC)
    if not titular:
        jud = next((r for r in resultados
                    if r["fuente"] == "Procesos Judiciales" and r["estado"] == "ok"), None)
        if jud and jud["datos"]:
            titular = nombre_titular_desde_judicial(jud["datos"])

    # Cotejo de sanciones (por nombre del titular). Se inserta antes de
    # Record Policial para que esa fuente quede al final.
    if titular:
        sanciones = consultar_sanciones(titular)
        resultados.insert(len(resultados) - 1, sanciones)

    # Semaforo consolidado
    alertas = sum(1 for r in resultados if r["nivel"] == "alerta")
    atenciones = sum(1 for r in resultados if r["nivel"] == "atencion")
    fuentes_reales = sum(1 for r in resultados if r["tipo"] == "real")
    hallazgos = sum(1 for r in resultados if r["estado"] == "ok")

    if alertas > 0:
        semaforo, mensaje = "alerta", "Se encontraron hallazgos relevantes."
    elif atenciones > 0 or hallazgos > 0:
        semaforo, mensaje = "atencion", "Hay registros que ameritan revision."
    else:
        semaforo, mensaje = "limpio", "Sin antecedentes relevantes en las fuentes consultadas."

    score, etiqueta_riesgo = calcular_riesgo(resultados)
    folio = siguiente_folio()

    # Registro en el historial de consultas (auditoria + LOPDP)
    registrar_historial({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folio": folio,
        "usuario": usuario,
        "cedula": cedula,
        "titular": titular or "—",
        "proposito": proposito,
        "semaforo": semaforo,
        "score": score,
        "alertas": alertas,
    })

    return {
        "cedula": cedula,
        "titular": titular,
        "semaforo": semaforo,
        "mensaje": mensaje,
        "score": score,
        "etiqueta_riesgo": etiqueta_riesgo,
        "folio": folio,
        "proposito": proposito,
        "usuario": usuario,
        "resumen": {
            "fuentes_consultadas": len(resultados),
            "fuentes_con_api": fuentes_reales,
            "con_hallazgos": hallazgos,
            "alertas": alertas,
        },
        "resultados": resultados,
    }
