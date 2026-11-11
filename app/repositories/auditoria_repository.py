from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Auditoria


def insertar(db: Session, **datos) -> Auditoria:
    registro = Auditoria(**datos)
    db.add(registro)
    db.flush()
    return registro


def consultar(
    db: Session,
    usuario: str | None,
    accion: str | None,
    resultado: str | None,
    recurso: str | None,
    desde: datetime | None,
    hasta: datetime | None,
    page: int,
    size: int,
):
    """Solo lectura: la bitacora nunca se modifica ni se borra."""
    filtros = []
    if usuario:
        filtros.append(Auditoria.numero_identificacion == usuario)
    if accion:
        filtros.append(Auditoria.accion == accion)
    if resultado:
        filtros.append(Auditoria.resultado == resultado)
    if recurso:
        filtros.append(Auditoria.recurso == recurso)
    if desde:
        filtros.append(Auditoria.fecha >= desde)
    if hasta:
        filtros.append(Auditoria.fecha < hasta)
    total = db.scalar(select(func.count()).select_from(Auditoria).where(*filtros))
    filas = db.scalars(
        select(Auditoria)
        .where(*filtros)
        .order_by(Auditoria.id_auditoria.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return total or 0, list(filas)
