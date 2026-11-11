from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.repositories import usuario_repository
from app.services import auditoria_service


class CredencialesInvalidas(Exception):
    """Mensaje generico: no revela si fallo el usuario o la clave."""


def iniciar_sesion(
    db: Session, documento: str, password: str, ip: str | None
) -> tuple[str, list[str]]:
    ahora = datetime.now(timezone.utc)
    usuario = usuario_repository.buscar_por_documento(db, documento)

    if usuario is None:
        auditoria_service.registrar(
            db, "LOGIN", "fallo", recurso=documento, ip=ip, detalle="cuenta inexistente"
        )
        db.commit()
        raise CredencialesInvalidas()

    if usuario.bloqueado_hasta is not None and usuario.bloqueado_hasta > ahora:
        auditoria_service.registrar(
            db, "LOGIN", "bloqueada", usuario.numero_identificacion, ip=ip
        )
        db.commit()
        raise CredencialesInvalidas()

    valida = (
        usuario.estado == "activo"
        and usuario.password_hash is not None
        and verify_password(password, usuario.password_hash)
    )
    if not valida:
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= settings.max_intentos_login:
            usuario.bloqueado_hasta = ahora + timedelta(minutes=settings.bloqueo_minutos)
            usuario.intentos_fallidos = 0
        auditoria_service.registrar(
            db, "LOGIN", "fallo", usuario.numero_identificacion, ip=ip
        )
        db.commit()
        raise CredencialesInvalidas()

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    roles = usuario_repository.roles_de(db, usuario.numero_identificacion)
    token = create_access_token(usuario.numero_identificacion, roles)
    auditoria_service.registrar(db, "LOGIN", "ok", usuario.numero_identificacion, ip=ip)
    db.commit()
    return token, roles
