"""SUPA (Funcion Judicial): pensiones alimenticias. API REAL via JSF."""
import re
import requests

from ..config import ENLACES_OFICIALES, USER_AGENT
from ..utils import resultado

# Consulta publica JSF/PrimeFaces de la Funcion Judicial
SUPA_URL = "https://supa.funcionjudicial.gob.ec/pensiones/publico/consulta.jsf"


def consultar_pensiones(cedula):
    """Pensiones alimenticias (SUPA) - API REAL.

    La consulta publica de SUPA es una app JSF/PrimeFaces: se hace un GET para
    obtener el ViewState y las cookies de sesion, y luego un POST AJAX que
    devuelve un partial-response XML con la tabla de tarjetas de pension donde
    la persona figura como obligado o representante legal.
    """
    fuente, icono = "Pensiones Alimenticias (SUPA)", "fa-hand-holding-heart"
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": USER_AGENT})
        g = s.get(SUPA_URL, timeout=15)
        m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', g.text)
        if not m:
            raise ValueError("Sin ViewState")
        view_state = m.group(1)
        data = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "form:b_buscar_cedula",
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "form:pResultado panelMensajes form:pFiltro",
            "form:b_buscar_cedula": "form:b_buscar_cedula",
            "form": "form",
            "form:t_texto_cedula": cedula,
            "form:s_criterio_busqueda": "Seleccione...",
            "form:t_texto": "",
            "javax.faces.ViewState": view_state,
        }
        headers = {
            "Faces-Request": "partial/ajax",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        p = s.post(SUPA_URL, data=data, headers=headers, timeout=20)
        bloque = re.search(
            r'<update id="form:pResultado"><!\[CDATA\[(.*?)\]\]></update>',
            p.text, re.S)
        if not bloque:
            return resultado(fuente, icono, "sin_resultados",
                             "Sin registros de pension alimenticia.",
                             nivel="limpio", enlace=ENLACES_OFICIALES["pensiones"])

        html = bloque.group(1)
        filas = _parsear_tarjetas_supa(html)
        if not filas:
            return resultado(fuente, icono, "sin_resultados",
                             "La persona no registra tarjetas de pension alimenticia.",
                             nivel="limpio", enlace=ENLACES_OFICIALES["pensiones"])

        datos = []
        for f in filas[:8]:
            etiqueta = f"Tarjeta {f['tarjeta']} ({f['rol']})"
            valor = f"{f['tipo']} - Proceso {f['proceso']} - {f['dependencia']}"
            datos.append({"campo": etiqueta, "valor": valor})

        obligado = any(f["rol"] == "Obligado" for f in filas)
        nivel = "atencion" if obligado else "limpio"
        if obligado:
            resumen = (f"Registra {len(filas)} tarjeta(s) de pension alimenticia "
                       f"como OBLIGADO. Verifique si mantiene valores pendientes.")
        else:
            resumen = (f"Aparece en {len(filas)} tarjeta(s) de pension como "
                       f"representante legal (no como obligado).")
        return resultado(fuente, icono, "ok", resumen, datos=datos,
                         nivel=nivel, enlace=ENLACES_OFICIALES["pensiones"])
    except (requests.RequestException, ValueError):
        return resultado(
            fuente, icono, "no_disponible",
            "No se pudo consultar SUPA en este momento. Verifique en el portal oficial.",
            nivel="limpio", enlace=ENLACES_OFICIALES["pensiones"], tipo="informativo")


def _parsear_tarjetas_supa(html):
    """Extrae las filas de la tabla de resultados de SUPA (tarjetas de pension)."""
    filas = []
    # La cedula consultada figura como Obligado o como Representante Legal.
    for fila in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.S)
        if len(celdas) < 5:
            continue
        limpio = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in celdas]
        tarjeta = limpio[0]
        # filtra encabezados o celdas vacias
        if not re.match(r"^\d{3,}-?\d", tarjeta):
            continue
        intervinientes = limpio[4] if len(limpio) > 4 else ""
        rol = "Obligado" if "Obligado" in intervinientes else "Representante"
        filas.append({
            "tarjeta": tarjeta,
            "proceso": limpio[1] if len(limpio) > 1 else "",
            "dependencia": limpio[2] if len(limpio) > 2 else "",
            "tipo": limpio[3] if len(limpio) > 3 else "Pension alimenticia",
            "rol": rol,
        })
    return filas
