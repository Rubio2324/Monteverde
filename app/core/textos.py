import re
import unicodedata


def normalizar(texto) -> str:
    """Minusculas, sin tildes ni signos, con espacios simples."""
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9 ]", " ", texto.lower())
    return re.sub(r"\s+", " ", texto).strip()


def solo_digitos(texto) -> str:
    return re.sub(r"\D", "", str(texto or ""))


def dividir_nombre(completo: str) -> tuple[str, str]:
    """Heuristica: 2 nombres y el resto apellidos si hay 4 o mas palabras."""
    partes = completo.split()
    if len(partes) == 1:
        return partes[0], "-"
    if len(partes) == 2:
        return partes[0], partes[1]
    if len(partes) == 3:
        return partes[0], " ".join(partes[1:])
    return " ".join(partes[:2]), " ".join(partes[2:])
