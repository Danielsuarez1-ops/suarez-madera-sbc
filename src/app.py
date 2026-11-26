# app.py
# Pagina web del sistema experto, hecha con Streamlit.
# Para correrla (desde la carpeta principal del proyecto):
#     streamlit run src/app.py

import time
import unicodedata
import streamlit as st

from base_conocimiento import (REGLAS, PREDICADOS, ENTRADAS, ENTRADAS_QUE_PASA,
                               ENTRADAS_A_QUIEN, TIEMPO_ATENCION, QUE_HACER,
                               AYUDA, SIGNIFICADO_PRIORIDAD, PALABRAS_CLAVE)
from motor_inferencia import (encadenamiento_adelante, explicar_razonamiento,
                              porque, obtener_resultado, texto_hecho, bonito)
from casos_prueba import CASOS

st.set_page_config(page_title='Clasificador de incidentes TI', page_icon='🛠️')

# Colores de cada prioridad (para que se entienda de un vistazo)
COLOR = {'critica': '🔴', 'alta': '🟠', 'media': '🔵', 'baja': '🟢'}


# ---------------------------------------------------------------
# Estado de la pagina (Streamlit vuelve a correr todo el archivo en
# cada clic, por eso guardamos las cosas en st.session_state)
# ---------------------------------------------------------------
for entrada in ENTRADAS:
    if 'chk_' + entrada not in st.session_state:
        st.session_state['chk_' + entrada] = False
for clave, inicial in [('resultado', None), ('descripcion', ''), ('aviso_sugerencia', None)]:
    if clave not in st.session_state:
        st.session_state[clave] = inicial


def limpiar():
    """Deja todo en blanco."""
    for e in ENTRADAS:
        st.session_state['chk_' + e] = False
    st.session_state['descripcion'] = ''
    st.session_state['resultado'] = None
    st.session_state['aviso_sugerencia'] = None


def cargar_caso():
    """Marca las casillas segun el caso de prueba que se escogio."""
    nombre = st.session_state['caso_elegido']
    caso = next(c for c in CASOS if f"Caso {c['id']}: {c['nombre']}" == nombre)
    for e in ENTRADAS:
        st.session_state['chk_' + e] = e in caso['hechos']
    st.session_state['descripcion'] = caso['nombre']
    st.session_state['resultado'] = None
    st.session_state['aviso_sugerencia'] = None


def borrar_resultado():
    """Si cambian algo del formulario, el resultado anterior ya no sirve."""
    st.session_state['resultado'] = None


def sin_tildes(texto):
    """Pasa a minuscula y quita tildes, para buscar palabras mas facil."""
    texto = unicodedata.normalize('NFD', texto.lower())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')


def sugerir_casillas():
    """Lee la descripcion y marca las casillas que parecen aplicar.

    Solo es una ayuda: el usuario revisa y corrige antes de clasificar.
    """
    texto = sin_tildes(st.session_state['descripcion'])
    if not texto.strip():
        st.session_state['aviso_sugerencia'] = ('error', 'Primero escribe qué está pasando.')
        return

    encontradas = []
    for entrada, palabras in PALABRAS_CLAVE.items():
        if any(p in texto for p in palabras):
            encontradas.append(entrada)

    for e in ENTRADAS:
        st.session_state['chk_' + e] = e in encontradas
    st.session_state['resultado'] = None

    if encontradas:
        st.session_state['aviso_sugerencia'] = (
            'ok', f'Se marcaron {len(encontradas)} casillas según lo que escribiste. '
                  'Revísalas en el paso 2 y corrige si algo no aplica.')
    else:
        st.session_state['aviso_sugerencia'] = (
            'nada', 'No reconocí palabras conocidas en la descripción. '
                    'Marca las casillas a mano en el paso 2.')


# ---------------------------------------------------------------
# Barra lateral: ayuda, casos precargados y boton de limpiar
# ---------------------------------------------------------------
with st.sidebar:
    st.header('¿Cómo se usa?')
    st.markdown('1. Cuenta el problema o marca las casillas.\n'
                '2. Dale **Clasificar incidente**.\n'
                '3. Mira la prioridad y qué hacer.')

    st.divider()
    st.header('Casos de prueba')
    st.write('Ejemplos ya armados para probar rápido.')
    st.selectbox('Caso', [f"Caso {c['id']}: {c['nombre']}" for c in CASOS], key='caso_elegido')
    st.button('Cargar caso', on_click=cargar_caso, use_container_width=True)

    st.divider()
    st.button('Limpiar todo', on_click=limpiar, use_container_width=True)

    st.divider()
    st.subheader('¿Qué significa cada prioridad?')
    for p in ['critica', 'alta', 'media', 'baja']:
        st.markdown(f"{COLOR[p]} **{bonito(p).capitalize()}:** {SIGNIFICADO_PRIORIDAD[p]}")

    st.divider()
    st.caption(f'Base de conocimiento: {len(REGLAS)} reglas y {len(PREDICADOS)} predicados.')


