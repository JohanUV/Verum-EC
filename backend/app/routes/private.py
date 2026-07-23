"""Rutas privadas (requieren sesion): interfaz principal."""
from flask import Blueprint, render_template, session

from ..auth import asegurar_permisos, login_required

bp = Blueprint("private", __name__)


@bp.route("/app")
@login_required
def index():
    asegurar_permisos()
    return render_template("private/index.html",
                           user=session.get("user"),
                           rol=session.get("rol", ""),
                           permisos=session.get("permisos", []))
