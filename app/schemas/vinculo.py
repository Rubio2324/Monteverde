from pydantic import BaseModel, Field

from app.schemas.beneficiario import CORREO, TIPOS


class AcudienteCreate(BaseModel):
    numero_identificacion: str = Field(pattern=r"^\d{5,15}$")
    tipo_identificacion: str = Field(pattern=TIPOS)
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    vinculo: str = Field(min_length=1, max_length=50)
    telefono: str | None = Field(default=None, max_length=30)
    correo: str | None = Field(default=None, max_length=150, pattern=CORREO)
    ocupacion: str | None = Field(default=None, max_length=120)
    estado_civil: str | None = Field(default=None, max_length=30)
    direccion: str | None = Field(default=None, max_length=200)
    id_barrio: int | None = None
    nivel_escolar: str | None = Field(default=None, max_length=50)


class AcudienteOut(BaseModel):
    numero_identificacion: str
    tipo_identificacion: str
    nombres: str
    apellidos: str
    vinculo: str
    telefono: str | None
    correo: str | None
    ocupacion: str | None