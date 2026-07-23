"""Fuentes informativas sin API automatizable: Record Policial, Registro Social
y los stubs de titulos (SENESCYT / Bachiller) que se resuelven via relay de captcha."""
from ..config import ENLACES_OFICIALES
from ..utils import resultado


def consultar_record_policial(cedula):
    """Record policial / antecedentes penales. Sin API (captcha). INFORMATIVO."""
    return resultado(
        "Record Policial", "fa-fingerprint", "no_disponible",
        "El Ministerio del Gobierno no expone API publica (requiere captcha y "
        "validacion de identidad). Consulta el certificado en el portal oficial.",
        nivel="limpio", enlace=ENLACES_OFICIALES["record_policial"], tipo="informativo")


def consultar_senescyt(cedula):
    """Titulos de educacion superior (SENESCYT / SNIESE). INFORMATIVO.

    El portal de consulta de titulos es una app JSF/PrimeFaces protegida con
    un captcha de imagen (/Captcha.jpg por sesion) y requiere apellidos ademas
    de la identificacion. No expone API publica, por lo que se enlaza al portal
    oficial para la consulta manual (titulos de 3er y 4to nivel registrados).
    """
    return resultado(
        "Titulos Educacion Superior (SENESCYT)", "fa-user-graduate", "no_disponible",
        "Consulta protegida con captcha de imagen. Pulsa \"Consultar titulo "
        "(captcha)\" para resolver el captcha y traer los titulos de tercer y "
        "cuarto nivel registrados en el SNIESE.",
        nivel="limpio", enlace=ENLACES_OFICIALES["senescyt"],
        tipo="captcha", clave="senescyt")


def consultar_registro_social(cedula):
    """Registro Social (MIES / SIIRS) - nivel socioeconomico. INFORMATIVO.

    Dato socioeconomico protegido (LOPDP). El portal publico exige la fecha de
    expedicion de la cedula y resuelve un Google reCAPTCHA v2, por lo que no es
    automatizable; se enlaza al SIIRS para la consulta manual con consentimiento.
    """
    return resultado(
        "Registro Social (MIES)", "fa-house-user", "no_disponible",
        "Dato socioeconomico protegido (LOPDP). El portal exige la fecha de "
        "expedicion de la cedula y un reCAPTCHA de Google (no automatizable). "
        "Pulsa \"Abrir SIIRS\" para consultar manualmente: se copia la cedula y "
        "se abre el portal oficial; alli ingresas la fecha de expedicion y "
        "resuelves el reCAPTCHA.",
        nivel="limpio", enlace=ENLACES_OFICIALES["registro_social"],
        tipo="informativo", clave="registro_social")


def consultar_bachiller(cedula):
    """Titulo de bachiller (Ministerio de Educacion). INFORMATIVO.

    La consulta de titulos refrendados es una app JSF protegida con captcha de
    imagen; no hay API publica. Se enlaza al portal oficial del MinEduc.
    """
    return resultado(
        "Titulo de Bachiller (MinEduc)", "fa-graduation-cap", "no_disponible",
        "Consulta protegida con captcha de imagen. Pulsa \"Consultar titulo "
        "(captcha)\" para resolver el captcha y traer el titulo de bachiller y "
        "su numero de refrendacion desde el portal del MinEduc.",
        nivel="limpio", enlace=ENLACES_OFICIALES["bachiller"],
        tipo="captcha", clave="bachiller")
