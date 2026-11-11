from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.models import Usuario
from app.models.enums import EstadoProceso
from app.repositories import curso_repository as repo
from app.repositories import persona_repository as personas
from app.schemas.academico import CursoCreate, CursoUpdate
from app.services import auditoria_service as bitacora

MATRICULABLES = {EstadoProceso.admitido, EstadoProceso.matriculado}
OBLIGATORIOS = (
    "nombre",
    "id_programa",
    "numero_identificacion_profesor",
    "es_calificable",
)


def _guardar(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ReglaNegocio(
            "Datos invalidos: revise las referencias (programa, profesor, curso, beneficiario)"
        )


def _curso(fila) -> dict:
    curso, programa, profesor, matriculados = fila
    return {
        "id_curso": curso.id_curso,
        "nombre": curso.nombre,
        "id_programa": curso.id_programa,
        "programa": programa,
        "numero_identificacion_profesor": curso.numero_identificacion_profesor,
        "profesor": f"{profesor.nombres} {profesor.apellidos}",
        "dia": curso.dia,
        "hora_inicio": curso.hora_inicio,
        "hora_fin": curso.hora_fin,
        "fecha_inicio": curso.fecha_inicio,
        "fecha_fin": curso.fecha_fin,
        "es_calificable": curso.es_calificable,
        "matriculados": matriculados,
    }


def _curso_de(db: Session, id_curso: int) -> dict:
    fila = repo.curso_detalle(db, id_curso)
    if fila is None:
        raise NoEncontrado("Curso no encontrado")
    return _curso(fila)


def _matricula(fila) -> dict:
    matricula, usuario, curso = fila
    return {
        "id_matricula": matricula.id_matricula,
        "id_curso": matricula.id_curso,
        "curso": curso,
        "numero_identificacion_persona": usuario.numero_identificacion,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "numero_asistencias": matricula.numero_asistencias,
        "aprobo": matricula.aprobo,
        "nota_definitiva": matricula.nota_definitiva,
    }


def _validar_horario(hora_inicio, hora_fin, fecha_inicio, fecha_fin) -> None:
    if hora_inicio and hora_fin and hora_fin <= hora_inicio:
        raise ReglaNegocio("La hora de fin debe ser posterior a la de inicio")
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        raise ReglaNegocio("La fecha de fin no puede ser anterior a la de inicio")


def _validar_referencias(db: Session, id_programa: int, documento_profesor: str) -> None:
    if repo.obtener_programa(db, id_programa) is None:
        raise ReglaNegocio("El programa no existe")
    profesor = repo.obtener_profesor(db, documento_profesor)
    if profesor is None or profesor.estado != "activo":
        raise ReglaNegocio("El profesor no existe o no esta activo")


def listar_programas(db: Session) -> list[dict]:
    return [
        {
            "id_programa": p.id_programa,
            "nombre": p.nombre,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin,
        }
        for p in repo.listar_programas(db)
    ]


def listar_profesores(db: Session) -> list[dict]:
    return [
        {
            "numero_identificacion": u.numero_identificacion,
            "nombres": u.nombres,
            "apellidos": u.apellidos,
            "correo": p.correo,
            "es_preceptor": p.es_preceptor,
            "estado": p.estado,
        }
        for p, u in repo.listar_profesores(db)
    ]


def listar_cursos(db: Session, id_programa, page, size) -> dict:
    total, filas = repo.listar_cursos(db, id_programa, page, size)
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [_curso(f) for f in filas],
    }


def consultar_curso(db: Session, id_curso: int) -> dict:
    return _curso_de(db, id_curso)


def crear_curso(db: Session, admin: Usuario, datos: CursoCreate, ip) -> dict:
    _validar_horario(
        datos.hora_inicio, datos.hora_fin, datos.fecha_inicio, datos.fecha_fin
    )
    _validar_referencias(db, datos.id_programa, datos.numero_identificacion_profesor)
    curso = repo.crear_curso(db, datos.model_dump())
    id_curso = curso.id_curso
    bitacora.registrar(
        db, "CREAR_CURSO", "ok", admin.numero_identificacion,
        recurso=f"curso:{id_curso}", ip=ip, detalle=curso.nombre,
    )
    _guardar(db)
    return _curso_de(db, id_curso)


