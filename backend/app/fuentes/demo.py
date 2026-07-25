"""Modo demostracion: informes simulados y garantizados.

Las fuentes reales son portales del Estado que a veces no responden o son
lentos; para presentaciones y pruebas (docente / usuarios de prueba) este
modulo devuelve un informe completo y consistente SIN salir a la red.

Se usa cuando el cliente envia {"demo": true} a /api/verificar. Los datos son
FICTICIOS y solo sirven para demostrar la interfaz.
"""
from datetime import datetime

from ..historial import registrar_historial
from ..utils import calcular_riesgo, resultado, siguiente_folio


def _sri_contribuyente(razon, nivel="limpio", resumen="Contribuyente activo con RUC."):
    return resultado(
        "SRI - Contribuyente", "fa-file-invoice-dollar", "ok", resumen,
        datos=[
            {"campo": "Razon Social", "valor": razon},
            {"campo": "RUC", "valor": "0102030405001"},
            {"campo": "Estado", "valor": "ACTIVO"},
            {"campo": "Actividad", "valor": "Servicios de consultoria"},
        ], nivel=nivel, tipo="real")


# --- Perfiles fijos para las cedulas de ejemplo -----------------------------
def _perfil_atencion(titular):
    return titular, [
        resultado("Procesos Judiciales", "fa-scale-balanced", "ok",
                  "1 causa civil como demandado (en tramite).",
                  datos=[{"tipo": "Ejecutivo (cobro)", "fecha": "2023-05-14",
                          "rol": "Demandado", "provincia": "Pichincha", "estado": "En tramite"}],
                  nivel="atencion", tipo="real"),
        _sri_contribuyente(titular),
        resultado("SRI - Establecimientos", "fa-location-dot", "ok",
                  "1 establecimiento registrado.",
                  datos=[{"campo": "Matriz", "valor": "Quito - La Carolina"}], tipo="real"),
        resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "sin_resultados",
                  "Sin deudas firmes registradas.", tipo="real"),
        resultado("Pensiones Alimenticias (SUPA)", "fa-hand-holding-heart", "sin_resultados",
                  "Sin obligaciones de pension en mora.", tipo="real"),
        resultado("Multas de Transito (ANT)", "fa-car-burst", "ok",
                  "1 multa de transito pendiente de pago.",
                  datos=[{"campo": "Citacion", "valor": "PIC-2024-01822"},
                         {"campo": "Valor", "valor": "$ 46.00"},
                         {"campo": "Estado", "valor": "Pendiente"}],
                  nivel="atencion", tipo="real"),
        resultado("Listas de Sancion (OFAC / ONU)", "fa-ban", "sin_resultados",
                  "Sin coincidencias en listas de sancion.", tipo="real"),
    ]


def _perfil_alerta(titular):
    return titular, [
        resultado("Procesos Judiciales", "fa-scale-balanced", "ok",
                  "Causa penal como procesado (relevante).",
                  datos=[{"tipo": "Penal - Estafa", "fecha": "2022-09-02",
                          "rol": "Procesado", "provincia": "Guayas", "estado": "En tramite"},
                         {"tipo": "Transito", "fecha": "2021-03-18",
                          "rol": "Demandado", "provincia": "Guayas", "estado": "Archivado"}],
                  nivel="alerta", tipo="real"),
        _sri_contribuyente(titular, resumen="Contribuyente con obligaciones pendientes."),
        resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "ok",
                  "Deuda tributaria firme registrada.",
                  datos=[{"campo": "Deuda total", "valor": "$ 1.284,50"},
                         {"campo": "Estado", "valor": "Firme"}],
                  nivel="atencion", tipo="real"),
        resultado("SRI - Establecimientos", "fa-location-dot", "ok",
                  "2 establecimientos registrados.",
                  datos=[{"campo": "Matriz", "valor": "Guayaquil - Centro"},
                         {"campo": "Sucursal", "valor": "Duran"}], tipo="real"),
        resultado("Pensiones Alimenticias (SUPA)", "fa-hand-holding-heart", "ok",
                  "Registro de pension alimenticia en mora.",
                  datos=[{"campo": "Estado", "valor": "En mora"},
                         {"campo": "Cuotas", "valor": "3 pendientes"}],
                  nivel="alerta", tipo="real"),
        resultado("Multas de Transito (ANT)", "fa-car-burst", "ok",
                  "2 multas de transito pendientes.",
                  datos=[{"campo": "Total pendiente", "valor": "$ 92.00"}],
                  nivel="atencion", tipo="real"),
        resultado("Listas de Sancion (OFAC / ONU)", "fa-ban", "ok",
                  "Coincidencia parcial por nombre (requiere verificacion manual).",
                  datos=[{"campo": "Lista", "valor": "OFAC - SDN (coincidencia parcial)"}],
                  nivel="atencion", tipo="real"),
    ]


def _perfil_limpio(titular):
    return titular, [
        resultado("Procesos Judiciales", "fa-scale-balanced", "sin_resultados",
                  "Sin procesos judiciales registrados.", tipo="real"),
        resultado("SRI - Contribuyente", "fa-file-invoice-dollar", "sin_resultados",
                  "Sin RUC registrado (persona natural sin actividad economica).", tipo="real"),
        resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "sin_resultados",
                  "Sin deudas tributarias.", tipo="real"),
        resultado("SRI - Establecimientos", "fa-location-dot", "sin_resultados",
                  "Sin establecimientos registrados.", tipo="real"),
        resultado("Pensiones Alimenticias (SUPA)", "fa-hand-holding-heart", "sin_resultados",
                  "Sin obligaciones de pension en mora.", tipo="real"),
        resultado("Multas de Transito (ANT)", "fa-car-burst", "sin_resultados",
                  "Sin multas de transito pendientes.", tipo="real"),
        resultado("Listas de Sancion (OFAC / ONU)", "fa-ban", "sin_resultados",
                  "Sin coincidencias en listas de sancion.", tipo="real"),
    ]


# Cedulas de ejemplo de la interfaz -> perfil (para que cada chip muestre algo distinto).
_PERFILES = {
    "0102030405": lambda: _perfil_atencion("PEREZ GARCIA JUAN CARLOS"),
    "0959083015": lambda: _perfil_alerta("MENDOZA LOOR ANGEL DAVID"),
    "1809139098": lambda: _perfil_limpio("SANCHEZ ROBALINO MARIA JOSE"),
}


def informe_demo(cedula, proposito, usuario):
    """Construye un informe simulado completo (misma forma que la verificacion real)."""
    titular, resultados = _PERFILES.get(cedula, lambda: _perfil_atencion("TITULAR DE DEMOSTRACION"))()

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

    registrar_historial({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folio": folio, "usuario": usuario, "cedula": cedula,
        "titular": titular, "proposito": proposito,
        "semaforo": semaforo, "score": score, "alertas": alertas,
        "demo": True,
    })

    return {
        "cedula": cedula, "titular": titular, "semaforo": semaforo, "mensaje": mensaje,
        "score": score, "etiqueta_riesgo": etiqueta_riesgo, "folio": folio,
        "proposito": proposito, "usuario": usuario, "demo": True,
        "resumen": {
            "fuentes_consultadas": len(resultados), "fuentes_con_api": fuentes_reales,
            "con_hallazgos": hallazgos, "alertas": alertas,
        },
        "resultados": resultados,
    }
