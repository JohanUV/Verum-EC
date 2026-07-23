"""Relay de captcha para fuentes JSF protegidas (Bachiller MinEduc / SENESCYT).

Estas consultas exigen resolver un captcha de imagen, por lo que no se pueden
automatizar dentro del barrido en paralelo. En su lugar, Verum abre la
sesion JSF, le muestra la imagen del captcha al usuario y, cuando este lo
escribe, reenvia la consulta y devuelve los titulos. El usuario es quien
resuelve el captcha: no se intenta romperlo automaticamente.
"""
import base64
import os
import re
import secrets
import threading
import time
from html import unescape

import requests

from ..config import DATA_DIR, USER_AGENT

JSF_CAPTCHA_FUENTES = {
    "bachiller": {
        "nombre": "Titulo de Bachiller (MinEduc)",
        "page": "https://servicios.educacion.gob.ec/titulacion25-web/faces/paginas/consulta-titulos-refrendados.xhtml",
        "captcha": "https://servicios.educacion.gob.ec/titulacion25-web/Captcha.jpg",
        "origin": "https://servicios.educacion.gob.ec",
        "form": "formBusqueda",
        "campo_cedula": "formBusqueda:cedula",
        "campo_captcha": "formBusqueda:captcha",
        "boton": "formBusqueda:clBuscar",
        # selecItem=1 -> buscar por "Nº de Identificacion"
        "extra": {"formBusqueda:selecItem": "1"},
    },
    "senescyt": {
        "nombre": "Titulos Educacion Superior (SENESCYT)",
        "page": "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml",
        "captcha": "https://www.senescyt.gob.ec/consulta-titulos-web/Captcha.jpg",
        "origin": "https://www.senescyt.gob.ec",
        "form": "formPrincipal",
        "campo_cedula": "formPrincipal:identificacion",
        "campo_captcha": "formPrincipal:captchaSellerInput",
        "campo_apellidos": "formPrincipal:apellidos",
        "boton": "formPrincipal:boton-buscar",
        "extra": {},
    },
}

_CAPTCHA_SESIONES = {}
_CAPTCHA_LOCK = threading.Lock()
_CAPTCHA_TTL = 300  # 5 minutos de vida por captcha


def _limpiar_captchas():
    """Elimina las sesiones de captcha expiradas (llamar con el lock tomado)."""
    ahora = time.time()
    muertos = [t for t, s in _CAPTCHA_SESIONES.items() if ahora - s["ts"] > _CAPTCHA_TTL]
    for t in muertos:
        _CAPTCHA_SESIONES.pop(t, None)


def _viewstate(html_txt):
    """Extrae el javax.faces.ViewState de una pagina JSF."""
    m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]*)"', html_txt)
    if not m:
        m = re.search(r'ViewState"[^>]*value="([^"]*)"', html_txt)
    return m.group(1) if m else None


def iniciar_captcha(clave):
    """Abre una sesion JSF, descarga el captcha y la cachea.

    Devuelve (token, data_uri_imagen) o lanza ValueError con un mensaje.
    """
    cfg = JSF_CAPTCHA_FUENTES.get(clave)
    if not cfg:
        raise ValueError("Fuente no valida.")
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    page = s.get(cfg["page"], timeout=35)
    page.raise_for_status()
    vs = _viewstate(page.text)
    if not vs:
        raise ValueError("No se pudo iniciar la sesion de consulta.")
    img = s.get(cfg["captcha"], timeout=25)
    if img.status_code != 200 or "image" not in img.headers.get("Content-Type", ""):
        raise ValueError("No se pudo cargar la imagen del captcha.")
    b64 = base64.b64encode(img.content).decode()
    token = secrets.token_urlsafe(16)
    with _CAPTCHA_LOCK:
        _limpiar_captchas()
        _CAPTCHA_SESIONES[token] = {
            "session": s, "viewstate": vs, "clave": clave, "ts": time.time(),
        }
    ctype = img.headers.get("Content-Type", "image/jpeg").split(";")[0]
    return token, "data:%s;base64,%s" % (ctype, b64)


