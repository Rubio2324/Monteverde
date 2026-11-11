"""Datos iniciales y ficticios para el prototipo.

Uso: python -m app.db.seed [cantidad_de_beneficiarios]
Es idempotente: se puede ejecutar varias veces sin duplicar.
Todos los datos de personas son ficticios.
"""
import random
import sys
from datetime import date

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import (
    Acudiente,
    AcudientePersona,
    Administrador,
    Barrio,
    Eps,
    EstadoPersonaHistorial,
    Institucion,
    Persona,
    Profesion,
    Profesor,
    Programa,
    ProgramaPersona,
    Religion,
    Rol,
    Usuario,
    UsuarioRol,
)
from app.models.enums import EstadoProceso, Localidad

# Credenciales de PRUEBA (solo desarrollo local)
DOC_ADMIN = "1000000001"
DOC_PROFESOR = "1000000002"
CLAVE_ADMIN = "Monteverde2026"

ROLES = ["Administrador", "Profesor", "Acudiente", "Estudiante"]
PROGRAMAS = ["Mejor Bachiller", "Juventus"]
EPS = ["Sanitas", "Compensar", "Nueva EPS", "Sura", "Famisanar", "Salud Total"]
RELIGIONES = ["Catolica", "Cristiana", "Judia", "Agnostico", "Ateo", "Otra"]
PROFESIONES = [
    "Ingeniero de Sistemas",
    "Licenciado en Ingles",
    "Licenciado en Frances",
    "Musico",
    "Profesor de Educacion Fisica",
]
BARRIOS = [
    ("Patio Bonito", Localidad.Kennedy),
    ("Timiza", Localidad.Kennedy),
    ("Las Cruces", Localidad.Santa_Fe),
    ("Danubio", Localidad.Usme),
    ("San Benito", Localidad.Tunjuelito),
    ("El Porvenir", Localidad.Bosa),
    ("Modelia", Localidad.Fontibon),
    ("Egipto", Localidad.La_Candelaria),
    ("Quiroga", Localidad.Rafael_Uribe_Uribe),
    ("Lucero", Localidad.Ciudad_Bolivar),
]
INSTITUCIONES = [
    "Colegio Argelia IED",
    "Colegio Jaime Garzon Forero IED",
    "Colegio Miravalle IED",
    "Colegio La Giralda IED",
    "Colegio Las Margaritas IED",
    "Colegio Jorge Isaacs IED",
    "Colegio Laurel de Cera IED",
    "Colegio El Nogal IED",
]
NOMBRES = [
    "Juan", "Maria", "Carlos", "Laura", "Andres", "Camila", "Santiago",
    "Valentina", "Daniel", "Sofia", "Mateo", "Isabella", "Sebastian",
    "Luciana", "David", "Mariana",
]
APELLIDOS = [
    "Gomez", "Rodriguez", "Martinez", "Lopez", "Garcia", "Hernandez",
    "Ramirez", "Torres", "Diaz", "Vargas", "Castro", "Moreno",
]
GRADOS = ["Octavo", "Noveno", "Decimo"]
OCUPACIONES = ["Comerciante", "Docente", "Independiente", "Conductor", "Empleado"]
ESTADOS_CIVILES = ["Casados", "Union libre", "Separados", "Solteros"]


def obtener_o_crear(s, modelo, filtro, **datos):
    obj = s.scalar(select(modelo).filter_by(**filtro))
    if obj is None:
        obj = modelo(**filtro, **datos)
        s.add(obj)
        s.flush()
    return obj


def asignar_rol(s, documento, nombre_rol):
    rol = s.scalar(select(Rol).filter_by(nombre=nombre_rol))
    if s.get(UsuarioRol, (documento, rol.id_rol)) is None:
        s.add(UsuarioRol(numero_identificacion=documento, id_rol=rol.id_rol))
        s.flush()


def crear_catalogos(s):
    for nombre in ROLES:
        obtener_o_crear(s, Rol, {"nombre": nombre})
    for nombre in PROGRAMAS:
        obtener_o_crear(s, Programa, {"nombre": nombre})
    for nombre in EPS:
        obtener_o_crear(s, Eps, {"nombre": nombre})
    for nombre in RELIGIONES:
        obtener_o_crear(s, Religion, {"nombre": nombre})
    for nombre in PROFESIONES:
        obtener_o_crear(s, Profesion, {"nombre": nombre})
    barrios = [
        obtener_o_crear(s, Barrio, {"nombre": n, "localidad": loc})
        for n, loc in BARRIOS
    ]
    for i, nombre in enumerate(INSTITUCIONES):
        obtener_o_crear(
            s,
            Institucion,
            {"nombre": nombre},
            id_barrio=barrios[i % len(barrios)].id_barrio,
        )


