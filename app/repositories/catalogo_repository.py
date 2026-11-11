from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.textos import normalizar
from app.models import Barrio, Institucion, Profesor, Programa, Religion, Usuario
from app.models.enums import Localidad


def _por_nombre(db: Session, modelo, texto):
    n = normalizar(texto)
    if not n:
        return None
    for obj in db.scalars(select(modelo)):
        if normalizar(obj.nombre) == n:
            return obj
    return None


def buscar_barrio(db: Session, texto, localidad: Localidad | None) -> Barrio | None:
    n = normalizar(texto)
    if not n:
        return None
    candidatos = [b for b in db.scalars(select(Barrio)) if normalizar(b.nombre) == n]
    if localidad is not None:
        candidatos = [b for b in candidatos if b.localidad in (localidad, None)]
    return candidatos[0] if len(candidatos) == 1 else None


def buscar_institucion(db: Session, texto) -> Institucion | None:
    return _por_nombre(db, Institucion, texto)


def buscar_religion(db: Session, texto) -> Religion | None:
    return _por_nombre(db, Religion, texto)


def programa_por_nombre(db: Session, texto) -> Programa | None:
    return _por_nombre(db, Programa, texto)


def buscar_preceptor(db: Session, texto) -> Profesor | None:
    n = normalizar(texto)
    if not n or n.startswith("ninguno"):
        return None
    filas = db.execute(
        select(Profesor, Usuario)
        .join(Usuario, Usuario.numero_identificacion == Profesor.numero_identificacion)
        .where(Profesor.es_preceptor.is_(True), Profesor.estado == "activo")
    ).all()
    for profesor, usuario in filas:
        if normalizar(f"{usuario.nombres} {usuario.apellidos}") == n:
            return profesor
    return None


def listar_catalogos(db: Session) -> dict:
    from app.models import Eps

    def pares(modelo, id_columna):
        return [
            {"id": getattr(o, id_columna), "nombre": o.nombre}
            for o in db.scalars(select(modelo).order_by(modelo.nombre))
        ]

    barrios = [
        {
            "id": b.id_barrio,
            "nombre": b.nombre,
            "localidad": b.localidad.value if b.localidad else None,
        }
        for b in db.scalars(select(Barrio).order_by(Barrio.nombre))
    ]
    return {
        "barrios": barrios,
        "eps": pares(Eps, "id_eps"),
        "religiones": pares(Religion, "id_religion"),
        "instituciones": pares(Institucion, "id_institucion"),
        "programas": pares(Programa, "id_programa"),
    }