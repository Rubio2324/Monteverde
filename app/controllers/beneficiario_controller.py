from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Usuario
from app.models.enums import EstadoProceso
from app.schemas.beneficiario import (
    BeneficiarioCreate,
    BeneficiarioOut,
    BeneficiarioUpdate,
    CambioEstado,
    HistorialItem,
    Pagina,
)
from app.services import beneficiario_service as servicio

router = APIRouter(prefix="/beneficiarios", tags=["Beneficiarios"])
SoloAdmin = Depends(requiere_roles("Administrador"))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _ejecutar(funcion, *args):
    try:
        return funcion(*args)
    except NoEncontrado as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except Conflicto as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except ReglaNegocio as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))


@router.get("", response_model=Pagina)
def listar(
    request: Request,
    q: str | None = Query(default=None, max_length=100),
    estado: EstadoProceso | None = None,
    id_programa: int | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(
        servicio.listar, db, admin, q, estado, id_programa, page, size, _ip(request)
    )


@router.post("", response_model=BeneficiarioOut, status_code=status.HTTP_201_CREATED)
def crear(
    datos: BeneficiarioCreate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(servicio.registrar, db, admin, datos, _ip(request))


@router.get("/{documento}", response_model=BeneficiarioOut)
def ficha(
    documento: str,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(servicio.consultar, db, admin, documento, _ip(request))


@router.patch("/{documento}", response_model=BeneficiarioOut)
def actualizar(
    documento: str,
    datos: BeneficiarioUpdate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(servicio.actualizar, db, admin, documento, datos, _ip(request))


@router.patch("/{documento}/estado", response_model=BeneficiarioOut)
def cambiar_estado(
    documento: str,
    datos: CambioEstado,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(
        servicio.cambiar_estado, db, admin, documento, datos.estado,
        datos.observaciones, _ip(request),
    )


@router.get("/{documento}/historial", response_model=list[HistorialItem])
def historial(
    documento: str,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return _ejecutar(servicio.historial, db, admin, documento, _ip(request))
