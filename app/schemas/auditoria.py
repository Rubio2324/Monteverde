from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_auditoria: int
    fecha: datetime
    numero_identificacion: str | None
    accion: str
    recurso: str | None
    resultado: str
    ip: str | None
    detalle: str | None


class PaginaAuditoria(BaseModel):
    total: int
    page: int
    size: int
    items: list[AuditoriaItem]
