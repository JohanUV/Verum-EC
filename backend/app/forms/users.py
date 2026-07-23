"""Validacion de los datos de entrada de usuarios (peticiones JSON)."""


class LoginForm:
    """Valida el cuerpo JSON del login: usuario y contrasena obligatorios."""

    def __init__(self, data):
        data = data or {}
        self.username = (data.get("username", "") or "").strip()
        self.password = data.get("password", "") or ""
        self.errores = []

    def es_valido(self):
        if not self.username:
            self.errores.append("El usuario es obligatorio.")
        if not self.password:
            self.errores.append("La contrasena es obligatoria.")
        return not self.errores
