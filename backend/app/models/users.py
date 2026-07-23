"""Modelo de usuarios: cuentas, roles y verificacion de credenciales."""
import os

from werkzeug.security import check_password_hash

# Roles y permisos. Cada rol agrupa un conjunto de acciones permitidas.
ROLES = {
    "admin":     {"verificar", "exportar", "historial", "nombre"},
    "analista":  {"verificar", "exportar", "nombre"},
    "consultor": {"verificar"},
}

# Las contrasenas se guardan HASHEADAS (pbkdf2:sha256), nunca en texto plano.
# Para cambiar una clave en produccion, define la variable de entorno con su
# nuevo hash: VERUM_HASH_ADMIN / VERUM_HASH_ANALISTA / VERUM_HASH_CONSULTOR.
# Generar un hash:  python -c "from werkzeug.security import generate_password_hash as g; print(g('TU_CLAVE', method='pbkdf2:sha256'))"
USERS = {
    "admin":     {"password_hash": os.environ.get("VERUM_HASH_ADMIN",     "pbkdf2:sha256:1000000$8S927HGNY4R0j2Qf$b9ea46d37c90aea852e95b464f5370e6db9b7ff95a8dfac145f205ae1c904077"), "rol": "admin",     "nombre": "Administrador"},
    "analista":  {"password_hash": os.environ.get("VERUM_HASH_ANALISTA",  "pbkdf2:sha256:1000000$xhn56iJ2$a72b0807c858e987448e28a5f196cf0462852f9ad84aa0ea9a576913363b1175"), "rol": "analista",  "nombre": "Analista"},
    "consultor": {"password_hash": os.environ.get("VERUM_HASH_CONSULTOR", "pbkdf2:sha256:1000000$P3dMzKJD7zf0OOwd$468247aedb54a7f7a05e4030905b541f997f1a03637f81a373804effc7a32311"), "rol": "consultor", "nombre": "Consultor"},
}


def obtener_usuario(username):
    """Devuelve el registro del usuario o None."""
    return USERS.get(username)


def permisos_de_rol(rol):
    """Permisos (ordenados) que corresponden a un rol."""
    return sorted(ROLES.get(rol, set()))


def verificar_credenciales(username, password):
    """Valida usuario y contrasena. Devuelve el registro del usuario o None."""
    u = USERS.get(username)
    if u and check_password_hash(u["password_hash"], password):
        return u
    return None
