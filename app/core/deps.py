from collections.abc import Callable, Iterator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models import Usuario
from app.repositories import usuario_repository

_bearer = HTTPBearer(auto_error=False)


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    no_autenticado = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "No autenticado", {"WWW-Authenticate": "Bearer"}
    )
    if credenciales is None:
        raise no_autenticado
    try:
        payload = decode_token(credenciales.credentials)
    except jwt.PyJWTError:
        raise no_autenticado
    usuario = usuario_repository.buscar_por_documento(db, payload.get("sub", ""))
    # Una cuenta desactivada se rechaza en la siguiente peticion
    if usuario is None or usuario.estado != "activo":
        raise no_autenticado
    return usuario


def requiere_roles(*roles_permitidos: str) -> Callable[..., Usuario]:
    """Dependencia RBAC: si la ruta no declara roles, no pasa nadie."""

    def dependencia(
        usuario: Usuario = Depends(usuario_actual),
        db: Session = Depends(get_db),
    ) -> Usuario:
        roles = usuario_repository.roles_de(db, usuario.numero_identificacion)
        if not set(roles) & set(roles_permitidos):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin permiso")
        return usuario

    return dependencia
