from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import InscripcionFormulario as Inscripcion


def existe(db: Session, id_respuesta: str) -> bool:
    return (
        db.scalar(select(Inscripcion.id).where(Inscripcion.id_respuesta == id_respuesta))
        is not None
    )


def guardar(
    db: Session, id_respuesta: str, fecha: datetime | None, datos: dict
) -> Inscripcion:
    registro = Inscripcion(
        id_respuesta=id_respuesta,
        fecha_respuesta=fecha,
        datos=datos,
        estado_procesamiento="pendiente",
    )
    db.add(registro)
    db.flush()
    return registro


def listar(db: Session, estado: str | None, page: int, size: int):
    filtros = [Inscripcion.estado_procesamiento == estado] if estado else []
    total = db.scalar(select(func.count()).select_from(Inscripcion).where(*filtros))
    items = db.scalars(
        select(Inscripcion)
        .where(*filtros)
        .order_by(Inscripcion.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total or 0, list(items)


def obtener(db: Session, id_inscripcion: int) -> Inscripcion | None:
    return db.get(Inscripcion, id_inscripcion)
