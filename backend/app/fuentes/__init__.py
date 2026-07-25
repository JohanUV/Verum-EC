"""Modulos de consulta, uno por fuente. MODULOS define el barrido en paralelo
de la verificacion completa (el orden es el orden de aparicion en el informe)."""
from .judicial import consultar_judicial
from .sri import consultar_sri, consultar_sri_deudas, consultar_sri_establecimientos
from .supa import consultar_pensiones
from .ant import consultar_ant

MODULOS = [
    consultar_judicial,
    consultar_sri,
    consultar_sri_establecimientos,
    consultar_sri_deudas,
    consultar_pensiones,
    consultar_ant,
]
