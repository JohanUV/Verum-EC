"""Rutas publicas (sin sesion): landing de presentacion, acceso y contacto."""
import json
import os
import re
import threading
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from ..config import DATA_DIR

bp = Blueprint("public", __name__)

CONTACTOS_FILE = os.path.join(DATA_DIR, "contactos.json")
_CONTACTOS_LOCK = threading.Lock()
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.route("/")
def landing():
    """Pagina publica de presentacion (antes de iniciar sesion)."""
    return render_template("public/landing.html")


@bp.route("/login")
def login_page():
    return render_template("users/login.html")


@bp.route("/api/contacto", methods=["POST"])
def contacto():
    """Recibe el formulario de contacto de la landing y lo guarda en disco.

    Se almacena en data/contactos.json para poder automatizar el seguimiento
    (envio de correo, CRM, etc.) mas adelante.
    """
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get("nombre") or "").strip()
    email = (datos.get("email") or "").strip()
    mensaje = (datos.get("mensaje") or "").strip()

    errores = []
    if len(nombre) < 3:
        errores.append("Ingresa tu nombre.")
    if not _EMAIL_RE.match(email):
        errores.append("Ingresa un correo valido.")
    if len(mensaje) < 10:
        errores.append("El mensaje debe tener al menos 10 caracteres.")
    if errores:
        return jsonify({"error": " ".join(errores)}), 400

    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nombre": nombre[:120],
        "email": email[:120],
        "telefono": (datos.get("telefono") or "").strip()[:40],
        "asunto": (datos.get("asunto") or "").strip()[:120],
        "mensaje": mensaje[:2000],
    }
    with _CONTACTOS_LOCK:
        try:
            with open(CONTACTOS_FILE, "r", encoding="utf-8") as f:
                lista = json.load(f)
                if not isinstance(lista, list):
                    lista = []
        except (OSError, ValueError):
            lista = []
        lista.insert(0, entrada)
        try:
            with open(CONTACTOS_FILE, "w", encoding="utf-8") as f:
                json.dump(lista[:500], f, ensure_ascii=False, indent=2)
        except OSError:
            return jsonify({"error": "No se pudo guardar el mensaje."}), 500

    return jsonify({"ok": True, "mensaje": "¡Gracias! Tu mensaje fue recibido, te contactaremos pronto."})
