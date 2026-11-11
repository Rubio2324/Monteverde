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
