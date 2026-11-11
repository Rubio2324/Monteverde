from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    numero_identificacion: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str]


class UsuarioOut(BaseModel):
    numero_identificacion: str
    tipo_identificacion: str
    nombres: str
    apellidos: str
    roles: list[str]
