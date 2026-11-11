from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.models import Usuario
from app.schemas.auditoria import PaginaAuditoria
from app.services import auditoria_service as servicio

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])
SoloAdmin = Depends(requiere_roles("Administrador"))


@router.get("", response_model=PaginaAuditoria)
def consultar(
    request: Request,
    usuario: str | None = Query(default=None, max_length=20),
    accion: str | None = Query(default=None, max_length=50),
    resultado: str | None = Query(default=None, max_length=20),
    recurso: str | None = Query(default=None, max_length=200),
    desde: date | None = None,
    hasta: date | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    return servicio.consultar(
        db, admin.numero_identificacion, usuario, accion, resultado, recurso,
        desde, hasta, page, size, ip,
    )
