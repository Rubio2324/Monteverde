from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, Field

# Sin tildes, como el resto de los datos del prototipo
DIA = r"^(Lunes|Martes|Miercoles|Jueves|Viernes|Sabado|Domingo)$"
DOC = r"^\d{5,15}$"


class ProgramaOut(BaseModel):
    id_programa: int
    nombre: str
    fecha_inicio: date | None
    fecha_fin: date | None


class ProfesorOut(BaseModel):
    numero_identificacion: str
    nombres: str
    apellidos: str
    correo: str | None
    es_preceptor: bool
    estado: str


class CursoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    id_programa: int
    numero_identificacion_profesor: str = Field(pattern=DOC)
    dia: str | None = Field(default=None, pattern=DIA)
    hora_inicio: time | None = None
    hora_fin: time | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    es_calificable: bool = False


class CursoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    id_programa: int | None = None
    numero_identificacion_profesor: str | None = Field(default=None, pattern=DOC)
    dia: str | None = Field(default=None, pattern=DIA)
    hora_inicio: time | None = None
    hora_fin: time | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    es_calificable: bool | None = None


class CursoOut(BaseModel):
    id_curso: int
    nombre: str
    id_programa: int
    programa: str
    numero_identificacion_profesor: str
    profesor: str
    dia: str | None
    hora_inicio: time | None
    hora_fin: time | None
    fecha_inicio: date | None
    fecha_fin: date | None
    es_calificable: bool
    matriculados: int


class PaginaCursos(BaseModel):
    total: int
    page: int
    size: int
    items: list[CursoOut]


class MatriculaCreate(BaseModel):
    numero_identificacion_persona: str = Field(pattern=DOC)


class MatriculaOut(BaseModel):
    id_matricula: int
    id_curso: int
    curso: str
    numero_identificacion_persona: str
    nombres: str
    apellidos: str
    numero_asistencias: int
    aprobo: bool | None
    nota_definitiva: Decimal | None
