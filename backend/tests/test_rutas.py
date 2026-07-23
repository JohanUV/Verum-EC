"""Pruebas de rutas, autenticacion y permisos (sin llamar APIs externas)."""
import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def login(client, usuario, clave):
    return client.post("/api/login", json={"username": usuario, "password": clave})


def test_landing_publica_en_raiz(client):
    # La raiz "/" es la landing publica de presentacion (sin sesion, 200).
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Verum" in html
    assert 'id="contacto"' in html


def test_app_redirige_sin_sesion(client):
    # La aplicacion protegida vive en "/app" y exige sesion.
    res = client.get("/app")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_contacto_valida_datos(client):
    # Formulario de contacto: rechaza datos incompletos, acepta validos.
    assert client.post("/api/contacto", json={"nombre": "ab", "email": "x", "mensaje": "corto"}).status_code == 400
    ok = client.post("/api/contacto", json={
        "nombre": "Persona Prueba", "email": "p@ejemplo.com",
        "mensaje": "Mensaje de prueba con longitud suficiente."})
    assert ok.status_code == 200
    assert ok.get_json()["ok"] is True


def test_api_sin_sesion_devuelve_401(client):
    assert client.post("/api/verificar", json={"cedula": "0959083015"}).status_code == 401


def test_login_correcto_devuelve_permisos(client):
    res = login(client, "admin", "admin123")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True
    assert data["rol"] == "admin"
    assert "historial" in data["permisos"]


def test_login_incorrecto(client):
    assert login(client, "admin", "clave-mala").status_code == 401


def test_cedula_invalida_da_400(client):
    login(client, "admin", "admin123")
    res = client.post("/api/verificar", json={"cedula": "123"})
    assert res.status_code == 400


def test_analista_no_accede_a_historial(client):
    # El permiso "historial" es solo del rol admin
    res = login(client, "analista", "verum2026")
    assert res.status_code == 200
    assert client.get("/api/historial").status_code == 403


def test_verificar_masivo_ya_no_existe(client):
    # La busqueda masiva se elimino del producto: la ruta no debe existir
    login(client, "admin", "admin123")
    assert client.post("/api/verificar-masivo", json={"cedulas": "0959083015"}).status_code == 404


def test_login_sin_datos_da_400(client):
    assert client.post("/api/login", json={}).status_code == 400


def test_app_con_sesion_carga_bundle_react(client):
    login(client, "admin", "admin123")
    res = client.get("/app")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'id="root"' in html
    assert "dist/app.js" in html
