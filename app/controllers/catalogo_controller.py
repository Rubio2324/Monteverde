from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.models import Usuario
from app.schemas.catalogo import CatalogosOut
from app.services import catalogo_service as servicio

router = APIRouter(prefix="/catalogos", tags=["Catalogos"])


@router.get("", response_model=CatalogosOut)
def catalogos(
    usuario: Usuario = Depends(requiere_roles("Administrador")),
    db: Session = Depends(get_db),
):
    return servicio.todos(db)