def crear_admin(s):
    if s.get(Usuario, DOC_ADMIN) is None:
        s.add(
            Usuario(
                numero_identificacion=DOC_ADMIN,
                tipo_identificacion="CC",
                nombres="Administrador",
                apellidos="Prueba",
                password_hash=hash_password(CLAVE_ADMIN),
                estado="activo",
            )
        )
        s.flush()
        s.add(Administrador(numero_identificacion=DOC_ADMIN))
        s.flush()
    asignar_rol(s, DOC_ADMIN, "Administrador")


def crear_profesor(s):
    if s.get(Usuario, DOC_PROFESOR) is None:
        s.add(
            Usuario(
                numero_identificacion=DOC_PROFESOR,
                tipo_identificacion="CC",
                nombres="Profesor",
                apellidos="Prueba",
                password_hash=None,
                estado="activo",
            )
        )
        s.flush()
        profesion = s.scalar(select(Profesion).filter_by(nombre="Licenciado en Ingles"))
        s.add(
            Profesor(
                numero_identificacion=DOC_PROFESOR,
                correo="profesor.prueba@ejemplo.test",
                id_profesion=profesion.id_profesion,
                universidad_graduacion="Universidad Ficticia",
                grado_profesion="Licenciatura",
                es_preceptor=True,
                estado="activo",
            )
        )
        s.flush()
    asignar_rol(s, DOC_PROFESOR, "Profesor")


def crear_beneficiarios(s, cantidad):
    rng = random.Random(42)
    barrios = s.scalars(select(Barrio)).all()
    instituciones = s.scalars(select(Institucion)).all()
    eps = s.scalars(select(Eps)).all()
    religiones = s.scalars(select(Religion)).all()
    programas = s.scalars(select(Programa)).all()
    estados = [
        EstadoProceso.aspirante,
        EstadoProceso.aspirante,
        EstadoProceso.aspirante,
        EstadoProceso.admitido,
        EstadoProceso.matriculado,
    ]
    creados = 0
    for i in range(cantidad):
        doc = str(1100000001 + i)
        doc_acu = str(5000000001 + i)
        if s.get(Usuario, doc) is not None:
            continue
        apellidos = f"{rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"
        barrio = rng.choice(barrios)
        s.add(
            Usuario(
                numero_identificacion=doc,
                tipo_identificacion="TI",
                nombres=rng.choice(NOMBRES),
                apellidos=apellidos,
                password_hash=None,
                estado="inactivo",
            )
        )
        s.flush()
        s.add(
            Persona(
                numero_identificacion=doc,
                fecha_nacimiento=date(
                    rng.randint(2008, 2013), rng.randint(1, 12), rng.randint(1, 28)
                ),
                direccion=f"Calle {rng.randint(1, 99)} # {rng.randint(1, 99)}-{rng.randint(1, 99)}",
                id_barrio=barrio.id_barrio,
                correo=f"beneficiario{i + 1}@ejemplo.test",
                telefono="3" + "".join(str(rng.randint(0, 9)) for _ in range(9)),
                estrato_socioeconomico=rng.randint(1, 4),
                id_eps=rng.choice(eps).id_eps,
                id_religion=rng.choice(religiones).id_religion,
                bautizado=rng.choice([True, False]),
                primera_comunion=rng.choice([True, False]),
                id_institucion=rng.choice(instituciones).id_institucion,
                grado=rng.choice(GRADOS),
                autoriza_tratamiento_datos=True,
            )
        )
        s.flush()
        s.add(
            EstadoPersonaHistorial(
                numero_identificacion=doc,
                estado=rng.choice(estados),
                activo=True,
                fecha_estado=date.today(),
                observaciones="Dato ficticio de prueba",
            )
        )
        s.add(
            ProgramaPersona(
                id_programa=rng.choice(programas).id_programa,
                numero_identificacion_persona=doc,
            )
        )
        s.add(
            Usuario(
                numero_identificacion=doc_acu,
                tipo_identificacion="CC",
                nombres=rng.choice(NOMBRES),
                apellidos=apellidos,
                password_hash=None,
                estado="inactivo",
            )
        )
        s.flush()
        s.add(
            Acudiente(
                numero_identificacion=doc_acu,
                ocupacion=rng.choice(OCUPACIONES),
                estado_civil=rng.choice(ESTADOS_CIVILES),
                telefono="3" + "".join(str(rng.randint(0, 9)) for _ in range(9)),
                correo=f"acudiente{i + 1}@ejemplo.test",
                id_barrio=barrio.id_barrio,
            )
        )
        s.flush()
        s.add(
            AcudientePersona(
                id_acudiente=doc_acu,
                numero_identificacion_persona=doc,
                vinculo="Madre",
            )
        )
        s.flush()
        asignar_rol(s, doc, "Estudiante")
        asignar_rol(s, doc_acu, "Acudiente")
        creados += 1
    return creados


def main():
    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    with SessionLocal() as s:
        crear_catalogos(s)
        crear_admin(s)
        crear_profesor(s)
        creados = crear_beneficiarios(s, cantidad)
        s.commit()
    print(f"Listo. Beneficiarios nuevos: {creados}")
    print(f"Administrador de prueba: documento {DOC_ADMIN}")


if __name__ == "__main__":
    main()
