from sqlalchemy.orm import Session

from app.repositories import catalogo_repository as repo


def todos(db: Session) -> dict:
    return repo.listar_catalogos(db)