"""SRI: contribuyente/RUC, deudas tributarias, establecimientos y resolucion
de nombre -> cedula (registro de personas). API REAL."""
import requests
from urllib.parse import quote

from ..config import USER_AGENT
from ..utils import resultado

SRI_RUC_URL = "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc"
SRI_DEUDAS_URL = "https://srienlinea.sri.gob.ec/sri-deudas-servicio-internet/rest/Deudas/porIdentificacion"
SRI_ESTAB_URL = "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/Establecimiento/consultarPorNumeroRuc"
# Nombre -> cedula. Origen oficial: SRI (deudas por denominacion). El endpoint
# directo del SRI esta protegido por firewall F5, por lo que se usa el proxy
# publico de ecuadorlegalonline, que reenvia la consulta al SRI y devuelve JSON.
SRI_POR_NOMBRE_URL = "https://srienlinea.sri.gob.ec/movil-servicios/api/v1.0/deudas/porDenominacion"
CEDULA_POR_NOMBRE_PROXY = "https://apps.ecuadorlegalonline.com/modulo/consultar-cedulanombre.php"


def consultar_sri(cedula):
    """Estado del contribuyente / RUC en el SRI. API REAL."""
    ruc = cedula + "001"
    try:
        r = requests.get(SRI_RUC_URL, params={"ruc": ruc}, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        if r.status_code == 200 and r.text.strip() and r.text.strip() != "[]":
            data = r.json()
            if isinstance(data, list) and data:
                info = data[0]
                estado_c = (info.get("estadoContribuyenteRuc") or "").upper()
                razon = info.get("razonSocial") or "N/A"
                actividad = ""
                if info.get("informacionFechasContribuyente"):
                    actividad = info["informacionFechasContribuyente"].get("fechaInicioActividades", "")
                fantasma = (info.get("contribuyenteFantasma") or "NO").upper()
                inexistente = (info.get("transaccionesInexistente") or "NO").upper()

                datos = [
                    {"campo": "Razon Social", "valor": razon},
                    {"campo": "Estado RUC", "valor": estado_c or "N/A"},
                    {"campo": "Tipo", "valor": info.get("tipoContribuyente", "N/A")},
                    {"campo": "Actividad economica", "valor": info.get("actividadEconomicaPrincipal", "N/A")},
                    {"campo": "Regimen", "valor": info.get("regimen", "N/A")},
                    {"campo": "Categoria", "valor": info.get("categoria") or "N/A"},
                    {"campo": "Inicio actividades", "valor": (actividad or "N/A")[:10]},
                ]
                # Banderas de riesgo
                if fantasma == "SI":
                    datos.append({"campo": "⚠ Contribuyente fantasma", "valor": "SI"})
                if inexistente == "SI":
                    datos.append({"campo": "⚠ Transacciones inexistentes", "valor": "SI"})

                if fantasma == "SI" or inexistente == "SI":
                    nivel = "alerta"
                    resumen = f"{razon}. ALERTA: marcado por el SRI (fantasma/transacciones inexistentes)."
                elif estado_c == "ACTIVO":
                    nivel = "limpio"
                    resumen = f"Contribuyente activo. {info.get('actividadEconomicaPrincipal', '')}".strip()
                else:
                    nivel = "atencion"
                    resumen = f"Estado RUC: {estado_c or 'N/A'}."
                return resultado("SRI - Contribuyente", "fa-file-invoice-dollar", "ok",
                                 resumen, datos=datos, nivel=nivel)
        # Sin RUC asociado
        return resultado("SRI - Contribuyente", "fa-file-invoice-dollar", "sin_resultados",
                         "La cedula no tiene RUC activo registrado en el SRI.", nivel="limpio")
    except (requests.RequestException, ValueError) as e:
        return resultado("SRI - Contribuyente", "fa-file-invoice-dollar", "error",
                         f"No se pudo consultar el SRI: {e}", nivel="atencion")


def consultar_sri_deudas(cedula):
    """Deudas tributarias firmes/impugnadas con el SRI. API REAL (best-effort)."""
    try:
        r = requests.get(f"{SRI_DEUDAS_URL}/{cedula}", timeout=15,
                         headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        if r.status_code == 200 and r.text.strip() and r.text.strip() not in ("[]", "{}", "null"):
            data = r.json()
            # La respuesta puede traer listas de deudas firmes/impugnadas
            deudas = []
            if isinstance(data, dict):
                for clave in ("deudasFirmes", "deudasImpugnadas", "deudas"):
                    val = data.get(clave)
                    if isinstance(val, list):
                        deudas.extend(val)
                total_val = data.get("totalDeuda") or data.get("total")
            elif isinstance(data, list):
                deudas = data
                total_val = None

            if deudas:
                datos = []
                for d in deudas[:5]:
                    concepto = d.get("descripcion") or d.get("concepto") or "Obligacion"
                    valor = d.get("saldo") or d.get("valor") or d.get("totalDeuda") or ""
                    datos.append({"campo": str(concepto)[:40], "valor": f"${valor}" if valor else "Pendiente"})
                resumen = f"Registra {len(deudas)} obligacion(es) pendiente(s) con el SRI"
                if total_val:
                    resumen += f" (total ${total_val})"
                return resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "ok",
                                 resumen + ".", datos=datos, nivel="alerta")
        return resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "sin_resultados",
                         "No registra deudas tributarias firmes con el SRI.", nivel="limpio")
    except (requests.RequestException, ValueError):
        return resultado("SRI - Deudas Tributarias", "fa-money-bill-wave", "no_disponible",
                         "El servicio de deudas del SRI no respondio. Consulta en el portal del SRI.",
                         nivel="limpio", enlace="https://srienlinea.sri.gob.ec/", tipo="informativo")


