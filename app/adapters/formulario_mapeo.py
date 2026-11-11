"""Mapeo entre las preguntas del formulario y los campos del sistema.

Cada pregunta se identifica por el INICIO de su titulo, sin tildes ni signos
y sin la numeracion. Las columnas que no aparecen aqui se ignoran.
"""
import hashlib
import json
import re
from datetime import date, datetime, timedelta, timezone

from app.core.textos import normalizar, solo_digitos
from app.models.enums import Localidad

ZONA = timezone(timedelta(hours=-5))

TITULOS = [
    ("marca_temporal", "Marca temporal"),
    ("marca_temporal", "Timestamp"),
    ("autorizacion", "Autorizacion de tratamiento de datos"),
    ("tipo_registro", "Dentro de Monte Verde, ¿Actualmente usted es?"),
    ("nombres", "Escriba sus nombres"),
    ("apellidos", "Escriba sus apellidos"),
    ("tipo_documento", "Tipo de documento de identidad"),
    ("documento", "Ingrese su número de Documento de Identidad."),
    ("fecha_nacimiento", "Registre su fecha de nacimiento."),
    ("telefono", "Ingrese su número de contacto personal"),
    ("correo", "Ingrese su correo electrónico."),
    ("direccion", "Ingrese su dirección de residencia."),
    ("barrio", "Indique el barrio en donde vive."),
    ("localidad", "Indique la localidad donde vive."),
    ("grado", "Grado que cursa actualmente."),
    ("colegio", "Seleccione el Colegio del que proviene."),
    ("foto", "Anexar una foto tipo documento 3x4"),
    ("boletin", "Anexe el último boletín entregado por el Colegio."),
    ("padre_nombre", "Registre Nombre completo del Padre."),
    ("padre_documento", "Número de documento del Padre."),
    ("padre_telefono", "Número de contacto del Padre."),
    ("padre_ocupacion", "Ocupación del Padre."),
    ("padre_correo", "Correo electrónico del Padre."),
    ("madre_nombre", "Registre Nombre completo de la Madre."),
    ("madre_documento", "Número de documento de la Madre."),
    ("madre_telefono", "Número de contacto de la Madre."),
    ("madre_ocupacion", "Ocupación de la Madre."),
    ("madre_correo", "Correo electrónico de la Madre."),
    ("estado_civil", "Estado civil de los padres"),
    ("religion", "¿Qué Religión profesa?"),
    ("sacramentos", "Si es Católico, ¿Qué sacramentos has recibido?"),
    ("preceptor", "¿Cuál es el nombre de su preceptor?"),
]

# Se prueba primero el titulo mas largo, para evitar choques entre prefijos
_PREFIJOS = sorted(
    ((clave, normalizar(titulo)) for clave, titulo in TITULOS),
    key=lambda par: len(par[1]),
    reverse=True,
)

_TIPOS_DOCUMENTO = {
    "tarjeta de identidad": "TI", "ti": "TI",
    "cedula de ciudadania": "CC", "cc": "CC",
    "registro civil": "RC", "rc": "RC",
    "cedula de extranjeria": "CE", "ce": "CE",
}


def texto(valor) -> str | None:
    if valor is None:
        return None
    limpio = str(valor).strip()
    return limpio or None


def mapear_fila(fila: dict) -> dict:
    datos: dict = {}
    for encabezado, valor in fila.items():
        enc = re.sub(r"^\d+\s+", "", normalizar(encabezado))
        for clave, prefijo in _PREFIJOS:
            if enc.startswith(prefijo):
                datos.setdefault(clave, texto(valor))
                break
    return datos


def es_si(valor) -> bool:
    return normalizar(valor).startswith(("si", "acepto", "autorizo"))


def parsear_fecha(valor) -> date | None:
    t = texto(valor)
    if not t:
        return None
    t = t.split()[0]
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(t, formato).date()
        except ValueError:
            continue
    return None


def fecha_marca(datos: dict) -> datetime | None:
    t = datos.get("marca_temporal")
    if not t:
        return None
    for formato in ("%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(t, formato).replace(tzinfo=ZONA)
        except ValueError:
            continue
    return None


def identificador(datos: dict, fila: dict) -> str:
    base = f"{datos.get('marca_temporal') or ''}|{solo_digitos(datos.get('documento'))}"
    if base == "|":
        base = json.dumps(fila, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:40]


def tipo_documento(valor) -> str:
    return _TIPOS_DOCUMENTO.get(normalizar(valor), "OTRO")


def localidad(valor) -> Localidad | None:
    n = normalizar(valor)
    for loc in Localidad:
        if normalizar(loc.value.replace("_", " ")) == n:
            return loc
    return None


def sacramentos(valor) -> tuple[bool | None, bool | None]:
    n = normalizar(valor)
    if not n:
        return None, None
    if n.startswith("ninguno"):
        return False, False
    return "bautismo" in n, "primera comunion" in n


def correo_valido(valor: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor) is not None
