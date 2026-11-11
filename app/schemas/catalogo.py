from pydantic import BaseModel


class ItemCatalogo(BaseModel):
    id: int
    nombre: str


class BarrioItem(ItemCatalogo):
    localidad: str | None


class CatalogosOut(BaseModel):
    barrios: list[BarrioItem]
    eps: list[ItemCatalogo]
    religiones: list[ItemCatalogo]
    instituciones: list[ItemCatalogo]
    programas: list[ItemCatalogo]