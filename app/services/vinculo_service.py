from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Usuario
from app.models.enums import EstadoProceso
from app.repositories import acudiente_repository as repo
from app.repositories import persona_repository as personas
from app.repositories import vinculo_repository as vinculos
from app.schemas.vinculo import AcudienteCreate
from app.services import auditoria_service as bitacora
from app.services.beneficiario_service import _es_menor


def _exigir_persona(db: Session, documento: str):
    persona = personas.obtener_persona(db, documento)
    if persona is None:
        raise NoEncontrado("Beneficiario no encontrado")
    return persona


def listar(db: Session, admin: Usuario, documento: str, ip):
    _exigir_persona(db, documento)
    filas = repo.listar(db, documento)
    bitacora.registrar(
        db, "CONSULTAR_ACUDIENTES", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip,
    )
    db.commit()
    return filas


def vincular(db: Session, admin: Usuario, documento: str, datos: AcudienteCreate, ip):
    _exigir_persona(db, documento)
    if datos.numero_identificacion == documento:
        raise ReglaNegocio("Una persona no puede ser su propio acudiente")
    if repo.existe_vinculo(db, datos.numero_identificacion, documento):
        raise Conflicto("Ese acudiente ya esta vinculado al beneficiario")
    campos = datos.model_dump()
    vinculo = campos.pop("vinculo")
    datos_usuario = {
        k: campos.pop(k)
        for k in ("numero_identificacion", "tipo_identificacion", "nombres", "apellidos")
    }
    try:
        vinculos.crear_o_reutilizar_acudiente(db, datos_usuario, campos)
        vinculos.vincular(db, datos.numero_identificacion, documento, vinculo)
        bitacora.registrar(
            db, "VINCULAR_ACUDIENTE", "ok", admin.numero_identificacion,
            recurso=documento, ip=ip,
            detalle=f"acudiente {datos.numero_identificacion} ({vinculo})",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ReglaNegocio("Datos invalidos: revise el barrio y los demas campos")
    return repo.listar(db, documento)


def desvincular(db: Session, admin: Usuario, documento: str, id_acudiente: str, ip):
    persona = _exigir_persona(db, documento)
    if not repo.existe_vinculo(db, id_acudiente, documento):
        raise NoEncontrado("El acudiente no esta vinculado a este beneficiario")
    estado = personas.estado_vigente_de(db, documento)
    if (
        persona.fecha_nacimiento is not None
        and _es_menor(persona.fecha_nacimiento)
        and estado in (EstadoProceso.admitido, EstadoProceso.matriculado)
        and repo.cantidad(db, documento) <= 1
    ):
        motivo = "No se puede quitar el unico acudiente de un menor admitido o matriculado"
        bitacora.registrar(
            db, "DESVINCULAR_ACUDIENTE", "rechazado", admin.numero_identificacion,
            recurso=documento, ip=ip, detalle=motivo,
        )
        db.commit()
        raise ReglaNegocio(motivo)
    repo.eliminar(db, id_acudiente, documento)
    bitacora.registrar(
        db, "DESVINCULAR_ACUDIENTE", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip, detalle=f"acudiente {id_acudiente}",
    )
    db.commit()