def _limpiar_scripts(html_raw):
    """Quita bloques <script>/<style> (RichFaces inyecta JS de paginacion)."""
    h = re.sub(r'<script\b[^>]*>.*?</script>', ' ', html_raw, flags=re.S | re.I)
    h = re.sub(r'<style\b[^>]*>.*?</style>', ' ', h, flags=re.S | re.I)
    return h


def _extraer_tablas(html_raw):
    """Extrae todas las tablas HTML como listas de filas (listas de celdas)."""
    html_raw = _limpiar_scripts(html_raw)
    tablas = []
    for tabla in re.findall(r'<table\b[^>]*>(.*?)</table>', html_raw, re.S | re.I):
        filas = []
        for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>', tabla, re.S | re.I):
            celdas = re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', tr, re.S | re.I)
            celdas = [unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', c))).strip()
                      for c in celdas]
            if celdas:
                filas.append(celdas)
        if filas:
            tablas.append(filas)
    return tablas


def _parsear_titulos_jsf(html_raw):
    """Extrae informacion personal y la tabla de titulos de la respuesta JSF."""
    texto = unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html_raw)))
    ident = ""
    m = re.search(r'Identificaci[oó]n\s*:?\s*([0-9]{6,13})', texto)
    if m:
        ident = m.group(1)
    nombres = ""
    m = re.search(r'Nombres?\s*:?\s*([A-ZÑÁÉÍÓÚÜ][A-ZÑÁÉÍÓÚÜ.\s]+?)\s+'
                  r'(?:Ver informaci|Identificaci|T[IÍ]TULO|Imprimir|Instituci)', texto)
    if m:
        nombres = m.group(1).strip()

    titulos = []
    kw = r't[íi]tulo|refrendaci|instituci|especialidad|nivel|carrera|fecha\s*grado'
    for filas in _extraer_tablas(html_raw):
        if len(filas) < 2:
            continue
        # La fila de encabezado es la primera con >=3 columnas y palabras clave
        # (asi se ignora el "caption" de una sola celda del dataTable).
        hdr_idx = None
        for idx, fila in enumerate(filas):
            if len(fila) >= 3 and re.search(kw, " ".join(fila).lower()):
                hdr_idx = idx
                break
        if hdr_idx is None:
            continue
        encabezado = filas[hdr_idx]
        for fila in filas[hdr_idx + 1:]:
            valores = "".join(fila).strip()
            # ignora filas vacias, paginacion (datascroller) o residuales
            if len(fila) < 2 or not re.search(r'[A-Za-zÁÉÍÓÚÑ0-9]', valores):
                continue
            if re.search(r'richfaces|datascroller|datatable', valores, re.I):
                continue
            registro = {}
            for i, col in enumerate(encabezado):
                clave = (col or ("Columna %d" % (i + 1))).strip()
                registro[clave] = fila[i] if i < len(fila) else ""
            titulos.append(registro)
        if titulos:
            break
    return {"identificacion": ident, "nombres": nombres, "titulos": titulos}


