from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, usuario_actual
from app.models import Usuario
from app.repositories import usuario_repository
from app.schemas.auth import LoginIn, TokenOut, UsuarioOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    try:
        token, roles = auth_service.iniciar_sesion(
            db, datos.numero_identificacion, datos.password, ip
        )
    except auth_service.CredencialesInvalidas:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales invalidas")
    return TokenOut(access_token=token, roles=roles)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    roles = usuario_repository.roles_de(db, usuario.numero_identificacion)
    return UsuarioOut(
        numero_identificacion=usuario.numero_identificacion,
        tipo_identificacion=usuario.tipo_identificacion,
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        roles=roles,
    )
