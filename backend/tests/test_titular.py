"""Pruebas de la deduccion del nombre del titular desde los procesos judiciales.

Reproduce el caso real reportado: una causa de divorcio con tres co-actores y
otra causa donde el titular aparece con las palabras del nombre en otro orden.
"""
from app.fuentes import judicial
from app.fuentes.judicial import _clave_nombre, nombre_titular_desde_judicial


class TestClaveNombre:
    def test_agrupa_ordenes_distintos(self):
        assert _clave_nombre("UNTUÑA LICERO ANGEL PAUL") == _clave_nombre("ANGEL PAUL UNTUÑA LICERO")

    def test_normaliza_tildes(self):
        assert _clave_nombre("PÉREZ JOSÉ") == _clave_nombre("PEREZ JOSE")

    def test_nombres_distintos_no_se_agrupan(self):
        assert _clave_nombre("VALIENTE INES") != _clave_nombre("UNTUÑA ANGEL")


def _simular_litigantes(monkeypatch, por_causa):
    """obtener_litigantes falso: devuelve los litigantes definidos por causa."""
    monkeypatch.setattr(judicial, "obtener_litigantes",
                        lambda numero: por_causa.get(numero))


class TestNombreTitular:
    def test_caso_real_divorcio_mas_denuncia(self, monkeypatch):
        # Causa 1 (divorcio): tres co-actores. Causa 2: el titular solo, con el
        # nombre en otro orden. Antes ganaba el primer co-actor por empate;
        # ahora las variantes se agrupan y el titular gana 2 a 1.
        _simular_litigantes(monkeypatch, {
            "C1": {"actores": ["VALIENTE PILAGUANO INES MARGARITA",
                               "UNTUÑA LICERO ANGEL PAUL",
                               "UNTUÑA VALIENTE JOHAN JAREN"], "demandados": []},
            "C2": {"actores": ["ANGEL PAUL UNTUÑA LICERO"], "demandados": []},
        })
        causas = [{"numero": "C1", "rol": "Actor"}, {"numero": "C2", "rol": "Actor"}]
        assert nombre_titular_desde_judicial(causas) == "UNTUÑA LICERO ANGEL PAUL"

    def test_empate_devuelve_none(self, monkeypatch):
        # Una sola causa con dos co-actores: imposible saber cual es el titular
        _simular_litigantes(monkeypatch, {
            "C1": {"actores": ["PERSONA UNO", "PERSONA DOS"], "demandados": []},
        })
        assert nombre_titular_desde_judicial([{"numero": "C1", "rol": "Actor"}]) is None

    def test_unico_litigante_gana(self, monkeypatch):
        _simular_litigantes(monkeypatch, {
            "C1": {"actores": [], "demandados": ["GARCIA LOPEZ MARIA"]},
        })
        assert nombre_titular_desde_judicial([{"numero": "C1", "rol": "Demandado"}]) == "GARCIA LOPEZ MARIA"

    def test_sin_causas_devuelve_none(self, monkeypatch):
        _simular_litigantes(monkeypatch, {})
        assert nombre_titular_desde_judicial([]) is None
