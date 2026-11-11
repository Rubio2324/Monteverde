from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.models import Usuario
from app.schemas.inscripcion import (
    InscripcionDetalle,
    InscripcionItem,
    PaginaInscripciones,
    ResultadoImportacion,
)
from app.services import importador_service as servicio

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])
SoloAdmin = Depends(requiere_roles("Administrador"))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/importar", response_model=ResultadoImportacion)
def importar(request: Request, admin: Usuario = SoloAdmin, db: Session = Depends(get_db)):
    return servicio.importar(db, admin.numero_identificacion, _ip(request))


@router.get("", response_model=PaginaInscripciones)
def listar(
    request: Request,
    estado: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.listar(db, admin.numero_identificacion, estado, page, size, _ip(request))


@router.get("/{id_inscripcion}", response_model=InscripcionDetalle)
def ver(
    id_inscripcion: int,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.detalle(db, admin.numero_identificacion, id_inscripcion, _ip(request))


@router.patch("/{id_inscripcion}/descartar", response_model=InscripcionItem)
def descartar(
    id_inscripcion: int,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.descartar(db, admin.numero_identificacion, id_inscripcion, _ip(request))
