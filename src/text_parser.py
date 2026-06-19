import re

from text_analyzer import analizar_texto

OBJETOS = [
    "destornillador",
    "alicate",
    "martillo",
    "llave",
    "tornillo",
    "tuerca",
]

# --- Verbos de movimiento, agrupados por accion final ---
VERBOS_MOVIMIENTO = {
    "avanzar": ["avanza", "avanzar", "adelante", "ve adelante"],
    "retroceder": ["retrocede", "retroceder", "atras", "ve atras"],
    "girar_izquierda": ["izquierda", "gira izquierda", "gira a la izquierda"],
    "girar_derecha": ["derecha", "gira derecha", "gira a la derecha"],
    "detener": ["detente", "para", "alto", "deten", "detener"],
    "abrir_pinza": ["abre pinza", "abre la pinza", "abrir pinza"],
    "cerrar_pinza": ["cierra pinza", "cierra la pinza", "cerrar pinza"],
    "subir_brazo": ["sube brazo", "sube el brazo", "subir brazo"],
    "bajar_brazo": ["baja brazo", "baja el brazo", "bajar brazo"],
}

# --- Verbos de tarea con objeto ---
VERBOS_TAREA_OBJETO = {
    "buscar_y_entregar": [
        "pasame",
        "pasar",
        "pasarme",
        "traeme",
        "trae",
        "dame",
        "alcanzame",
    ],
    "buscar_objeto": ["busca", "buscar", "encuentra", "localiza"],
    "recoger_objeto": ["recoge", "recoger", "agarra", "coge", "toma"],
    "llevar_objeto": ["lleva", "llevar", "transporta"],
}

# --- Verbos de tarea sin objeto explicito ---
VERBOS_TAREA_SIN_OBJETO = {
    "entregar_objeto": ["entrega", "entregar", "suelta", "soltar"],
    "llevar_objeto_usuario": ["ven aqui", "ven", "lleva el objeto"],
}


# Lista de diagnosticos de la ULTIMA llamada a interpretar_orden(), al estilo
# de LogLexer.lexer_errors / self.parser_errors en el parser de logs.
# No son errores fatales: son trazas de por que se tomo cada decision,
# pensadas para depurar ambiguedades sin tener que poner breakpoints.
ultimo_diagnostico = []


def _palabra_en_texto(palabra_o_frase, texto):
    """Coincidencia por palabra/frase completa, no por substring (evita 'oye' en 'oyente')."""
    patron = r"\b" + re.escape(palabra_o_frase) + r"\b"
    return re.search(patron, texto) is not None


def _buscar_en_mapa(texto, mapa):
    """
    Busca en un mapa {accion: [variantes]} cual accion calza con el texto.
    Devuelve (accion, variante_encontrada) o (None, None) si no hay match.
    Si hay varias variantes que calzan, gana la mas larga (mas especifica),
    igual que la regla de "maximal munch" que se usa en lexers reales:
    ante varias coincidencias posibles, gana la mas larga/especifica.
    """
    mejor_accion = None
    mejor_variante = None
    mejor_longitud = -1

    for accion, variantes in mapa.items():
        for variante in variantes:
            if _palabra_en_texto(variante, texto) and len(variante) > mejor_longitud:
                mejor_accion = accion
                mejor_variante = variante
                mejor_longitud = len(variante)

    return mejor_accion, mejor_variante


def extraer_objeto(texto):
    for objeto in OBJETOS:
        if _palabra_en_texto(objeto, texto):
            return objeto
    return None


