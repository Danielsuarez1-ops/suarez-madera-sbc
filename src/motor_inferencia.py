# motor_inferencia.py
# Este es el "cerebro" del sistema experto. Toma los hechos que marca el
# usuario, revisa las reglas una por una y va agregando hechos nuevos
# hasta que ya no se puede sacar nada mas (encadenamiento hacia adelante).

import logging

from base_conocimiento import PREDICADOS, CUALQUIERA, ORDEN_PRIORIDAD

# Logging: va dejando registro de lo que hace el motor (sale en la consola)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [motor] %(message)s')
logger = logging.getLogger('motor')

# Por si acaso: numero maximo de vueltas para no quedar en un ciclo infinito
MAX_VUELTAS = 50

# Solo para que los textos se vean bien escritos (con tildes)
BONITO = {'categoria': 'la categoría', 'impacto': 'el impacto', 'prioridad': 'la prioridad',
          'critica': 'crítica'}


def bonito(palabra):
    return BONITO.get(palabra, palabra)


# ---------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------

def texto_hecho(predicado, valor):
    """Convierte un hecho en un texto que se pueda leer facil."""
    descripcion = PREDICADOS.get(predicado, predicado)
    if valor is True:
        return descripcion
    if valor is False:
        return 'NO es cierto que ' + descripcion[0].lower() + descripcion[1:]
    if valor == CUALQUIERA:
        return 'ya se sabe ' + bonito(predicado)
    return f'{bonito(predicado)} es {bonito(valor)}'


def minuscula(texto):
    """Pone la primera letra en minuscula (para que las frases se lean seguidas)."""
    if texto.startswith('NO '):
        return texto
    return texto[0].lower() + texto[1:] if texto else texto


def se_cumple(condicion, hechos):
    """Revisa si UNA condicion se cumple con los hechos que tenemos.

    hechos es un diccionario: {(predicado, valor): certeza}
    """
    predicado, valor = condicion

    if valor is False:
        # Negacion: se cumple si el hecho NO esta marcado como verdadero
        return (predicado, True) not in hechos

    if valor == CUALQUIERA:
        # Se cumple si el predicado tiene cualquier valor
        for (p, v) in hechos:
            if p == predicado:
                return True
        return False

    # Caso normal: el hecho tiene que estar tal cual
    return (predicado, valor) in hechos


def certeza_de(condicion, hechos):
    """Devuelve la certeza de una condicion que ya se cumplio."""
    predicado, valor = condicion
    if valor is False:
        return 1.0  # una negacion la tomamos como segura
    if valor == CUALQUIERA:
        return max(c for (p, v), c in hechos.items() if p == predicado)
    return hechos[(predicado, valor)]


# ---------------------------------------------------------------
# Motor de inferencia
# ---------------------------------------------------------------

def encadenamiento_adelante(base_conocimiento, hechos_iniciales, traza=None):
    """Aplica encadenamiento hacia adelante.

    base_conocimiento: la lista de REGLAS
    hechos_iniciales: diccionario {predicado: True/False} con lo que marco el usuario
    traza: lista opcional donde se van guardando los pasos (para mostrarlos en la pagina)

    Returns: (hechos_finales, reglas_aplicadas)
        hechos_finales: {(predicado, valor): certeza}
        reglas_aplicadas: lista en orden con {'regla', 'certeza', 'vuelta', 'nuevo'}
    """
    if traza is None:
        traza = []

    def anotar(mensaje):
        logger.info(mensaje)
        traza.append(mensaje)

    # 1. Pasamos los hechos del usuario a la memoria de trabajo.
    #    Solo guardamos los que son verdaderos (lo que no esta, se toma como falso).
    hechos = {}
    for predicado, valor in hechos_iniciales.items():
        if valor:
            hechos[(predicado, True)] = 1.0
    anotar(f'Inicio: {len(hechos)} hechos marcados por el usuario')

    reglas_aplicadas = []
    ya_usadas = set()   # cada regla se usa una sola vez (asi no se repite ni se cicla)
    vuelta = 0

    # 2. Vamos dando vueltas por todas las reglas hasta que no salga nada nuevo
    while True:
        vuelta += 1
        if vuelta > MAX_VUELTAS:
            anotar(f'ALERTA: se llego a {MAX_VUELTAS} vueltas, se detiene para evitar un ciclo infinito')
            break

        anotar(f'--- Vuelta {vuelta} ---')
        se_aplico_alguna = False

        for regla in base_conocimiento:
            nombre = regla['nombre']
            if nombre in ya_usadas:
                continue

            # La regla se dispara solo si TODAS sus condiciones se cumplen
            if all(se_cumple(c, hechos) for c in regla['condiciones']):
                # Certeza = certeza de la regla x la condicion menos segura
                certeza_cond = min(certeza_de(c, hechos) for c in regla['condiciones'])
                certeza = round(regla['certeza'] * certeza_cond, 2)

                conclusion = regla['conclusion']
                nuevo = conclusion not in hechos
                if nuevo:
                    hechos[conclusion] = certeza
                    anotar(f'{nombre} se cumple -> se agrega "{texto_hecho(*conclusion)}" (certeza {certeza:.0%})')
                else:
                    # Ya lo sabiamos por otra regla: se deja la certeza mas alta
                    hechos[conclusion] = max(hechos[conclusion], certeza)
                    anotar(f'{nombre} se cumple -> confirma "{texto_hecho(*conclusion)}" que ya se sabia')

                ya_usadas.add(nombre)
                reglas_aplicadas.append({
                    'regla': regla,
                    'certeza': certeza,
                    'vuelta': vuelta,
                    'nuevo': nuevo,
                })
                se_aplico_alguna = True

        if not se_aplico_alguna:
            anotar(f'En la vuelta {vuelta} no se aplicó ninguna regla nueva. Fin.')
            break

    if not reglas_aplicadas:
        anotar('No se pudo aplicar ninguna regla: no hay conclusión con estos datos.')

    return hechos, reglas_aplicadas