# ---------------------------------------------------------------
# 1. Entrada de datos
# ---------------------------------------------------------------
st.title('Clasificador de incidentes de soporte TI')
st.write('Este sistema experto te ayuda a saber **qué tan urgente** es un incidente, '
         '**de qué tipo** es y **qué hacer**. Sirve para cualquier problema, no solo para '
         'los casos de prueba.')

# --- Paso 1 ---
st.subheader('Paso 1. Cuenta qué pasa (opcional)')
st.text_area('Describe el problema con tus palabras',
             key='descripcion', height=80,
             placeholder='Ej: a todo el piso de cartera no le abre el sistema de facturación')
st.button('Sugerir casillas con lo que escribí', on_click=sugerir_casillas)

aviso = st.session_state['aviso_sugerencia']
if aviso:
    tipo, mensaje = aviso
    if tipo == 'ok':
        st.success(mensaje)
    elif tipo == 'nada':
        st.warning(mensaje)
    else:
        st.error(mensaje)
st.caption('Si prefieres, sáltate este paso y marca las casillas directamente.')

# --- Paso 2 ---
st.subheader('Paso 2. Marca lo que aplica')
st.caption('Pasa el mouse por el signo (?) de cada opción para ver ejemplos.')

st.markdown('**¿Qué está pasando?** (marca por lo menos una)')
for e in ENTRADAS_QUE_PASA:
    st.checkbox(PREDICADOS[e], key='chk_' + e, help=AYUDA[e], on_change=borrar_resultado)

st.markdown('**¿A quién afecta?**')
for e in ENTRADAS_A_QUIEN:
    st.checkbox(PREDICADOS[e], key='chk_' + e, help=AYUDA[e], on_change=borrar_resultado)

marcadas = sum(st.session_state['chk_' + e] for e in ENTRADAS)
st.caption(f'Llevas {marcadas} de {len(ENTRADAS)} opciones marcadas.')

# --- Paso 3 ---
st.subheader('Paso 3. Clasifica')
if st.button('Clasificar incidente', type='primary', use_container_width=True):
    hechos_iniciales = {e: st.session_state['chk_' + e] for e in ENTRADAS}

    # Validacion basica: que haya marcado algo
    if not any(hechos_iniciales.values()):
        st.error('Marca por lo menos una opción antes de clasificar.')
    else:
        with st.spinner('Revisando las reglas...'):
            time.sleep(0.4)  # solo para que se alcance a ver que esta procesando
            traza = []
            hechos_finales, reglas_aplicadas = encadenamiento_adelante(REGLAS, hechos_iniciales, traza)
        st.session_state['resultado'] = {
            'hechos_iniciales': hechos_iniciales,
            'hechos_finales': hechos_finales,
            'reglas_aplicadas': reglas_aplicadas,
            'traza': traza,
        }


