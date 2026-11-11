from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Acudiente, AcudientePersona, Usuario


def listar(db: Session, documento_persona: str) -> list[dict]:
    stmt = (
        select(AcudientePersona.vinculo, Usuario, Acudiente)
        .join(Usuario, Usuario.numero_identificacion == AcudientePersona.id_acudiente)
        .join(
            Acudiente,
            Acudiente.numero_identificacion == AcudientePersona.id_acudiente,
        )
        .where(AcudientePersona.numero_identificacion_persona == documento_persona)
        .order_by(Usuario.apellidos, Usuario.nombres)
    )
    return [
        {
            "numero_identificacion": u.numero_identificacion,
            "tipo_identificacion": u.tipo_identificacion,
            "nombres": u.nombres,
            "apellidos": u.apellidos,
            "vinculo": vinculo,
            "telefono": a.telefono,
            "correo": a.correo,
            "ocupacion": a.ocupacion,
        }
        for vinculo, u, a in db.execute(stmt)
    ]


def existe_vinculo(db: Session, id_acudiente: str, documento_persona: str) -> bool:
    return db.get(AcudientePersona, (id_acudiente, documento_persona)) is not None


def cantidad(db: Session, documento_persona: str) -> int:
    return len(
        list(
            db.scalars(
                select(AcudientePersona.id_acudiente).where(
                    AcudientePersona.numero_identificacion_persona == documento_persona
                )
            )
        )
    )


def eliminar(db: Session, id_acudiente: str, documento_persona: str) -> None:
    db.execute(
        delete(AcudientePersona).where(
            AcudientePersona.id_acudiente == id_acudiente,
            AcudientePersona.numero_identificacion_persona == documento_persona,
        )
    )
    db.flush()