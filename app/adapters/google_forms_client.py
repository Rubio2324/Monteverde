import json
import time
from pathlib import Path
from typing import Protocol
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.core.errors import FuenteNoDisponible


class FuenteRespuestas(Protocol):
    def leer(self) -> list[dict]: ...


class ArchivoJsonClient:
    """Fuente de prueba: lee las respuestas de un archivo JSON local."""

    def __init__(self, ruta: str):
        self.ruta = Path(ruta)

    def leer(self) -> list[dict]:
        if not self.ruta.exists():
            raise FuenteNoDisponible("No se encontro el archivo de inscripciones")
        return json.loads(self.ruta.read_text(encoding="utf-8"))


class GoogleFormsClient:
    """Lee la hoja de respuestas con una cuenta de servicio de SOLO LECTURA."""

    ALCANCE = "https://www.googleapis.com/auth/spreadsheets.readonly"

    def leer(self) -> list[dict]:
        if not settings.google_sheet_id:
            raise FuenteNoDisponible("Falta configurar GOOGLE_SHEET_ID")
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
        except ImportError:
            raise FuenteNoDisponible("Falta instalar google-auth y requests")
        try:
            cred = service_account.Credentials.from_service_account_file(
                settings.google_credenciales, scopes=[self.ALCANCE]
            )
            cred.refresh(Request())
        except Exception:
            raise FuenteNoDisponible("No se pudo autenticar con Google")
        url = (
            "https://sheets.googleapis.com/v4/spreadsheets/"
            f"{settings.google_sheet_id}/values/{quote(settings.google_hoja_rango)}"
        )
        for intento in range(3):
            try:
                r = httpx.get(
                    url, headers={"Authorization": f"Bearer {cred.token}"}, timeout=20
                )
                r.raise_for_status()
                break
            except httpx.HTTPError:
                if intento == 2:
                    raise FuenteNoDisponible("Google no responde; se reintentara")
                time.sleep(2**intento)
        valores = r.json().get("values", [])
        if not valores:
            return []
        encabezados = valores[0]
        return [
            dict(zip(encabezados, fila + [""] * (len(encabezados) - len(fila))))
            for fila in valores[1:]
        ]


def obtener_fuente() -> FuenteRespuestas:
    if settings.fuente_inscripciones == "google":
        return GoogleFormsClient()
    return ArchivoJsonClient(settings.archivo_inscripciones)
