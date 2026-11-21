# app.py
# Pagina web del sistema experto, hecha con Streamlit.
# Para correrla (desde la carpeta principal del proyecto):
#     streamlit run src/app.py

import time
import streamlit as st

from base_conocimiento import (REGLAS, PREDICADOS, ENTRADAS, ENTRADAS_QUE_PASA,
                               ENTRADAS_A_QUIEN, TIEMPO_ATENCION, QUE_HACER)
from motor_inferencia import (encadenamiento_adelante, explicar_razonamiento,
                              porque, obtener_resultado, texto_hecho, bonito)
from casos_prueba import CASOS

st.set_page_config(page_title='Clasificador de incidentes TI', page_icon='🛠️')


# ---------------------------------------------------------------
# Estado de la pagina (Streamlit vuelve a correr todo el archivo en
# cada clic, por eso guardamos las cosas en st.session_state)
# ---------------------------------------------------------------
for entrada in ENTRADAS:
    if 'chk_' + entrada not in st.session_state:
        st.session_state['chk_' + entrada] = False
if 'resultado' not in st.session_state:
    st.session_state['resultado'] = None
if 'descripcion' not in st.session_state:
    st.session_state['descripcion'] = ''


def limpiar():
    """Deja todo en blanco."""
    for e in ENTRADAS:
        st.session_state['chk_' + e] = False
    st.session_state['descripcion'] = ''
    st.session_state['resultado'] = None


def cargar_caso():
    """Marca las casillas segun el caso de prueba que se escogio."""
    nombre = st.session_state['caso_elegido']
    caso = next(c for c in CASOS if f"Caso {c['id']}: {c['nombre']}" == nombre)
    for e in ENTRADAS:
        st.session_state['chk_' + e] = e in caso['hechos']
    st.session_state['descripcion'] = caso['nombre']
    st.session_state['resultado'] = None


def borrar_resultado():
    """Si cambian algo del formulario, el resultado anterior ya no sirve."""
    st.session_state['resultado'] = None


# ---------------------------------------------------------------
# Barra lateral: casos precargados y boton de limpiar
# ---------------------------------------------------------------
with st.sidebar:
    st.header('Casos de prueba')
    st.write('Escoge un caso para llenar el formulario rápido.')
    st.selectbox('Caso', [f"Caso {c['id']}: {c['nombre']}" for c in CASOS], key='caso_elegido')
    st.button('Cargar caso', on_click=cargar_caso, use_container_width=True)
    st.divider()
    st.button('Limpiar todo', on_click=limpiar, use_container_width=True)
    st.divider()
    st.caption(f'Base de conocimiento: {len(REGLAS)} reglas y {len(PREDICADOS)} predicados.')


# ---------------------------------------------------------------
# 1. Entrada de datos
# ---------------------------------------------------------------
st.title('Sistema experto para clasificar incidentes de soporte TI')
st.write('Marca lo que está pasando con el incidente y el sistema te dice qué tipo de '
         'incidente es, qué tanto afecta y con qué prioridad se debe atender.')

st.text_input('Descripción corta del incidente (opcional)', key='descripcion',
              placeholder='Ej: no abre el correo en el área de cartera')

st.subheader('¿Qué está pasando?')
for e in ENTRADAS_QUE_PASA:
    st.checkbox(PREDICADOS[e], key='chk_' + e, on_change=borrar_resultado)

st.subheader('¿A quién afecta?')
for e in ENTRADAS_A_QUIEN:
    st.checkbox(PREDICADOS[e], key='chk_' + e, on_change=borrar_resultado)

if st.button('Clasificar incidente', type='primary'):
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
if res is not None:
    st.divider()
    st.header('Resultado')
    resultado = obtener_resultado(res['hechos_finales'])

    if resultado is None:
        st.warning('No se pudo clasificar el incidente con los datos marcados. '
                   'Falta decir qué está pasando (servicio caído, falla del equipo, '
                   'problema de acceso o sospecha de seguridad).')
    else:
        prioridad, cert_prioridad = resultado['prioridad']
        texto = f"Prioridad {bonito(prioridad).upper()} ({cert_prioridad:.0%} de certeza)"
        if prioridad == 'critica':
            st.error(texto)
        elif prioridad == 'alta':
            st.warning(texto)
        elif prioridad == 'media':
            st.info(texto)
        else:
            st.success(texto)

        c1, c2, c3 = st.columns(3)
        c1.metric('Prioridad', bonito(prioridad).capitalize())
        if resultado['impacto']:
            impacto, cert_impacto = resultado['impacto']
            c2.metric('Impacto', impacto.capitalize())
            c2.caption(f'{cert_impacto:.0%} de certeza')
        c3.metric('Categorías', len(resultado['categorias']))

        st.subheader('Qué hacer')
        st.write(f"**Tiempo de atención:** {TIEMPO_ATENCION[prioridad]}")
        for categoria, cert in resultado['categorias']:
            st.write(f"**{categoria.capitalize()}** ({cert:.0%} de certeza): {QUE_HACER[categoria]}")
        if resultado['escalar']:
            st.write('**Avisar al coordinador de soporte**, porque es un incidente crítico.')
        if len(set(resultado['todas_prioridades'])) > 1:
            otras = ', '.join(bonito(p) for p in resultado['todas_prioridades'])
            st.caption(f'Las reglas dieron varias prioridades ({otras}); se deja la más alta.')

    # -----------------------------------------------------------
    # 3. Explicacion
    # -----------------------------------------------------------
    st.divider()
    st.header('Explicación')

    st.subheader('Reglas que se aplicaron (en orden)')
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

    st.subheader('Cadena de razonamiento')
    st.markdown(explicar_razonamiento(res['reglas_aplicadas']))

    # Boton "¿Por qué?"
    st.subheader('¿Por qué?')
    conclusiones = [h for h in res['hechos_finales'] if h[0] not in ENTRADAS]
    if conclusiones:
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

    with st.expander('Ver el log del motor (paso a paso)'):
        st.text('\n'.join(res['traza']))


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