# ---------------------------------------------------------------
# 2. Resultados
# ---------------------------------------------------------------
res = st.session_state['resultado']
resultado = None
if res is not None:
    st.divider()
    st.header('Resultado')
    resultado = obtener_resultado(res['hechos_finales'])

    if resultado is None:
        st.warning('No se pudo clasificar el incidente con los datos marcados. '
                   'Falta decir qué está pasando (servicio caído, falla del equipo, '
                   'problema de acceso o sospecha de seguridad).')
        st.write('👉 Vuelve al **paso 2** y marca por lo menos una opción de "¿Qué está pasando?".')
    else:
        prioridad, cert_prioridad = resultado['prioridad']
        nombres_cat = [c for c, _ in resultado['categorias']]

        # Mensaje principal, grande y con color
        texto = (f"{COLOR[prioridad]} Prioridad {bonito(prioridad).upper()} — "
                 f"{SIGNIFICADO_PRIORIDAD[prioridad]} ({cert_prioridad:.0%} de certeza)")
        if prioridad == 'critica':
            st.error(texto)
        elif prioridad == 'alta':
            st.warning(texto)
        elif prioridad == 'media':
            st.info(texto)
        else:
            st.success(texto)

        # Resumen en una frase
        impacto_txt = resultado['impacto'][0] if resultado['impacto'] else 'sin calcular'
        st.markdown(f"**En pocas palabras:** es un incidente de **{' y '.join(nombres_cat)}**, "
                    f"con impacto **{impacto_txt}** para la empresa. "
                    f"{TIEMPO_ATENCION[prioridad]}.")

        c1, c2, c3 = st.columns(3)
        c1.metric('Prioridad', bonito(prioridad).capitalize())
        if resultado['impacto']:
            impacto, cert_impacto = resultado['impacto']
            c2.metric('Impacto', impacto.capitalize())
            c2.caption(f'{cert_impacto:.0%} de certeza')
        c3.metric('Categorías', len(resultado['categorias']))
        c3.caption(', '.join(c.capitalize() for c in nombres_cat))

        st.subheader('Qué hacer ahora')
        pasos = [f"**Tiempo de atención:** {TIEMPO_ATENCION[prioridad]}"]
        for categoria, cert in resultado['categorias']:
            pasos.append(f"**{categoria.capitalize()}** ({cert:.0%} de certeza): {QUE_HACER[categoria]}")
        if resultado['escalar']:
            pasos.append('**Avisar al coordinador de soporte**, porque es un incidente crítico.')
        st.markdown('\n'.join(f'{i}. {p}' for i, p in enumerate(pasos, start=1)))

        if len(set(resultado['todas_prioridades'])) > 1:
            otras = ', '.join(bonito(p) for p in resultado['todas_prioridades'])
            st.caption(f'Las reglas dieron varias prioridades ({otras}); se deja la más alta.')
        st.caption('La certeza es qué tan seguro está el sistema de cada conclusión (100 % = totalmente seguro).')

    # -----------------------------------------------------------
    # 3. Explicacion
    # -----------------------------------------------------------
    st.divider()
    st.header('¿Cómo llegó a esta respuesta?')
    st.write('Aquí puedes ver qué reglas usó el sistema y en qué orden.')

    tab_reglas, tab_cadena, tab_log = st.tabs(['Reglas que se aplicaron',
                                               'Cadena de razonamiento',
                                               'Log del motor'])
    with tab_reglas:
        if res['reglas_aplicadas']:
            st.table([{
                'Orden': i,
                'Regla': r['regla']['nombre'],
                'Grupo': r['regla']['grupo'],
                'Qué dice': r['regla']['descripcion'],
                'Certeza': f"{r['certeza']:.0%}",
            } for i, r in enumerate(res['reglas_aplicadas'], start=1)])
        else:
            st.write('Ninguna.')
    with tab_cadena:
        st.markdown(explicar_razonamiento(res['reglas_aplicadas']))
    with tab_log:
        st.caption('Lo que hizo el motor paso a paso (vuelta por vuelta).')
        st.text('\n'.join(res['traza']))

    # Boton "¿Por qué?"
    st.subheader('¿Por qué?')
    conclusiones = [h for h in res['hechos_finales'] if h[0] not in ENTRADAS]
    if conclusiones:
        st.write('Escoge una conclusión y el sistema te explica de dónde salió.')
        # Por defecto sale seleccionada la prioridad final (lo mas importante)
        inicio = 0
        if resultado is not None and ('prioridad', resultado['prioridad'][0]) in conclusiones:
            inicio = conclusiones.index(('prioridad', resultado['prioridad'][0]))
        elegida = st.selectbox('Escoge una conclusión', conclusiones, index=inicio,
                               format_func=lambda h: texto_hecho(*h))
        if st.button('¿Por qué?'):
            st.markdown(porque(elegida, res['hechos_iniciales'], res['reglas_aplicadas']))
    else:
        st.write('No hay conclusiones para explicar.')

    st.divider()
    st.button('Clasificar otro incidente', on_click=limpiar)


# ---------------------------------------------------------------
# Base de conocimiento (para consultarla)
# ---------------------------------------------------------------
st.divider()
with st.expander('Ver todas las reglas del sistema'):
    st.table([{
        'Regla': r['nombre'],
        'Grupo': r['grupo'],
        'Qué dice': r['descripcion'],
        'Certeza': f"{r['certeza']:.0%}",
    } for r in REGLAS])
