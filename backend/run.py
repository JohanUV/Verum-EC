"""Punto de entrada de Verum:  python run.py"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug SOLO se activa si VERUM_DEBUG=1 (jamas en produccion: el modo
    # debug expone el codigo y una consola ejecutable ante cualquier error).
    debug = os.environ.get("VERUM_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=debug, host="0.0.0.0", port=port)
