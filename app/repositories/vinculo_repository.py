from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Acudiente,
    AcudientePersona,
    PreceptorPersona,
    ProgramaPersona,
    Rol,
    Usuario,
    UsuarioRol,
)


def _asignar_rol(db: Session, documento: str, nombre_rol: str) -> None:
    rol = db.scalar(select(Rol).filter_by(nombre=nombre_rol))
    if rol is not None and db.get(UsuarioRol, (documento, rol.id_rol)) is None:
        db.add(UsuarioRol(numero_identificacion=documento, id_rol=rol.id_rol))
        db.flush()


def crear_o_reutilizar_acudiente(
    db: Session, datos_usuario: dict, datos_acudiente: dict
) -> None:
    """Si el acudiente ya existe (por ejemplo, otro hijo), se reutiliza."""
    documento = datos_usuario["numero_identificacion"]
    if db.get(Usuario, documento) is None:
        db.add(Usuario(**datos_usuario, password_hash=None, estado="inactivo"))
        db.flush()
    if db.get(Acudiente, documento) is None:
        db.add(Acudiente(numero_identificacion=documento, **datos_acudiente))
        db.flush()
    _asignar_rol(db, documento, "Acudiente")


def vincular(db: Session, id_acudiente: str, documento_persona: str, vinculo: str) -> None:
    if db.get(AcudientePersona, (id_acudiente, documento_persona)) is None:
        db.add(
            AcudientePersona(
                id_acudiente=id_acudiente,
                numero_identificacion_persona=documento_persona,
                vinculo=vinculo,
            )
        )
        db.flush()


def asignar_preceptor(db: Session, documento_persona: str, id_preceptor: str) -> None:
    db.add(
        PreceptorPersona(
            numero_identificacion_persona=documento_persona,
            id_preceptor=id_preceptor,
            fecha_inicio=date.today(),
        )
    )
    db.flush()


def inscribir_programa(db: Session, id_programa: int, documento_persona: str) -> None:
    db.add(
        ProgramaPersona(
            id_programa=id_programa, numero_identificacion_persona=documento_persona
        )
    )
    db.flush()
