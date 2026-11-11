from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InscripcionFormulario(Base):
    __tablename__ = "inscripcion_formulario"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_respuesta: Mapped[str] = mapped_column(String(100), unique=True)
    fecha_respuesta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    datos: Mapped[dict] = mapped_column(JSONB)
    estado_procesamiento: Mapped[str] = mapped_column(
        String(20), default="pendiente", server_default="pendiente"
    )
    error: Mapped[str | None] = mapped_column(Text)
    numero_identificacion: Mapped[str | None] = mapped_column(String(20))
    fecha_importacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
