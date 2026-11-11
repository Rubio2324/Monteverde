from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, requiere_roles
from app.models import Usuario
from app.schemas.academico import (
    CursoCreate,
    CursoOut,
    CursoUpdate,
    MatriculaCreate,
    MatriculaOut,
    PaginaCursos,
    ProfesorOut,
    ProgramaOut,
)
from app.services import academico_service as servicio

router = APIRouter(tags=["Academico"])
SoloAdmin = Depends(requiere_roles("Administrador"))


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("/programas", response_model=list[ProgramaOut])
def programas(admin: Usuario = SoloAdmin, db: Session = Depends(get_db)):
    return servicio.listar_programas(db)


@router.get("/profesores", response_model=list[ProfesorOut])
def profesores(admin: Usuario = SoloAdmin, db: Session = Depends(get_db)):
    return servicio.listar_profesores(db)


@router.get("/cursos", response_model=PaginaCursos)
def listar_cursos(
    id_programa: int | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.listar_cursos(db, id_programa, page, size)


@router.post("/cursos", response_model=CursoOut, status_code=status.HTTP_201_CREATED)
def crear_curso(
    datos: CursoCreate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.crear_curso(db, admin, datos, _ip(request))


@router.get("/cursos/{id_curso}", response_model=CursoOut)
def ver_curso(id_curso: int, admin: Usuario = SoloAdmin, db: Session = Depends(get_db)):
    return servicio.consultar_curso(db, id_curso)


@router.patch("/cursos/{id_curso}", response_model=CursoOut)
def actualizar_curso(
    id_curso: int,
    datos: CursoUpdate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.actualizar_curso(db, admin, id_curso, datos, _ip(request))


@router.get("/cursos/{id_curso}/matriculas", response_model=list[MatriculaOut])
def matriculas_del_curso(
    id_curso: int,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.matriculas_de_curso(db, admin, id_curso, _ip(request))


@router.post(
    "/cursos/{id_curso}/matriculas",
    response_model=MatriculaOut,
    status_code=status.HTTP_201_CREATED,
)
def matricular(
    id_curso: int,
    datos: MatriculaCreate,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.matricular(
        db, admin, id_curso, datos.numero_identificacion_persona, _ip(request)
    )


@router.get("/beneficiarios/{documento}/cursos", response_model=list[MatriculaOut])
def cursos_del_beneficiario(
    documento: str,
    request: Request,
    admin: Usuario = SoloAdmin,
    db: Session = Depends(get_db),
):
    return servicio.cursos_de_beneficiario(db, admin, documento, _ip(request))
