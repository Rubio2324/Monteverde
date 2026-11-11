from datetime import date, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Programa(Base):
    __tablename__ = "programa"

    id_programa: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)


class ProgramaPersona(Base):
    __tablename__ = "programa_persona"

    id_programa_persona: Mapped[int] = mapped_column(primary_key=True)
    id_programa: Mapped[int] = mapped_column(ForeignKey("programa.id_programa"))
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )


class Curso(Base):
    __tablename__ = "curso"

    id_curso: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    id_programa: Mapped[int] = mapped_column(ForeignKey("programa.id_programa"))
    numero_identificacion_profesor: Mapped[str] = mapped_column(
        ForeignKey("profesor.numero_identificacion")
    )
    dia: Mapped[str | None] = mapped_column(String(20))
    hora_inicio: Mapped[time | None] = mapped_column(Time)
    hora_fin: Mapped[time | None] = mapped_column(Time)
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    es_calificable: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )


class CursoPersona(Base):
    __tablename__ = "curso_persona"

    id_matricula: Mapped[int] = mapped_column(primary_key=True)
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )
    numero_asistencias: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )
    aprobo: Mapped[bool | None] = mapped_column(Boolean)
    nota_definitiva: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))


class Asistencia(Base):
    __tablename__ = "asistencia"

    id_asistencia: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date)
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))


class Entregable(Base):
    __tablename__ = "entregable"

    id_entregable: Mapped[int] = mapped_column(primary_key=True)
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id_curso"))
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )
    nombre: Mapped[str] = mapped_column(String(150))
    fecha_entrega: Mapped[date | None] = mapped_column(Date)
    nota: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    porcentaje_entregable: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
