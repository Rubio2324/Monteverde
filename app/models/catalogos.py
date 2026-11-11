from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import Localidad


class Barrio(Base):
    __tablename__ = "barrio"
    __table_args__ = (
        UniqueConstraint("nombre", "localidad", name="uq_barrio_nombre_localidad"),
    )

    id_barrio: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    localidad: Mapped[Localidad | None] = mapped_column(
        Enum(Localidad, name="localidad_enum"), nullable=True
    )


class AsociacionInstitucion(Base):
    __tablename__ = "asociacion_institucion"

    id_asociacion: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))


class Institucion(Base):
    __tablename__ = "institucion"

    id_institucion: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    direccion: Mapped[str | None] = mapped_column(String(200))
    id_barrio: Mapped[int | None] = mapped_column(ForeignKey("barrio.id_barrio"))
    id_asociacion: Mapped[int | None] = mapped_column(
        ForeignKey("asociacion_institucion.id_asociacion")
    )


class Contacto(Base):
    __tablename__ = "contactos"

    id_contacto: Mapped[int] = mapped_column(primary_key=True)
    id_institucion: Mapped[int] = mapped_column(ForeignKey("institucion.id_institucion"))
    nombre: Mapped[str] = mapped_column(String(150))
    cargo: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(30))
    correo: Mapped[str | None] = mapped_column(String(150))


class Eps(Base):
    __tablename__ = "eps"

    id_eps: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))


class Religion(Base):
    __tablename__ = "religion"

    id_religion: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))


class Profesion(Base):
    __tablename__ = "profesiones"

    id_profesion: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
