from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EstadoPersona, EstadoProceso

CORREO = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
TIPOS = r"^(TI|CC|RC|CE|OTRO)$"


class DatosPersona(BaseModel):
    direccion: str | None = Field(default=None, max_length=200)
    id_barrio: int | None = None
    correo: str | None = Field(default=None, max_length=150, pattern=CORREO)
    telefono: str | None = Field(default=None, max_length=30)
    estrato_socioeconomico: int | None = Field(default=None, ge=0, le=6)
    id_eps: int | None = None
    id_religion: int | None = None
    bautizado: bool | None = None
    primera_comunion: bool | None = None
    id_institucion: int | None = None
    grado: str | None = Field(default=None, max_length=30)
    subgrupo: str | None = Field(default=None, max_length=30)
    observaciones: str | None = None
    foto_url: str | None = Field(default=None, max_length=500)
    boletin_url: str | None = Field(default=None, max_length=500)


class BeneficiarioCreate(DatosPersona):
    numero_identificacion: str = Field(pattern=r"^\d{5,15}$")
    tipo_identificacion: str = Field(pattern=TIPOS)
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    fecha_nacimiento: date
    autoriza_tratamiento_datos: bool = False


class BeneficiarioUpdate(DatosPersona):
    tipo_identificacion: str | None = Field(default=None, pattern=TIPOS)
    nombres: str | None = Field(default=None, min_length=1, max_length=120)
    apellidos: str | None = Field(default=None, min_length=1, max_length=120)
    fecha_nacimiento: date | None = None
    autoriza_tratamiento_datos: bool | None = None


class BeneficiarioOut(BaseModel):
    numero_identificacion: str
    tipo_identificacion: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None
    direccion: str | None
    id_barrio: int | None
    correo: str | None
    telefono: str | None
    estrato_socioeconomico: int | None
    id_eps: int | None
    id_religion: int | None
    bautizado: bool | None
    primera_comunion: bool | None
    id_institucion: int | None
    grado: str | None
    subgrupo: str | None
    observaciones: str | None
    foto_url: str | None
    boletin_url: str | None
    autoriza_tratamiento_datos: bool
    activo: EstadoPersona
    estado: EstadoProceso | None


class BeneficiarioItem(BaseModel):
    numero_identificacion: str
    tipo_identificacion: str
    nombres: str
    apellidos: str
    grado: str | None
    estado: EstadoProceso | None


class Pagina(BaseModel):
    total: int
    page: int
    size: int
    items: list[BeneficiarioItem]


class CambioEstado(BaseModel):
    estado: EstadoProceso
    observaciones: str | None = Field(default=None, max_length=500)


class HistorialItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    estado: EstadoProceso
    activo: bool
    fecha_estado: date
    observaciones: str | None