def interpretar_orden(texto):
    """
    Interpreta una orden de texto y devuelve un diccionario con tipo/accion/objeto.

    Ademas, deja un registro de diagnostico en la variable de modulo
    `ultimo_diagnostico` (lista de strings) explicando que señales se
    detectaron y por que se eligio esa interpretacion. Se reinicia en
    cada llamada, igual que lexer_errors se reinicia en __init__ del lexer.
    """
    global ultimo_diagnostico
    ultimo_diagnostico = []

    analisis = analizar_texto(texto)
    texto_limpio = analisis["texto"]
    palabras = analisis["palabras"]

    if texto_limpio == "":
        ultimo_diagnostico.append(
            f"El texto quedo vacio tras normalizar y quitar ruido "
            f"(entrada original: {texto!r})."
        )

    # 1. Detectamos TODAS las señales presentes, sin decidir todavia.
    objeto = extraer_objeto(texto_limpio)
    accion_movimiento, variante_mov = _buscar_en_mapa(texto_limpio, VERBOS_MOVIMIENTO)
    accion_tarea_obj, variante_tarea = _buscar_en_mapa(
        texto_limpio, VERBOS_TAREA_OBJETO
    )
    accion_tarea_sin_obj, variante_sin_obj = _buscar_en_mapa(
        texto_limpio, VERBOS_TAREA_SIN_OBJETO
    )

    if objeto is not None:
        ultimo_diagnostico.append(f"Objeto detectado: {objeto!r}.")
    if accion_movimiento is not None:
        ultimo_diagnostico.append(
            f"Verbo de movimiento detectado: {variante_mov!r} -> {accion_movimiento!r}."
        )
    if accion_tarea_obj is not None:
        ultimo_diagnostico.append(
            f"Verbo de tarea-con-objeto detectado: {variante_tarea!r} -> {accion_tarea_obj!r}."
        )
    if accion_tarea_sin_obj is not None:
        ultimo_diagnostico.append(
            f"Verbo de tarea-sin-objeto detectado: {variante_sin_obj!r} -> {accion_tarea_sin_obj!r}."
        )

    # 2. Reglas de prioridad EXPLICITAS (esto es lo que antes dependia
    #    accidentalmente del orden de los if y de que tan estricta era cada
    #    comparacion). Aqui se documenta el criterio real:
    #
    #    a) Si hay un objeto Y un verbo de tarea con objeto -> tarea con objeto.
    #       Esto es lo mas especifico e inequivoco: "trae el martillo".
    #    b) Si hay un objeto pero NINGUN verbo reconocido -> tarea con objeto,
    #       usando "buscar_y_entregar" como accion por defecto (igual que antes,
    #       pero ahora queda explicito que fue un default, no una deteccion real).
    #    c) Si NO hay objeto pero hay un verbo de movimiento -> movimiento.
    #       Ejemplo: "avanza", "gira a la izquierda".
    #    d) Si hay objeto Y verbo de movimiento a la vez (caso ambiguo, ej.
    #       "avanza hacia el martillo") -> gana el objeto, porque interpretamos
    #       que el usuario quiere que el robot interactue con algo concreto,
    #       no que simplemente se mueva. Decision de diseño explicita.
    #    e) Si no hay objeto ni verbo de movimiento, pero hay verbo de tarea
    #       sin objeto -> tarea sin objeto ("entrega", "ven aqui").
    #    f) Si nada calza -> desconocida.

    if objeto is not None:
        if accion_movimiento is not None:
            ultimo_diagnostico.append(
                f"Ambiguedad: hay objeto ({objeto!r}) y verbo de movimiento "
                f"({variante_mov!r}) a la vez. Gana el objeto por regla de prioridad (d)."
            )
        accion = (
            accion_tarea_obj if accion_tarea_obj is not None else "buscar_y_entregar"
        )
        if accion_tarea_obj is None:
            ultimo_diagnostico.append(
                f"Objeto {objeto!r} sin verbo de tarea reconocido. "
                "Se usa 'buscar_y_entregar' por defecto (regla b)."
            )
        ultimo_diagnostico.append(
            f"Decision final: tarea con objeto -> accion {accion!r}."
        )
        return {
            "tipo": "tarea",
            "accion": accion,
            "objeto": objeto,
            "texto": texto_limpio,
            "accion_fue_detectada": accion_tarea_obj is not None,
        }

    if accion_movimiento is not None:
        ultimo_diagnostico.append(
            f"Decision final: movimiento -> {accion_movimiento!r} (regla c)."
        )
        return {
            "tipo": "movimiento",
            "accion": accion_movimiento,
            "objeto": None,
            "texto": texto_limpio,
        }

    if accion_tarea_sin_obj is not None:
        objeto_resultante = (
            "usuario" if accion_tarea_sin_obj == "llevar_objeto_usuario" else None
        )
        accion_resultante = (
            "llevar_objeto"
            if accion_tarea_sin_obj == "llevar_objeto_usuario"
            else accion_tarea_sin_obj
        )
        ultimo_diagnostico.append(
            f"Decision final: tarea sin objeto -> {accion_resultante!r} (regla e)."
        )
        return {
            "tipo": "tarea",
            "accion": accion_resultante,
            "objeto": objeto_resultante,
            "texto": texto_limpio,
        }

    ultimo_diagnostico.append(
        "Decision final: ninguna señal reconocida. Tipo 'desconocida' (regla f)."
    )
    return {
        "tipo": "desconocida",
        "accion": None,
        "objeto": None,
        "texto": texto_limpio,
        "palabras": palabras,
    }


if __name__ == "__main__":
    import json

    casos = [
        "avanza",
        "gira a la izquierda",
        "pasame el destornillador por favor",
        "avanza hacia el martillo",
        "busca la llave",
        "lleva el destornillador a la mesa izquierda",
        "ven aqui",
        "entrega el objeto",
        "hazme un cafe",
        "tornillo",
        "para el destornillador",
        "para",
    ]

    for c in casos:
        r = interpretar_orden(c)
        print(f"\nENTRADA: {c!r}")
        print(f"RESULTADO: {json.dumps(r, ensure_ascii=False)}")
        print("DIAGNOSTICO:")
        for linea in ultimo_diagnostico:
            print(f"  - {linea}")