def consultar_sri_establecimientos(cedula):
    """Direccion y establecimientos registrados en el SRI. API REAL."""
    ruc = cedula + "001"
    try:
        r = requests.get(SRI_ESTAB_URL, params={"numeroRuc": ruc}, timeout=15,
                         headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        if r.status_code == 200 and r.text.strip() and r.text.strip() not in ("[]", "{}", "null"):
            data = r.json()
            locales = data if isinstance(data, list) else [data]
            datos = []
            for loc in locales[:5]:
                if not isinstance(loc, dict):
                    continue
                tipo = "Matriz" if loc.get("matriz") == "SI" else "Sucursal"
                estado = loc.get("estado") or "N/A"
                datos.append({"campo": f"{tipo} ({estado})",
                              "valor": loc.get("direccionCompleta") or "N/A"})
            if datos:
                return resultado("SRI - Establecimientos", "fa-location-dot", "ok",
                                 f"{len(locales)} direccion(es) registrada(s) en el SRI.",
                                 datos=datos, nivel="limpio")
        return resultado("SRI - Establecimientos", "fa-location-dot", "sin_resultados",
                         "Sin establecimientos registrados (la cedula no tiene RUC).", nivel="limpio")
    except (requests.RequestException, ValueError):
        return resultado("SRI - Establecimientos", "fa-location-dot", "no_disponible",
                         "No se pudo consultar establecimientos del SRI.", nivel="limpio", tipo="informativo")


def resolver_cedula_por_nombre(nombre):
    """Resuelve nombre completo -> cedula(s) usando el registro de personas del SRI.

    Devuelve una lista de coincidencias: {identificacion, nombreCompleto, fallecido}.
    Intenta primero el endpoint oficial del SRI; si el firewall F5 lo bloquea,
    usa el proxy publico que reenvia la misma consulta al SRI.

    Nota: dato sensible. Solo debe usarse para verificar a una persona en un
    contexto autorizado; la fuente es la misma informacion publica del SRI.
    """
    nombre = (nombre or "").strip()
    if len(nombre) < 5:
        return []
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.ecuadorlegalonline.com/",
        "Origin": "https://www.ecuadorlegalonline.com",
    }

    def normalizar(items):
        out, vistos = [], set()
        for it in items or []:
            if not isinstance(it, dict):
                continue
            ide = (it.get("identificacion") or "").strip()
            if not ide or ide in vistos:
                continue
            vistos.add(ide)
            out.append({
                "identificacion": ide,
                "nombreCompleto": (it.get("nombreCompleto") or "").strip(),
                "fallecido": bool(it.get("fechaDefuncion")),
            })
        return out

    # 1) SRI oficial directo (suele bloquear F5, pero se intenta por si pasa)
    try:
        enc = quote(nombre)
        r = requests.get(f"{SRI_POR_NOMBRE_URL}/{enc}/",
                         params={"tipoPersona": "N", "resultados": "30"},
                         headers=headers, timeout=12)
        if r.status_code == 200 and "json" in r.headers.get("Content-Type", ""):
            return normalizar(r.json())
    except (requests.RequestException, ValueError):
        pass

    # 2) Proxy publico (reenvia al SRI)
    try:
        r = requests.get(CEDULA_POR_NOMBRE_PROXY,
                         params={"nombres": nombre}, headers=headers, timeout=15)
        r.raise_for_status()
        return normalizar(r.json())
    except (requests.RequestException, ValueError):
        return []
