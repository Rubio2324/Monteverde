import enum


class Localidad(str, enum.Enum):
    Usaquen = "Usaquen"
    Chapinero = "Chapinero"
    Santa_Fe = "Santa_Fe"
    San_Cristobal = "San_Cristobal"
    Usme = "Usme"
    Tunjuelito = "Tunjuelito"
    Bosa = "Bosa"
    Kennedy = "Kennedy"
    Fontibon = "Fontibon"
    Engativa = "Engativa"
    Suba = "Suba"
    Barrios_Unidos = "Barrios_Unidos"
    Teusaquillo = "Teusaquillo"
    Los_Martires = "Los_Martires"
    Antonio_Narino = "Antonio_Narino"
    Puente_Aranda = "Puente_Aranda"
    La_Candelaria = "La_Candelaria"
    Rafael_Uribe_Uribe = "Rafael_Uribe_Uribe"
    Ciudad_Bolivar = "Ciudad_Bolivar"
    Sumapaz = "Sumapaz"


class EstadoProceso(str, enum.Enum):
    aspirante = "aspirante"
    admitido = "admitido"
    no_admitido = "no_admitido"
    matriculado = "matriculado"
    egresado = "egresado"
    retirado = "retirado"


class EstadoPersona(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
