import re
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters import formulario_mapeo as mapeo
from app.adapters.google_forms_client import obtener_fuente
from app.core.config import settings
from app.core.errors import Conflicto, FuenteNoDisponible, NoEncontrado, ReglaNegocio
from app.core.textos import dividir_nombre, normalizar, solo_digitos
from app.repositories import catalogo_repository as catalogos
from app.repositories import formulario_repository as formularios
from app.repositories import persona_repository as personas
from app.repositories import vinculo_repository as vinculos
from app.services import auditoria_service as bitacora

DOC = re.compile(r"^\d{5,15}$")


class EnRevision(Exception):
    """La respuesta necesita que el administrador la revise."""


def _acudiente(db, d, clave, vinculo, documento_persona, id_barrio, avisos) -> None:
    completo = d.get(f"{clave}_nombre")
    documento = solo_digitos(d.get(f"{clave}_documento"))
    if not completo and not documento:
        return
    if not completo or not DOC.match(documento):
        avisos.append(f"{vinculo}: faltan el nombre o el documento; no se vinculo")
        return
    if documento == documento_persona:
        avisos.append(f"{vinculo}: el documento coincide con el del beneficiario")
        return
    nombres, apellidos = dividir_nombre(completo)
    correo = d.get(f"{clave}_correo")
    if correo and not mapeo.correo_valido(correo):
        avisos.append(f"{vinculo}: correo invalido; no se guardo")
        correo = None
    vinculos.crear_o_reutilizar_acudiente(
        db,
        {
            "numero_identificacion": documento,
            "tipo_identificacion": "CC",
            "nombres": nombres,
            "apellidos": apellidos,
        },
        {
            "ocupacion": d.get(f"{clave}_ocupacion"),
            "estado_civil": d.get("estado_civil"),
            "telefono": d.get(f"{clave}_telefono"),
            "correo": correo,
            "id_barrio": id_barrio,
        },
    )
    vinculos.vincular(db, documento, documento_persona, vinculo)


def _procesar(db: Session, d: dict, avisos: list[str]) -> str:
    if not mapeo.es_si(d.get("autorizacion")):
        raise ReglaNegocio("No se acepto la autorizacion de tratamiento de datos")
    registro = normalizar(d.get("tipo_registro"))
    if registro.startswith("nuevo"):
        es_nuevo = True
    elif registro.startswith("antiguo"):
        es_nuevo = False
    else:
        raise ReglaNegocio("Tipo de registro no reconocido (nuevo o antiguo)")
    documento = solo_digitos(d.get("documento"))
    if not DOC.match(documento):
        raise ReglaNegocio("Documento de identidad invalido")
    nombres, apellidos = d.get("nombres"), d.get("apellidos")
    if not nombres or not apellidos:
        raise ReglaNegocio("Faltan los nombres o los apellidos")
    nacimiento = mapeo.parsear_fecha(d.get("fecha_nacimiento"))
    if nacimiento is None or nacimiento > date.today():
        raise ReglaNegocio("Fecha de nacimiento invalida")

    existente = personas.obtener_usuario(db, documento)
    if es_nuevo and existente is not None:
        raise EnRevision("El documento ya existe en el sistema")
    if not es_nuevo and (
        existente is None or personas.obtener_persona(db, documento) is None
    ):
        raise EnRevision("Se marco como antiguo, pero el documento no existe")

    localidad = mapeo.localidad(d.get("localidad"))
    barrio = catalogos.buscar_barrio(db, d.get("barrio"), localidad)
    institucion = catalogos.buscar_institucion(db, d.get("colegio"))
    religion = catalogos.buscar_religion(db, d.get("religion"))
    correo = d.get("correo")
    if correo and not mapeo.correo_valido(correo):
        avisos.append("Correo invalido; no se guardo")
        correo = None

    notas = []
    if d.get("barrio") and barrio is None:
        avisos.append("Barrio no encontrado en el catalogo")
        notas.append(f"Barrio informado: {d['barrio']}")
    if d.get("localidad") and localidad is None:
        avisos.append("Localidad no reconocida")
        notas.append(f"Localidad informada: {d['localidad']}")
    if d.get("colegio") and institucion is None:
        avisos.append("Colegio no encontrado en el catalogo")
        notas.append(f"Colegio informado: {d['colegio']}")
    if d.get("religion") and religion is None:
        avisos.append("Religion no encontrada en el catalogo")
        notas.append(f"Religion informada: {d['religion']}")

    id_barrio = barrio.id_barrio if barrio else None

    if not es_nuevo:
        persona = personas.obtener_persona(db, documento)
        actualizar = {
            "telefono": d.get("telefono"),
            "correo": correo,
            "direccion": d.get("direccion"),
            "grado": d.get("grado"),
            "id_barrio": id_barrio,
            "id_institucion": institucion.id_institucion if institucion else None,
        }
        for campo, valor in actualizar.items():
            if valor is not None:
                setattr(persona, campo, valor)
        db.flush()
        return documento

    if not d.get("tipo_documento"):
        avisos.append("Falta el tipo de documento")
    bautizado, comunion = mapeo.sacramentos(d.get("sacramentos"))
    personas.crear(
        db,
        {
            "numero_identificacion": documento,
            "tipo_identificacion": mapeo.tipo_documento(d.get("tipo_documento")),
            "nombres": nombres,
            "apellidos": apellidos,
        },
        {
            "fecha_nacimiento": nacimiento,
            "direccion": d.get("direccion"),
            "id_barrio": id_barrio,
            "correo": correo,
            "telefono": d.get("telefono"),
            "id_religion": religion.id_religion if religion else None,
            "bautizado": bautizado,
            "primera_comunion": comunion,
            "id_institucion": institucion.id_institucion if institucion else None,
            "grado": d.get("grado"),
            "observaciones": "; ".join(notas) or None,
            "foto_url": d.get("foto"),
            "boletin_url": d.get("boletin"),
            "autoriza_tratamiento_datos": True,
        },
    )
    programa = catalogos.programa_por_nombre(db, settings.programa_inscripcion)
    if programa is None:
        avisos.append("Programa de inscripcion no encontrado")
    else:
        vinculos.inscribir_programa(db, programa.id_programa, documento)

    _acudiente(db, d, "padre", "Padre", documento, id_barrio, avisos)
    _acudiente(db, d, "madre", "Madre", documento, id_barrio, avisos)

    if d.get("preceptor") and not normalizar(d["preceptor"]).startswith("ninguno"):
        preceptor = catalogos.buscar_preceptor(db, d["preceptor"])
        if preceptor is None:
            avisos.append("Preceptor no encontrado")
        else:
            vinculos.asignar_preceptor(db, documento, preceptor.numero_identificacion)
    return documento


