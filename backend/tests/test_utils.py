"""Pruebas de las utilidades puras (sin red)."""
from app.utils import calcular_riesgo, cedula_valida, resultado


class TestCedulaValida:
    def test_cedula_correcta(self):
        assert cedula_valida("0959083015") is True

    def test_digito_verificador_incorrecto(self):
        assert cedula_valida("0959083016") is False

    def test_longitud_invalida(self):
        assert cedula_valida("095908301") is False
        assert cedula_valida("09590830155") is False

    def test_no_numerica(self):
        assert cedula_valida("0959A83015") is False
        assert cedula_valida("") is False
        assert cedula_valida(None) is False

    def test_provincia_fuera_de_rango(self):
        # Provincia 25 no existe (01-24)
        assert cedula_valida("2523115083") is False
        assert cedula_valida("0023115083") is False


class TestCalcularRiesgo:
    def test_sin_hallazgos(self):
        score, etiqueta = calcular_riesgo([{"nivel": "limpio"}] * 5)
        assert score == 0
        assert etiqueta == "Sin riesgo detectado"

    def test_una_atencion(self):
        score, etiqueta = calcular_riesgo([{"nivel": "atencion"}])
        assert score == 15
        assert etiqueta == "Riesgo bajo"

    def test_alerta_y_atencion(self):
        score, etiqueta = calcular_riesgo([{"nivel": "alerta"}, {"nivel": "atencion"}])
        assert score == 50
        assert etiqueta == "Riesgo medio"

    def test_riesgo_alto_con_tope_100(self):
        score, etiqueta = calcular_riesgo([{"nivel": "alerta"}] * 4)
        assert score == 100
        assert etiqueta == "Riesgo alto"


class TestResultado:
    def test_estructura_normalizada(self):
        r = resultado("Fuente X", "fa-icono", "ok", "Resumen")
        assert r["fuente"] == "Fuente X"
        assert r["datos"] == []
        assert r["nivel"] == "limpio"
        assert r["tipo"] == "real"
        assert r["clave"] is None
