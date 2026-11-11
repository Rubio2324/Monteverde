class NoEncontrado(Exception):
    """El recurso no existe (404)."""


class Conflicto(Exception):
    """El recurso ya existe o choca con otro (409)."""


class ReglaNegocio(Exception):
    """Se incumple una regla de negocio (422)."""
