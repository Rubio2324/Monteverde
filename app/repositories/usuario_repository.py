from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Rol, Usuario, UsuarioRol


def buscar_por_documento(db: Session, documento: str) -> Usuario | None:
    return db.get(Usuario, documento)


def roles_de(db: Session, documento: str) -> list[str]:
    stmt = (
        select(Rol.nombre)
        .join(UsuarioRol, UsuarioRol.id_rol == Rol.id_rol)
        .where(UsuarioRol.numero_identificacion == documento)
    )
    return list(db.scalars(stmt))
