from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.models import Usuario
from app.schemas.vinculo import AcudienteCreate, AcudienteOut
from app.services import vinculo_service as servicio

router = APIRouter(prefix="/beneficiarios", tags=["Acudientes"])
SoloAdmin = Depends(requiere_roles("Administrador"))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("/{documento}/acudientes", response_model=list[AcudienteOut])
def listar(
    documento: str,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.listar(db, admin, documento, _ip(request))


@router.post(
    "/{documento}/acudientes",
    response_model=list[AcudienteOut],
    status_code=status.HTTP_201_CREATED,
)
def vincular(
    documento: str,
    datos: AcudienteCreate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.vincular(db, admin, documento, datos, _ip(request))


@router.delete(
    "/{documento}/acudientes/{id_acudiente}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desvincular(
    documento: str,
    id_acudiente: str,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    servicio.desvincular(db, admin, documento, id_acudiente, _ip(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)