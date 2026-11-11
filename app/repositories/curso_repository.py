from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Curso, CursoPersona, Profesor, Programa, Usuario


def listar_programas(db: Session):
    return list(db.scalars(select(Programa).order_by(Programa.nombre)))


def listar_profesores(db: Session):
    consulta = (
        select(Profesor, Usuario)
        .join(Usuario, Profesor.numero_identificacion == Usuario.numero_identificacion)
        .order_by(Usuario.apellidos, Usuario.nombres)
    )
    return db.execute(consulta).all()


def obtener_programa(db: Session, id_programa: int) -> Programa | None:
    return db.get(Programa, id_programa)


def obtener_profesor(db: Session, documento: str) -> Profesor | None:
    return db.get(Profesor, documento)


def obtener_curso(db: Session, id_curso: int) -> Curso | None:
    return db.get(Curso, id_curso)


def _consulta_cursos():
    matriculados = (
        select(func.count())
        .select_from(CursoPersona)
        .where(CursoPersona.id_curso == Curso.id_curso)
        .correlate(Curso)
        .scalar_subquery()
    )
    return (
        select(Curso, Programa.nombre, Usuario, matriculados.label("matriculados"))
        .join(Programa, Programa.id_programa == Curso.id_programa)
        .join(
            Usuario,
            Usuario.numero_identificacion == Curso.numero_identificacion_profesor,
        )
    )


def listar_cursos(db: Session, id_programa: int | None, page: int, size: int):
    filtros = []
    if id_programa:
        filtros.append(Curso.id_programa == id_programa)
    total = db.scalar(select(func.count()).select_from(Curso).where(*filtros))
    filas = db.execute(
        _consulta_cursos()
        .where(*filtros)
        .order_by(Curso.nombre)
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total or 0, filas


def curso_detalle(db: Session, id_curso: int):
    return db.execute(_consulta_cursos().where(Curso.id_curso == id_curso)).first()


def crear_curso(db: Session, datos: dict) -> Curso:
    curso = Curso(**datos)
    db.add(curso)
    db.flush()
    return curso


def matricula_existente(db: Session, id_curso: int, documento: str):
    return db.scalar(
        select(CursoPersona).where(
            CursoPersona.id_curso == id_curso,
            CursoPersona.numero_identificacion_persona == documento,
        )
    )


def crear_matricula(db: Session, id_curso: int, documento: str) -> CursoPersona:
    matricula = CursoPersona(id_curso=id_curso, numero_identificacion_persona=documento)
    db.add(matricula)
    db.flush()
    return matricula


def _consulta_matriculas():
    return (
        select(CursoPersona, Usuario, Curso.nombre)
        .join(
            Usuario,
            Usuario.numero_identificacion == CursoPersona.numero_identificacion_persona,
        )
        .join(Curso, Curso.id_curso == CursoPersona.id_curso)
    )


def matricula_detalle(db: Session, id_matricula: int):
    return db.execute(
        _consulta_matriculas().where(CursoPersona.id_matricula == id_matricula)
    ).first()


def matriculas_de_curso(db: Session, id_curso: int):
    return db.execute(
        _consulta_matriculas()
        .where(CursoPersona.id_curso == id_curso)
        .order_by(Usuario.apellidos, Usuario.nombres)
    ).all()


def matriculas_de_persona(db: Session, documento: str):
    return db.execute(
        _consulta_matriculas()
        .where(CursoPersona.numero_identificacion_persona == documento)
        .order_by(Curso.nombre)
    ).all()