def actualizar_curso(
    db: Session, admin: Usuario, id_curso: int, datos: CursoUpdate, ip
) -> dict:
    curso = repo.obtener_curso(db, id_curso)
    if curso is None:
        raise NoEncontrado("Curso no encontrado")
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise ReglaNegocio("No se envio ningun cambio")
    for campo in OBLIGATORIOS:
        if campo in cambios and cambios[campo] is None:
            raise ReglaNegocio(f"El campo {campo} no puede quedar vacio")
    _validar_horario(
        cambios.get("hora_inicio", curso.hora_inicio),
        cambios.get("hora_fin", curso.hora_fin),
        cambios.get("fecha_inicio", curso.fecha_inicio),
        cambios.get("fecha_fin", curso.fecha_fin),
    )
    if "id_programa" in cambios or "numero_identificacion_profesor" in cambios:
        _validar_referencias(
            db,
            cambios.get("id_programa", curso.id_programa),
            cambios.get(
                "numero_identificacion_profesor", curso.numero_identificacion_profesor
            ),
        )
    for campo, valor in cambios.items():
        setattr(curso, campo, valor)
    bitacora.registrar(
        db, "ACTUALIZAR_CURSO", "ok", admin.numero_identificacion,
        recurso=f"curso:{id_curso}", ip=ip, detalle="campos: " + ", ".join(sorted(cambios)),
    )
    _guardar(db)
    return _curso_de(db, id_curso)


def matricular(
    db: Session, admin: Usuario, id_curso: int, documento: str, ip
) -> dict:
    curso = repo.obtener_curso(db, id_curso)
    if curso is None:
        raise NoEncontrado("Curso no encontrado")
    if personas.obtener_persona(db, documento) is None:
        raise NoEncontrado("Beneficiario no encontrado")
    estado = personas.estado_vigente_de(db, documento)
    if estado not in MATRICULABLES:
        motivo = "Solo se matriculan beneficiarios admitidos o matriculados"
        bitacora.registrar(
            db, "MATRICULAR", "rechazado", admin.numero_identificacion,
            recurso=documento, ip=ip, detalle=f"curso {id_curso}: {motivo}",
        )
        db.commit()
        raise ReglaNegocio(motivo)
    if repo.matricula_existente(db, id_curso, documento) is not None:
        raise Conflicto("El beneficiario ya esta matriculado en este curso")
    matricula = repo.crear_matricula(db, id_curso, documento)
    id_matricula = matricula.id_matricula
    bitacora.registrar(
        db, "MATRICULAR", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip, detalle=f"curso {id_curso}: {curso.nombre}",
    )
    _guardar(db)
    return _matricula(repo.matricula_detalle(db, id_matricula))


def matriculas_de_curso(db: Session, admin: Usuario, id_curso: int, ip) -> list[dict]:
    if repo.obtener_curso(db, id_curso) is None:
        raise NoEncontrado("Curso no encontrado")
    filas = repo.matriculas_de_curso(db, id_curso)
    bitacora.registrar(
        db, "CONSULTAR_MATRICULAS", "ok", admin.numero_identificacion,
        recurso=f"curso:{id_curso}", ip=ip,
    )
    db.commit()
    return [_matricula(f) for f in filas]


def cursos_de_beneficiario(
    db: Session, admin: Usuario, documento: str, ip
) -> list[dict]:
    if personas.obtener_persona(db, documento) is None:
        raise NoEncontrado("Beneficiario no encontrado")
    filas = repo.matriculas_de_persona(db, documento)
    bitacora.registrar(
        db, "CONSULTAR_CURSOS_BENEFICIARIO", "ok", admin.numero_identificacion,
        recurso=documento, ip=ip,
    )
    db.commit()
    return [_matricula(f) for f in filas]