def obtener_resultado(hechos):
    """Saca de los hechos finales lo que se le muestra al usuario.

    Si salieron varias prioridades, se deja la mas alta.
    Returns: diccionario con categorias, impacto, prioridad, escalar (o None si no hay)
    """
    categorias = [(v, c) for (p, v), c in hechos.items() if p == 'categoria']
    impactos = [(v, c) for (p, v), c in hechos.items() if p == 'impacto']
    prioridades = [(v, c) for (p, v), c in hechos.items() if p == 'prioridad']

    if not prioridades:
        return None  # no hubo conclusion

    # La prioridad mas alta segun ORDEN_PRIORIDAD
    prioridad = max(prioridades, key=lambda x: ORDEN_PRIORIDAD.index(x[0]))

    return {
        'categorias': categorias,
        'impacto': impactos[0] if impactos else None,
        'prioridad': prioridad,
        'todas_prioridades': [v for v, c in prioridades],
        'escalar': ('escalar_coordinador', True) in hechos,
    }


# ---------------------------------------------------------------
# Explicaciones
# ---------------------------------------------------------------

def explicar_razonamiento(reglas_aplicadas):
    """Genera una explicacion en texto de todas las reglas que se usaron, en orden.

    Returns: texto explicativo
    """
    if not reglas_aplicadas:
        return ('No se aplicó ninguna regla. Con los datos marcados el sistema '
                'no tiene cómo saber qué tipo de incidente es.')

    lineas = []
    for i, item in enumerate(reglas_aplicadas, start=1):
        regla = item['regla']
        condiciones = ' Y '.join(minuscula(texto_hecho(p, v)) for p, v in regla['condiciones'])
        conclusion = minuscula(texto_hecho(*regla['conclusion']))
        extra = '' if item['nuevo'] else ' (ya se sabía, esta regla lo confirma)'
        lineas.append(
            f"{i}. [{regla['nombre']} - {regla['grupo']}] Como se cumple: {condiciones}. "
            f"Entonces: {conclusion}. Certeza {item['certeza']:.0%}{extra}."
        )
    return '\n'.join(lineas)


def porque(conclusion, hechos_iniciales, reglas_aplicadas, nivel=0, vistos=None):
    """Explica por que se llego a una conclusion (va hacia atras por la cadena).

    conclusion: (predicado, valor), ej. ('prioridad', 'critica')
    Returns: cadena de razonamiento como texto (con sangria por niveles)
    """
    if vistos is None:
        vistos = set()
    sangria = '    ' * nivel
    predicado, valor = conclusion

    # Caso 1: es un hecho que marco el usuario
    if valor is True and hechos_iniciales.get(predicado):
        return f'{sangria}- "{texto_hecho(predicado, valor)}": lo marcó el usuario.'

    # Caso 2: es una negacion (el usuario no lo marco)
    if valor is False:
        return f'{sangria}- "{PREDICADOS[predicado]}": el usuario NO lo marcó.'

    # Caso 3: se saco con reglas. Buscamos que reglas lo concluyeron
    if conclusion in vistos:
        return f'{sangria}- "{texto_hecho(predicado, valor)}": ya explicado arriba.'
    vistos.add(conclusion)

    que_reglas = [r for r in reglas_aplicadas if r['regla']['conclusion'] == conclusion]

    # Para CUALQUIERA buscamos cualquier regla que haya dado ese predicado
    if valor == CUALQUIERA:
        que_reglas = [r for r in reglas_aplicadas if r['regla']['conclusion'][0] == predicado]
        if not que_reglas:
            return f'{sangria}- No se sabe {bonito(predicado)}.'
        partes = [f'{sangria}- Ya se sabía {bonito(predicado)}:']
        for r in que_reglas:
            partes.append(porque(r['regla']['conclusion'], hechos_iniciales,
                                 reglas_aplicadas, nivel + 1, vistos))
        return '\n'.join(partes)

    if not que_reglas:
        return f'{sangria}- "{texto_hecho(predicado, valor)}": no se pudo concluir con los datos que hay.'

    partes = []
    for r in que_reglas:
        regla = r['regla']
        partes.append(f'{sangria}- "{texto_hecho(predicado, valor)}" porque se cumplió la regla '
                      f'{regla["nombre"]} ({regla["descripcion"]}), que necesita:')
        for cond in regla['condiciones']:
            partes.append(porque(cond, hechos_iniciales, reglas_aplicadas, nivel + 1, vistos))
    return '\n'.join(partes)
