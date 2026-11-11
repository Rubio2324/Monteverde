from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    numero_identificacion: Mapped[str] = mapped_column(String(20), primary_key=True)
    tipo_identificacion: Mapped[str] = mapped_column(String(20))
    nombres: Mapped[str] = mapped_column(String(120))
    apellidos: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20), default="activo", server_default="activo"
    )


class Rol(Base):
    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)


class Permiso(Base):
    __tablename__ = "permisos"

    id_permiso: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200))


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), primary_key=True)
    id_permiso: Mapped[int] = mapped_column(
        ForeignKey("permisos.id_permiso"), primary_key=True
    )


class UsuarioRol(Base):
    __tablename__ = "usuario_rol"

    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion"), primary_key=True
    )
    id_rol: Mapped[int] = mapped_column(ForeignKey("roles.id_rol"), primary_key=True)


class Administrador(Base):
    __tablename__ = "administrador"

    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion"), primary_key=True
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    numero_identificacion: Mapped[str] = mapped_column(
        ForeignKey("usuarios.numero_identificacion")
    )
    vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revocado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    numero_identificacion: Mapped[str | None] = mapped_column(String(20))
    accion: Mapped[str] = mapped_column(String(50))
    recurso: Mapped[str | None] = mapped_column(String(200))
    resultado: Mapped[str] = mapped_column(String(20))
    ip: Mapped[str | None] = mapped_column(String(45))
    detalle: Mapped[str | None] = mapped_column(Text)
