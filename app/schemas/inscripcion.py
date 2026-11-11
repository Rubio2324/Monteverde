from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InscripcionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_respuesta: str
    fecha_respuesta: datetime | None
    estado_procesamiento: str
    error: str | None
    numero_identificacion: str | None
    fecha_importacion: datetime


class InscripcionDetalle(InscripcionItem):
    datos: dict


class PaginaInscripciones(BaseModel):
    total: int
    page: int
    size: int
    items: list[InscripcionItem]


class ResultadoImportacion(BaseModel):
    leidas: int
    nuevas: int
    procesadas: int
    revision: int
    error: int
    omitidas: int
