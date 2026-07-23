"""API JSON privada: verificacion, historial, captcha relay y busquedas."""
import requests
from flask import Blueprint, jsonify, request, session

from ..auth import login_required, permiso_required
from ..fuentes.captcha_relay import (JSF_CAPTCHA_FUENTES, consultar_captcha,
                                     iniciar_captcha)
from ..fuentes.demo import informe_demo
from ..fuentes.judicial import buscar_procesos_por_nombre, obtener_litigantes
from ..fuentes.sri import resolver_cedula_por_nombre
from ..historial import leer_historial
from ..services import verificacion_completa
from ..utils import cedula_valida

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/verificar", methods=["POST"])
@login_required
def verificar():
    data = request.json or {}
    cedula = (data.get("cedula", "") or "").strip()
    proposito = (data.get("proposito", "") or "").strip() or "No especificado"

    if not cedula_valida(cedula):
        return jsonify({"error": "Cedula invalida. Debe tener 10 digitos validos."}), 400

    # Modo demostracion: informe simulado garantizado, sin salir a la red
    # (para presentaciones/pruebas cuando las fuentes en vivo no responden).
    if data.get("demo"):
        return jsonify(informe_demo(cedula, proposito, session.get("user", "—")))

    informe = verificacion_completa(cedula, proposito, session.get("user", "—"))
    return jsonify(informe)


@bp.route("/historial", methods=["GET"])
@permiso_required("historial")
def historial():
    """Devuelve las ultimas consultas realizadas (auditoria)."""
    return jsonify({"historial": leer_historial()})


@bp.route("/captcha/iniciar", methods=["POST"])
@login_required
def captcha_iniciar():
    """Abre la sesion JSF de una fuente con captcha y devuelve la imagen."""
    data = request.json or {}
    clave = (data.get("fuente", "") or "").strip()
    try:
        token, imagen = iniciar_captcha(clave)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.RequestException:
        return jsonify({"error": "El portal oficial no respondio. Intenta de nuevo."}), 502
    return jsonify({"token": token, "imagen": imagen,
                    "nombre": JSF_CAPTCHA_FUENTES[clave]["nombre"]})


@bp.route("/captcha/consultar", methods=["POST"])
@login_required
def captcha_consultar():
    """Reenvia la consulta JSF con el captcha resuelto y devuelve los titulos."""
    data = request.json or {}
    token = (data.get("token", "") or "").strip()
    cedula = (data.get("cedula", "") or "").strip()
    captcha = (data.get("captcha", "") or "").strip()
    apellidos = (data.get("apellidos", "") or "").strip()
    res = consultar_captcha(token, cedula, captcha, apellidos)
    return jsonify(res)


@bp.route("/proceso-detalle", methods=["POST"])
@login_required
def proceso_detalle():
    """Detalle de un proceso: actores, demandados, judicatura y ciudad."""
    data = request.json or {}
    idj = (data.get("idJuicio", "") or "").strip()
    if not idj:
        return jsonify({"error": "Falta el numero de proceso."}), 400
    det = obtener_litigantes(idj)
    if not det:
        return jsonify({"error": "Detalle no disponible (proceso reservado o sin respuesta)."}), 502
    return jsonify(det)


@bp.route("/buscar-nombre", methods=["POST"])
@login_required
def buscar_nombre():
    """Busca procesos judiciales por nombre (actor y/o demandado).

    Limitacion conocida: la API de la Funcion Judicial NO expone la cedula ni el
    nombre completo de las partes en el listado, por lo que no es posible separar
    a distintas personas que compartan el mismo nombre. Se devuelven los procesos
    coincidentes para revision manual.
    """
    data = request.json or {}
    nombre = (data.get("nombre", "") or "").strip().upper()
    if len(nombre) < 5:
        return jsonify({"error": "Ingresa un nombre y apellido (minimo 5 caracteres)."}), 400
    try:
        procesos = buscar_procesos_por_nombre(nombre)
        return jsonify({"nombre": nombre, "total": len(procesos), "procesos": procesos})
    except requests.RequestException as e:
        return jsonify({"error": f"No se pudo consultar la Funcion Judicial: {e}"}), 500


@bp.route("/cedula-por-nombre", methods=["POST"])
@login_required
def cedula_por_nombre():
    """Resuelve nombre completo -> cedula(s) usando el registro del SRI.

    Devuelve las coincidencias para que el analista seleccione a la persona y
    ejecute una verificacion completa por cedula. Fuente: SRI (dato publico).
    """
    data = request.json or {}
    nombre = (data.get("nombre", "") or "").strip()
    if len(nombre) < 5:
        return jsonify({"error": "Ingresa nombres y apellidos completos (minimo 5 caracteres)."}), 400
    coincidencias = resolver_cedula_por_nombre(nombre)
    return jsonify({
        "nombre": nombre,
        "total": len(coincidencias),
        "coincidencias": coincidencias,
        "fuente": "SRI (registro de personas)",
    })
