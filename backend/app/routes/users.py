"""Rutas de usuarios: inicio y cierre de sesion (API JSON)."""
from flask import Blueprint, jsonify, request, session

from ..forms.users import LoginForm
from ..models.users import permisos_de_rol, verificar_credenciales

bp = Blueprint("users", __name__, url_prefix="/api")


@bp.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.json)
    if not form.es_valido():
        return jsonify({"error": " ".join(form.errores)}), 400
    u = verificar_credenciales(form.username, form.password)
    if not u:
        return jsonify({"error": "Credenciales incorrectas"}), 401
    session["user"] = form.username
    session["rol"] = u["rol"]
    session["permisos"] = permisos_de_rol(u["rol"])
    return jsonify({"ok": True, "user": form.username, "rol": u["rol"],
                    "permisos": session["permisos"]})


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})
