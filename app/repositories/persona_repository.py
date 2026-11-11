from datetime import date

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    AcudientePersona,
    EstadoPersonaHistorial,
    Persona,
    ProgramaPersona,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.models.enums import EstadoProceso


def _estado_vigente():
    """Estado actual = ultimo registro del historial."""
    return (
        select(EstadoPersonaHistorial.estado)
        .where(
            EstadoPersonaHistorial.numero_identificacion
            == Persona.numero_identificacion
        )
        .order_by(
            EstadoPersonaHistorial.fecha_estado.desc(),
            EstadoPersonaHistorial.id_estado.desc(),
        )
        .limit(1)
        .correlate(Persona)
        .scalar_subquery()
    )


def _filtros(q, estado, id_programa):
    filtros = []
    if q:
        patron = f"%{q}%"
        filtros.append(
            or_(
                Usuario.numero_identificacion.ilike(patron),
                Usuario.nombres.ilike(patron),
                Usuario.apellidos.ilike(patron),
            )
        )
    if id_programa:
        filtros.append(
            exists().where(
                ProgramaPersona.id_programa == id_programa,
                ProgramaPersona.numero_identificacion_persona
                == Persona.numero_identificacion,
            )
        )
    if estado:
        filtros.append(_estado_vigente() == estado)
    return filtros


def listar(db: Session, q, estado, id_programa, page: int, size: int):
    filtros = _filtros(q, estado, id_programa)
    union = Persona.numero_identificacion == Usuario.numero_identificacion
    total = db.scalar(
        select(func.count()).select_from(Persona).join(Usuario, union).where(*filtros)
    )
    consulta = (
        select(Persona, Usuario, _estado_vigente().label("estado"))
        .join(Usuario, union)
        .where(*filtros)
        .order_by(Usuario.apellidos, Usuario.nombres)
        .offset((page - 1) * size)
        .limit(size)
    )
    return total or 0, db.execute(consulta).all()


def obtener(db: Session, documento: str):
    consulta = (
        select(Persona, Usuario, _estado_vigente().label("estado"))
        .join(Usuario, Persona.numero_identificacion == Usuario.numero_identificacion)
        .where(Persona.numero_identificacion == documento)
    )
    return db.execute(consulta).first()


def obtener_persona(db: Session, documento: str) -> Persona | None:
    return db.get(Persona, documento)


def obtener_usuario(db: Session, documento: str) -> Usuario | None:
    return db.get(Usuario, documento)


def estado_vigente_de(db: Session, documento: str):
    return db.scalar(
        select(EstadoPersonaHistorial.estado)
        .where(EstadoPersonaHistorial.numero_identificacion == documento)
        .order_by(
            EstadoPersonaHistorial.fecha_estado.desc(),
            EstadoPersonaHistorial.id_estado.desc(),
        )
        .limit(1)
    )


def historial(db: Session, documento: str):
    return list(
        db.scalars(
            select(EstadoPersonaHistorial)
            .where(EstadoPersonaHistorial.numero_identificacion == documento)
            .order_by(
                EstadoPersonaHistorial.fecha_estado.desc(),
                EstadoPersonaHistorial.id_estado.desc(),
            )
        )
    )


def agregar_estado(
    db: Session, documento: str, estado: EstadoProceso, observaciones: str | None
) -> None:
    db.add(
        EstadoPersonaHistorial(
            numero_identificacion=documento,
            estado=estado,
            activo=True,
            fecha_estado=date.today(),
            observaciones=observaciones,
        )
    )
    db.flush()


def tiene_acudiente(db: Session, documento: str) -> bool:
    return bool(
        db.scalar(
            select(
                exists().where(
                    AcudientePersona.numero_identificacion_persona == documento
                )
            )
        )
    )


def crear(db: Session, datos_usuario: dict, datos_persona: dict) -> None:
    documento = datos_usuario["numero_identificacion"]
    db.add(Usuario(**datos_usuario, password_hash=None, estado="inactivo"))
    db.flush()
    db.add(Persona(numero_identificacion=documento, **datos_persona))
    db.flush()
    agregar_estado(db, documento, EstadoProceso.aspirante, "Registro inicial")
    rol = db.scalar(select(Rol).filter_by(nombre="Estudiante"))
    if rol is not None:
        db.add(UsuarioRol(numero_identificacion=documento, id_rol=rol.id_rol))
    db.flush()
