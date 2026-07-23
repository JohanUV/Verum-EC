"""Configuracion central de Verum.

Roles, usuarios, catalogos y constantes compartidas por todos los modulos.
"""
import os

# Raiz del proyecto (carpeta que contiene app/, data/, run.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

PROVINCIAS = {
    "01": "Azuay", "02": "Bolivar", "03": "Canar", "04": "Carchi",
    "05": "Cotopaxi", "06": "Chimborazo", "07": "El Oro", "08": "Esmeraldas",
    "09": "Guayas", "10": "Imbabura", "11": "Loja", "12": "Los Rios",
    "13": "Manabi", "14": "Morona Santiago", "15": "Napo", "16": "Pastaza",
    "17": "Pichincha", "18": "Tungurahua", "19": "Zamora Chinchipe",
    "20": "Galapagos", "21": "Sucumbios", "22": "Orellana",
    "23": "Santo Domingo", "24": "Santa Elena"
}

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Enlaces oficiales para los modulos que no exponen API
ENLACES_OFICIALES = {
    "record_policial": "https://certificados.ministeriodelgobierno.gob.ec/",
    "ant": "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_grid_citaciones.jsp",
    "pensiones": "https://supa.funcionjudicial.gob.ec/",
    "senescyt": "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml",
    "registro_social": "https://siirs.registrosocial.gob.ec/pages/publico/busquedaPublica.jsf",
    "bachiller": "https://servicios.educacion.gob.ec/titulacion25-web/faces/paginas/consulta-titulos-refrendados.xhtml",
}
