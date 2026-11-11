from sqlalchemy.orm import Session

from app.models import Auditoria


def insertar(db: Session, **datos) -> Auditoria:
    registro = Auditoria(**datos)
    db.add(registro)
    db.flush()
    return registro
