from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import EstadoPersona, EstadoProceso


class Persona(Base):
    __tablename__ = "persona"

    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion"), primary_key=True
    )
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    direccion: Mapped[str | None] = mapped_column(String(200))
    id_barrio: Mapped[int | None] = mapped_column(ForeignKey("barrio.id_barrio"))
    correo: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(30))
    estrato_socioeconomico: Mapped[int | None] = mapped_column(Integer)
    id_eps: Mapped[int | None] = mapped_column(ForeignKey("eps.id_eps"))
    id_religion: Mapped[int | None] = mapped_column(ForeignKey("religion.id_religion"))
    bautizado: Mapped[bool | None] = mapped_column(Boolean)
    primera_comunion: Mapped[bool | None] = mapped_column(Boolean)
    id_institucion: Mapped[int | None] = mapped_column(
        ForeignKey("institucion.id_institucion")
    )
    grado: Mapped[str | None] = mapped_column(String(30))
    subgrupo: Mapped[str | None] = mapped_column(String(30))
    observaciones: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[EstadoPersona] = mapped_column(
        Enum(EstadoPersona, name="estado_persona_enum"),
        default=EstadoPersona.activo,
        server_default="activo",
    )
    foto_url: Mapped[str | None] = mapped_column(String(500))
    boletin_url: Mapped[str | None] = mapped_column(String(500))
    autoriza_tratamiento_datos: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )


class EstadoPersonaHistorial(Base):
    __tablename__ = "estado_persona"

    id_estado: Mapped[int] = mapped_column(primary_key=True)
    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )
    estado: Mapped[EstadoProceso] = mapped_column(
        Enum(EstadoProceso, name="estado_proceso_enum")
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    fecha_estado: Mapped[date] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)


class RedSocial(Base):
    __tablename__ = "redes_sociales"

    id_red_social: Mapped[int] = mapped_column(primary_key=True)
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion")
    )
    plataforma: Mapped[str] = mapped_column(String(50))
    usuario_o_url: Mapped[str] = mapped_column(String(300))


class Acudiente(Base):
    __tablename__ = "acudiente"

    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion"), primary_key=True
    )
    ocupacion: Mapped[str | None] = mapped_column(String(120))
    estado_civil: Mapped[str | None] = mapped_column(String(30))
    telefono: Mapped[str | None] = mapped_column(String(30))
    correo: Mapped[str | None] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(String(200))
    id_barrio: Mapped[int | None] = mapped_column(ForeignKey("barrio.id_barrio"))
    nivel_escolar: Mapped[str | None] = mapped_column(String(50))


class AcudientePersona(Base):
    __tablename__ = "acudiente_persona"

    id_acudiente: Mapped[str] = mapped_column(
        ForeignKey("acudiente.numero_identificacion"), primary_key=True
    )
    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion"), primary_key=True
    )
    vinculo: Mapped[str] = mapped_column(String(50))


class Profesor(Base):
    __tablename__ = "profesor"

    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion"), primary_key=True
    )
    correo: Mapped[str | None] = mapped_column(String(150))
    id_profesion: Mapped[int | None] = mapped_column(
        ForeignKey("profesiones.id_profesion")
    )
    universidad_graduacion: Mapped[str | None] = mapped_column(String(150))
    grado_profesion: Mapped[str | None] = mapped_column(String(100))
    es_preceptor: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="activo", server_default="activo"
    )


class PreceptorPersona(Base):
    __tablename__ = "preceptor_persona"

    numero_identificacion_persona: Mapped[str] = mapped_column(
        ForeignKey("persona.numero_identificacion"), primary_key=True
    )
    id_preceptor: Mapped[str] = mapped_column(
        ForeignKey("profesor.numero_identificacion"), primary_key=True
    )
    fecha_inicio: Mapped[date] = mapped_column(Date, primary_key=True)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