def importar(db: Session, admin_documento: str | None, ip: str | None) -> dict:
    try:
        filas = obtener_fuente().leer()
    except FuenteNoDisponible:
        bitacora.registrar(
            db, "IMPORTAR", "fallo", admin_documento, ip=ip, detalle="fuente no disponible"
        )
        db.commit()
        raise
    conteo = {
        "leidas": len(filas),
        "nuevas": 0,
        "procesadas": 0,
        "revision": 0,
        "error": 0,
        "omitidas": 0,
    }
    for fila in filas:
        d = mapeo.mapear_fila(fila)
        id_respuesta = mapeo.identificador(d, fila)
        if formularios.existe(db, id_respuesta):
            conteo["omitidas"] += 1
            continue
        registro = formularios.guardar(db, id_respuesta, mapeo.fecha_marca(d), fila)
        conteo["nuevas"] += 1
        avisos: list[str] = []
        estado, mensaje, documento = "procesada", None, None
        try:
            with db.begin_nested():
                documento = _procesar(db, d, avisos)
            mensaje = "; ".join(avisos) or None
        except EnRevision as e:
            estado, mensaje = "revision", str(e)
        except (ReglaNegocio, Conflicto) as e:
            estado, mensaje = "error", str(e)
        except IntegrityError:
            estado, mensaje = "error", "Datos invalidos: referencias o duplicados"
        if documento is None:
            crudo = solo_digitos(d.get("documento"))
            documento = crudo if DOC.match(crudo) else None
        registro.estado_procesamiento = estado
        registro.error = mensaje
        registro.numero_identificacion = documento
        conteo["procesadas" if estado == "procesada" else estado] += 1
        db.flush()
    bitacora.registrar(
        db, "IMPORTAR", "ok", admin_documento, ip=ip,
        detalle=", ".join(f"{k}={v}" for k, v in conteo.items()),
    )
    db.commit()
    return conteo


def listar(db: Session, admin_documento: str, estado, page, size, ip):
    total, items = formularios.listar(db, estado, page, size)
    bitacora.registrar(db, "LISTAR_INSCRIPCIONES", "ok", admin_documento, ip=ip)
    db.commit()
    return {"total": total, "page": page, "size": size, "items": items}


def detalle(db: Session, admin_documento: str, id_inscripcion: int, ip):
    registro = formularios.obtener(db, id_inscripcion)
    if registro is None:
        raise NoEncontrado("Inscripcion no encontrada")
    bitacora.registrar(
        db, "CONSULTAR_INSCRIPCION", "ok", admin_documento,
        recurso=f"inscripcion:{id_inscripcion}", ip=ip,
    )
    db.commit()
    return registro


def descartar(db: Session, admin_documento: str, id_inscripcion: int, ip):
    registro = formularios.obtener(db, id_inscripcion)
    if registro is None:
        raise NoEncontrado("Inscripcion no encontrada")
    if registro.estado_procesamiento not in {"revision", "error"}:
        raise ReglaNegocio("Solo se descartan inscripciones en revision o con error")
    registro.estado_procesamiento = "descartada"
    bitacora.registrar(
        db, "DESCARTAR_INSCRIPCION", "ok", admin_documento,
        recurso=f"inscripcion:{id_inscripcion}", ip=ip,
    )
    db.commit()
    return registro
