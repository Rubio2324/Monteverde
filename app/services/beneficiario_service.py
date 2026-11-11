from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Persona, Usuario
from app.models.enums import EstadoProceso
from app.repositories import persona_repository as repo
from app.schemas.beneficiario import BeneficiarioCreate, BeneficiarioUpdate
from app.services import auditoria_service as bitacora

E = EstadoProceso

TRANSICIONES = {
    E.aspirante: {E.admitido, E.no_admitido},
    E.admitido: {E.matriculado, E.retirado},
    E.no_admitido: {E.aspirante},
    E.matriculado: {E.egresado, E.retirado},
    E.egresado: set(),
    E.retirado: {E.admitido},
}

CAMPOS_USUARIO = {"tipo_identificacion", "nombres", "apellidos"}
NO_NULOS = CAMPOS_USUARIO | {"autoriza_tratamiento_datos"}
CAMPOS_PERSONA = [
    "fecha_nacimiento", "direccion", "id_barrio", "correo", "telefono",
    "estrato_socioeconomico", "id_eps", "id_religion", "bautizado",
    "primera_comunion", "id_institucion", "grado", "subgrupo",
    "observaciones", "foto_url", "boletin_url",
    "autoriza_tratamiento_datos", "activo",
]


def _es_menor(nacimiento: date) -> bool:
    hoy = date.today()
    edad = hoy.year - nacimiento.year - (
        (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
    )
    return edad < 18


def _ficha(persona: Persona, usuario: Usuario, estado) -> dict:
    ficha = {
        "numero_identificacion": usuario.numero_identificacion,
        "tipo_identificacion": usuario.tipo_identificacion,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "estado": estado,
    }
    for campo in CAMPOS_PERSONA:
        ficha[campo] = getattr(persona, campo)
    return ficha


def _ficha_de(db: Session, documento: str) -> dict:
    fila = repo.obtener(db, documento)
    if fila is None:
        raise NoEncontrado("Beneficiario no encontrado")
    return _ficha(*fila)


def _guardar(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ReglaNegocio(
            "Datos invalidos: revise el documento y las referencias "
            "(barrio, EPS, religion, institucion)"
        )


def listar(db: Session, admin: Usuario, q, estado, id_programa, page, size, ip):
    total, filas = repo.listar(db, q, estado, id_programa, page, size)
    items = [
        {
            "numero_identificacion": u.numero_identificacion,
            "tipo_identificacion": u.tipo_identificacion,
            "nombres": u.nombres,
            "apellidos": u.apellidos,
            "grado": p.grado,
            "estado": e,
        }
        for p, u, e in filas
    ]
    bitacora.registrar(
        db, "LISTAR_BENEFICIARIOS", "ok", admin.numero_identificacion,
        ip=ip, detalle=f"pagina {page}",
    )
    db.commit()
    return {"total": total, "page": page, "size": size, "items": items}


def consultar(db: Session, admin: Usuario, documento: str, ip):
    ficha = _ficha_de(db, documento)
    bitacora.registrar(
        db, "CONSULTAR_BENEFICIARIO", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip,
    )
    db.commit()
    return ficha


def registrar(db: Session, admin: Usuario, datos: BeneficiarioCreate, ip):
    if repo.obtener_usuario(db, datos.numero_identificacion) is not None:
        raise Conflicto("Ya existe una persona con ese documento")
    if datos.fecha_nacimiento > date.today():
        raise ReglaNegocio("La fecha de nacimiento no puede ser futura")
    if _es_menor(datos.fecha_nacimiento) and not datos.autoriza_tratamiento_datos:
        raise ReglaNegocio(
            "Para un menor se exige la autorizacion de tratamiento de datos "
            "del representante legal"
        )
    campos = datos.model_dump()
    datos_usuario = {
        k: campos.pop(k)
        for k in ("numero_identificacion", "tipo_identificacion", "nombres", "apellidos")
    }
    repo.crear(db, datos_usuario, campos)
    bitacora.registrar(
        db, "CREAR_BENEFICIARIO", "ok", admin.numero_identificacion,
        recurso=datos.numero_identificacion, ip=ip,
    )
    _guardar(db)
    return _ficha_de(db, datos.numero_identificacion)


def actualizar(db: Session, admin: Usuario, documento: str, datos: BeneficiarioUpdate, ip):
    persona = repo.obtener_persona(db, documento)
    usuario = repo.obtener_usuario(db, documento)
    if persona is None or usuario is None:
        raise NoEncontrado("Beneficiario no encontrado")
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise ReglaNegocio("No se envio ningun cambio")
    for campo in NO_NULOS & cambios.keys():
        if cambios[campo] is None:
            raise ReglaNegocio(f"El campo {campo} no puede quedar vacio")
    nacimiento = cambios.get("fecha_nacimiento")
    if nacimiento is not None and nacimiento > date.today():
        raise ReglaNegocio("La fecha de nacimiento no puede ser futura")
    for campo, valor in cambios.items():
        setattr(usuario if campo in CAMPOS_USUARIO else persona, campo, valor)
    bitacora.registrar(
        db, "ACTUALIZAR_BENEFICIARIO", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip, detalle="campos: " + ", ".join(sorted(cambios)),
    )
    _guardar(db)
    return _ficha_de(db, documento)


def cambiar_estado(
    db: Session, admin: Usuario, documento: str, nuevo: EstadoProceso,
    observaciones: str | None, ip,
):
    persona = repo.obtener_persona(db, documento)
    if persona is None:
        raise NoEncontrado("Beneficiario no encontrado")
    actual = repo.estado_vigente_de(db, documento) or E.aspirante
    motivo = None
    if nuevo not in TRANSICIONES[actual]:
        motivo = f"Transicion no valida: {actual.value} a {nuevo.value}"
    elif (
        nuevo == E.admitido
        and persona.fecha_nacimiento is not None
        and _es_menor(persona.fecha_nacimiento)
        and not repo.tiene_acudiente(db, documento)
    ):
        motivo = "Un menor solo se admite con un acudiente vinculado"
    if motivo:
        bitacora.registrar(
            db, "CAMBIAR_ESTADO", "rechazado", admin.numero_identificacion,
            recurso=documento, ip=ip, detalle=motivo,
        )
        db.commit()
        raise ReglaNegocio(motivo)
    repo.agregar_estado(db, documento, nuevo, observaciones)
    bitacora.registrar(
        db, "CAMBIAR_ESTADO", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip, detalle=f"{actual.value} a {nuevo.value}",
    )
    db.commit()
    return _ficha_de(db, documento)


def historial(db: Session, admin: Usuario, documento: str, ip):
    if repo.obtener_persona(db, documento) is None:
        raise NoEncontrado("Beneficiario no encontrado")
    filas = repo.historial(db, documento)
    bitacora.registrar(
        db, "CONSULTAR_HISTORIAL", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip,
    )
    db.commit()
    return filas
