"""Autenticacion y autorizacion: decoradores de sesion y permisos por rol."""
from functools import wraps

from flask import jsonify, redirect, request, session, url_for

from .models.users import obtener_usuario, permisos_de_rol


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "No autorizado"}), 401
            return redirect(url_for("public.login_page"))
        return f(*args, **kwargs)
    return decorated


def asegurar_permisos():
    """Rellena rol/permisos en la sesion si faltan (sesiones previas a los roles)."""
    u = obtener_usuario(session.get("user"))
    if u and "permisos" not in session:
        session["rol"] = u["rol"]
        session["permisos"] = permisos_de_rol(u["rol"])


def permiso_required(permiso):
    """Exige que el usuario en sesion tenga el permiso indicado."""
    def decorador(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("user"):
                return jsonify({"error": "No autorizado"}), 401
            asegurar_permisos()
            if permiso not in set(session.get("permisos", [])):
                return jsonify({"error": "No tienes permiso para esta accion."}), 403
            return f(*args, **kwargs)
        return decorated
    return decorador
