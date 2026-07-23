"""ANT: multas y citaciones de transito pendientes. API REAL (jqGrid JSON)."""
import requests

from ..config import ENLACES_OFICIALES, USER_AGENT
from ..utils import resultado

# Endpoint JSON del portal de consulta ciudadana
ANT_CITACIONES_URL = "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_json_citaciones.jsp"


def consultar_ant(cedula):
    """Multas de transito (ANT) - API REAL.

    El portal de consulta ciudadana de la ANT expone un endpoint JSON (jqGrid)
    que lista las citaciones PENDIENTES por cedula. ps_opcion=P = pendientes.
    """
    fuente, icono = "Multas de Transito (ANT)", "fa-car-burst"
    try:
        params = {
            "ps_opcion": "P",
            "ps_id_contrato": "",
            "ps_id_persona": "",
            "ps_placa": "",
            "ps_identificacion": cedula,
            "ps_tipo_identificacion": "CED",
            "_search": "false",
            "rows": "100",
            "page": "1",
            "sidx": "fecha_emision",
            "sord": "desc",
        }
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_grid_citaciones.jsp",
            "X-Requested-With": "XMLHttpRequest",
        }
        r = requests.get(ANT_CITACIONES_URL, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        registros = int(data.get("records", 0) or 0)
        filas = data.get("rows", []) or []

        if registros == 0:
            return resultado(fuente, icono, "sin_resultados",
                             "Sin citaciones de transito pendientes.",
                             nivel="limpio", enlace=ENLACES_OFICIALES["ant"])

        datos, total_multa = [], 0.0
        for fila in filas[:15]:
            celda = fila.get("cell", fila) if isinstance(fila, dict) else fila
            if isinstance(celda, list):
                # Columnas: infraccion, entidad, citacion, placa, f.emision,
                # f.notificacion, puntos, sancion, multa, ...
                citacion = celda[2] if len(celda) > 2 else ""
                placa = celda[3] if len(celda) > 3 else ""
                emision = celda[4] if len(celda) > 4 else ""
                multa = celda[8] if len(celda) > 8 else ""
                try:
                    total_multa += float(str(multa).replace("$", "").replace(",", "").strip() or 0)
                except ValueError:
                    pass
                datos.append({
                    "campo": f"Citacion {citacion} ({placa})",
                    "valor": f"Emitida {emision} - Multa {multa}",
                })
            else:
                datos.append({"campo": "Citacion", "valor": str(celda)})

        extra = f" Total aproximado: ${total_multa:,.2f}." if total_multa else ""
        resumen = f"Registra {registros} citacion(es) de transito PENDIENTE(S).{extra}"
        return resultado(fuente, icono, "ok", resumen, datos=datos,
                         nivel="alerta", enlace=ENLACES_OFICIALES["ant"])
    except (requests.RequestException, ValueError):
        return resultado(
            fuente, icono, "no_disponible",
            "No se pudo consultar la ANT en este momento. Verifique en el portal oficial.",
            nivel="limpio", enlace=ENLACES_OFICIALES["ant"], tipo="informativo")
