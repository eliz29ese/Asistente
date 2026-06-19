from text_analyzer import analizar_texto

OBJETOS = [
    "destornillador",
    "alicate",
    "martillo",
    "llave",
    "tornillo",
    "tuerca",
]


def interpretar_orden(texto):
    analisis = analizar_texto(texto)

    texto_limpio = analisis["texto"]
    palabras = analisis["palabras"]

    objeto = extraer_objeto(texto_limpio)

    if es_comando_movimiento(texto_limpio):
        return interpretar_movimiento(texto_limpio)

    if objeto is not None:
        return interpretar_tarea_con_objeto(texto_limpio, objeto)

    if es_comando_tarea_sin_objeto(texto_limpio):
        return interpretar_tarea_sin_objeto(texto_limpio)

    return {
        "tipo": "desconocida",
        "accion": None,
        "objeto": None,
        "texto": texto_limpio,
        "palabras": palabras,
    }


def extraer_objeto(texto):
    for objeto in OBJETOS:
        if objeto in texto:
            return objeto

    return None


def es_comando_movimiento(texto):
    comandos = [
        "avanza",
        "adelante",
        "ve adelante",
        "retrocede",
        "atras",
        "ve atras",
        "izquierda",
        "gira izquierda",
        "gira a la izquierda",
        "derecha",
        "gira derecha",
        "gira a la derecha",
        "detente",
        "para",
        "alto",
        "abre pinza",
        "abre la pinza",
        "cierra pinza",
        "cierra la pinza",
        "sube brazo",
        "sube el brazo",
        "baja brazo",
        "baja el brazo",
    ]

    return texto in comandos


def interpretar_movimiento(texto):
    if texto in ["avanza", "adelante", "ve adelante"]:
        accion = "avanzar"

    elif texto in ["retrocede", "atras", "ve atras"]:
        accion = "retroceder"

    elif texto in ["izquierda", "gira izquierda", "gira a la izquierda"]:
        accion = "girar_izquierda"

    elif texto in ["derecha", "gira derecha", "gira a la derecha"]:
        accion = "girar_derecha"

    elif texto in ["detente", "para", "alto"]:
        accion = "detener"

    elif texto in ["abre pinza", "abre la pinza"]:
        accion = "abrir_pinza"

    elif texto in ["cierra pinza", "cierra la pinza"]:
        accion = "cerrar_pinza"

    elif texto in ["sube brazo", "sube el brazo"]:
        accion = "subir_brazo"

    elif texto in ["baja brazo", "baja el brazo"]:
        accion = "bajar_brazo"

    else:
        accion = None

    return {
        "tipo": "movimiento",
        "accion": accion,
        "objeto": None,
        "texto": texto,
    }


def interpretar_tarea_con_objeto(texto, objeto):
    if contiene_alguna(texto, ["pasame", "traeme", "trae", "dame"]):
        accion = "buscar_y_entregar"

    elif contiene_alguna(texto, ["busca", "buscar", "encuentra", "localiza"]):
        accion = "buscar_objeto"

    elif contiene_alguna(texto, ["recoge", "recoger", "agarra", "coge", "toma"]):
        accion = "recoger_objeto"

    elif contiene_alguna(texto, ["lleva", "transporta"]):
        accion = "llevar_objeto"

    else:
        accion = "buscar_y_entregar"

    return {
        "tipo": "tarea",
        "accion": accion,
        "objeto": objeto,
        "texto": texto,
    }


def es_comando_tarea_sin_objeto(texto):
    comandos = [
        "entrega",
        "entrega el objeto",
        "suelta",
        "suelta el objeto",
        "lleva el objeto",
        "ven aqui",
    ]

    return texto in comandos


def interpretar_tarea_sin_objeto(texto):
    if texto in ["entrega", "entrega el objeto", "suelta", "suelta el objeto"]:
        accion = "entregar_objeto"
        objeto = None

    elif texto in ["lleva el objeto", "ven aqui"]:
        accion = "llevar_objeto"
        objeto = "usuario"

    else:
        accion = None
        objeto = None

    return {
        "tipo": "tarea",
        "accion": accion,
        "objeto": objeto,
        "texto": texto,
    }


def contiene_alguna(texto, palabras):
    for palabra in palabras:
        if palabra in texto:
            return True

    return False


ACCIONES_ENTREGA = [
    "pasame",
    "pasar",
    "pasarme",
    "trae",
    "traeme",
    "dame",
    "alcanzame",
]
