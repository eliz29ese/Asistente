import re
import unicodedata


def quitar_tildes(texto):
    """Convierte 'café' en 'cafe' descomponiendo letra+acento y descartando el acento."""
    texto_normalizado = unicodedata.normalize("NFD", texto)

    texto_sin_tildes = "".join(
        letra
        for letra in texto_normalizado
        if unicodedata.category(letra)
        != "Mn"  # Mn = marca diacritica (tilde, dieresis, etc.)
    )

    return texto_sin_tildes


def normalizar_texto(texto):
    """
    Minusculas, sin tildes, sin puntuacion, sin espacios duplicados ni en los extremos.
    """
    texto = texto.lower().strip()
    texto = quitar_tildes(texto)

    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# IMPORTANTE: estas expresiones deben ir SIN tildes y en minusculas,
# porque quitar_ruido() se llama DESPUES de normalizar_texto() en analizar_texto().
#
# Ordenadas de mas especifica (frases largas) a menos especifica (palabras sueltas).
# Esto evita que una frase corta "consuma" parte de una frase larga antes de tiempo.
# Ejemplo: si "podrias" se quitara antes que "me podrias", quedaria un "me" suelto.
EXPRESIONES_RUIDO = [
    "me podrias",
    "me puedes",
    "necesito que",
    "quiero que",
    "por favor",
    "porfa",
    "podrias",
    "puedes",
    "oye",
    "robot",
]


def quitar_ruido(texto):
    """
    Elimina frases de cortesia/relleno usando limites de palabra (\\b).

    """
    for expresion in EXPRESIONES_RUIDO:
        patron = r"\b" + re.escape(expresion) + r"\b"
        texto = re.sub(patron, "", texto)

    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def analizar_texto(texto):
    texto = normalizar_texto(texto)
    texto = quitar_ruido(texto)

    palabras = texto.split()

    return {
        "texto": texto,
        "palabras": palabras,
    }


if __name__ == "__main__":
    casos = [
        "Oye robot, por favor pásame el destornillador.",
        "Me podrías traer el alicate?",
        "Necesito que gires a la derecha",
        "Robot, puedes avanzar?",
        "Porfa abre la pinza",
        "Quiero que busques el martillo",
        "PÁSAME    EL    DESTORNILLADOR!!!",
    ]

    for caso in casos:
        resultado = analizar_texto(caso)
        print(f"ENTRADA : {caso!r}")
        print(f"SALIDA  : {resultado['texto']!r}")
        print(f"PALABRAS: {resultado['palabras']}")
        print("-" * 50)