def consultar_captcha(token, cedula, captcha, apellidos=""):
    """Reenvia la consulta JSF con el captcha resuelto por el usuario.

    Devuelve un dict con: ok/error/captcha + titulos. No lanza excepciones de red
    (las captura y devuelve {"error": ...}).
    """
    with _CAPTCHA_LOCK:
        sesion = _CAPTCHA_SESIONES.get(token)
    if not sesion:
        return {"error": "expirado", "mensaje": "La sesion del captcha expiro. Genera uno nuevo."}
    cfg = JSF_CAPTCHA_FUENTES[sesion["clave"]]
    captcha = (captcha or "").strip()
    if not captcha:
        return {"error": "vacio", "mensaje": "Escribe el texto del captcha."}

    boton, form = cfg["boton"], cfg["form"]
    body = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": boton,
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": form,
        boton: boton,
        form: form,
        cfg["campo_cedula"]: cedula,
        cfg["campo_captcha"]: captcha,
        "javax.faces.ViewState": sesion["viewstate"],
    }
    body.update(cfg.get("extra", {}))
    if apellidos and cfg.get("campo_apellidos"):
        body[cfg["campo_apellidos"]] = apellidos
    headers = {
        "Faces-Request": "partial/ajax",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Origin": cfg["origin"],
        "Referer": cfg["page"],
        "User-Agent": USER_AGENT,
    }
    sess = sesion["session"]

    def _post(cuerpo):
        return sess.post(cfg["page"], data=cuerpo, headers=headers, timeout=25).text

    try:
        texto = _post(body)

        if re.search(r'captcha[^<]{0,40}incorrect', texto, re.I) or \
           re.search(r'incorrect[^<]{0,20}captcha', texto, re.I) or \
           re.search(r'c[oó]digo[^<]{0,30}(incorrect|err[oó]n)', texto, re.I):
            return {"error": "captcha", "mensaje": "El captcha es incorrecto. Genera uno nuevo e intentalo otra vez."}

        parsed = _parsear_titulos_jsf(texto)

        # Paso 2: algunos portales (MinEduc) muestran primero los datos
        # personales con un boton "Ver informacion" que despliega los titulos.
        if not parsed["titulos"]:
            ver = re.search(r'id="((?:formBusqueda|formPrincipal):[^"]+)"[^>]*'
                            r'value="[^"]*informaci', texto, re.I)
            if ver:
                bid = ver.group(1)
                vs2 = re.search(r'<update id="[^"]*ViewState[^"]*"><!\[CDATA\[(.*?)\]\]>',
                                texto, re.S)
                nuevo_vs = vs2.group(1) if vs2 else sesion["viewstate"]
                body2 = {
                    "javax.faces.partial.ajax": "true",
                    "javax.faces.source": bid,
                    "javax.faces.partial.execute": "@all",
                    "javax.faces.partial.render": form,
                    bid: bid,
                    form: form,
                    cfg["campo_cedula"]: cedula,
                    cfg["campo_captcha"]: captcha,
                    "javax.faces.ViewState": nuevo_vs,
                }
                body2.update(cfg.get("extra", {}))
                texto2 = _post(body2)
                p2 = _parsear_titulos_jsf(texto2)
                if p2["titulos"] or p2["nombres"]:
                    parsed = p2
                texto = texto2  # para el volcado de depuracion
    except requests.RequestException:
        return {"error": "red", "mensaje": "El portal oficial no respondio. Intenta de nuevo."}
    finally:
        # el captcha es de un solo uso: se invalida para forzar uno nuevo
        with _CAPTCHA_LOCK:
            _CAPTCHA_SESIONES.pop(token, None)

    if not parsed["titulos"]:
        # Volcado temporal solo cuando no se pudieron leer titulos (depuracion)
        try:
            dbg = os.path.join(DATA_DIR, "_debug_captcha_%s.html" % sesion["clave"])
            with open(dbg, "w", encoding="utf-8") as f:
                f.write(texto)
        except OSError:
            pass
        if re.search(r'no\s+(se\s+)?(obtuv|encontr|registr|existe|posee|tiene|hay)\w*'
                     r'(\s+\w+){0,3}\s+(resultado|titulo|t[íi]tulo|registro|criterio)',
                     texto, re.I) or \
           re.search(r'no\s+(se\s+)?(obtuv|encontr|registr)', texto, re.I):
            return {"ok": True, "sin_resultados": True, "nombres": parsed["nombres"],
                    "identificacion": parsed["identificacion"] or cedula, "titulos": [],
                    "mensaje": "No se encontraron titulos registrados para esa identificacion."}
        return {"ok": True, "sin_resultados": True, "nombres": parsed["nombres"],
                "identificacion": parsed["identificacion"] or cedula, "titulos": [],
                "mensaje": "No se pudieron leer titulos en la respuesta. Verifica la cedula e intenta de nuevo."}
    return {"ok": True, "fuente": cfg["nombre"], "nombres": parsed["nombres"],
            "identificacion": parsed["identificacion"] or cedula, "titulos": parsed["titulos"]}
