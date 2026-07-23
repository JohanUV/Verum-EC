"""Verum - Plataforma de Verificacion de Antecedentes (Ecuador).

Fabrica de la aplicacion Flask. Estructura:
  app/routes/   -> public (login), users (sesion), private (interfaz), api (JSON)
  app/models/   -> usuarios y roles
  app/forms/    -> validacion de datos de entrada
  app/fuentes/  -> un modulo de consulta por institucion
  app/services.py -> orquestacion de la verificacion
"""
import os
import secrets

from flask import Flask


def create_app():
    app = Flask(__name__)
    # La clave de sesion se toma de la variable de entorno VERUM_SECRET_KEY.
    # En produccion DEBE definirse (si no, se genera una aleatoria y las
    # sesiones se invalidan en cada reinicio).
    app.secret_key = os.environ.get("VERUM_SECRET_KEY") or secrets.token_hex(32)

    from .routes.api import bp as api_bp
    from .routes.private import bp as private_bp
    from .routes.public import bp as public_bp
    from .routes.users import bp as users_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(private_bp)
    app.register_blueprint(api_bp)
    return app
