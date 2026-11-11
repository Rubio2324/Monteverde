from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.repositories import auditoria_repository


def registrar(
    db: Session,
    accion: str,
    resultado: str,
    numero_identificacion: str | None = None,
    recurso: str | None = None,
    ip: str | None = None,
    detalle: str | None = None,
) -> None:
    """Registra un evento sensible en la bitacora (solo insercion)."""
    auditoria_repository.insertar(
        db,
        accion=accion,
        resultado=resultado,
        numero_identificacion=numero_identificacion,
        recurso=recurso,
        ip=ip,
        detalle=detalle,
    )


def consultar(
    db: Session,
    admin_documento: str,
    usuario: str | None,
    accion: str | None,
    resultado: str | None,
    recurso: str | None,
    desde: date | None,
    hasta: date | None,
    page: int,
    size: int,
    ip: str | None,
) -> dict:
    if hasta is not None:
        hasta = hasta + timedelta(days=1)  # incluye todo el dia final
    total, items = auditoria_repository.consultar(
        db, usuario, accion, resultado, recurso, desde, hasta, page, size
    )
    registrar(db, "CONSULTAR_AUDITORIA", "ok", admin_documento, ip=ip)
    db.commit()
    return {"total": total, "page": page, "size": size, "items": items}
