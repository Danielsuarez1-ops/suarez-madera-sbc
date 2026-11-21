# Sistema experto para clasificar incidentes de soporte TI

Proyecto final de **Inteligencia Artificial II**, Fundación Universitaria Los Libertadores.

Integrantes:
- Edison Daniel Suárez
- Brayan Darío Madera

## De qué se trata

Es un sistema experto (sistema basado en conocimiento) con una página web hecha en Streamlit. Sirve para clasificar los incidentes que llegan a una mesa de ayuda de TI.

La persona de soporte marca lo que está pasando con el incidente (si el servicio está caído, si es una falla del equipo, si afecta a varios usuarios, etc.) y el sistema le dice:

- **Qué tipo de incidente es:** seguridad, hardware, acceso o software.
- **Qué tanto afecta:** impacto alto, medio o bajo.
- **Con qué prioridad se debe atender:** crítica, alta, media o baja, con el tiempo de atención.
- **Qué hacer** y si hay que avisarle al coordinador.

También explica cómo llegó a esa respuesta: qué reglas usó, en qué orden, y un botón "¿Por qué?" para ver la cadena completa.

La base de conocimiento tiene **12 predicados** y **15 reglas**. El motor usa **encadenamiento hacia adelante**.

## Estructura del proyecto

```
suarez-madera-sbc/
├── README.md
├── requirements.txt
├── src/
│   ├── base_conocimiento.py   # predicados, reglas y tablas de recomendaciones
│   ├── motor_inferencia.py    # encadenamiento hacia adelante y explicaciones
│   ├── casos_prueba.py        # casos precargados (para la demo y las pruebas)
│   └── app.py                 # página web en Streamlit
├── docs/
│   ├── documentacion_tecnica.pdf   (y .docx editable)
│   └── manual_usuario.pdf          (y .docx editable)
└── tests/
    ├── casos_prueba.md        # tabla con los casos de prueba
    └── probar_casos.py        # script que corre todos los casos
```

No hay carpetas `templates/` ni `static/` porque esas solo se usan con Flask. Con Streamlit no hacen falta.

## Instalación

Se necesita **Python 3.8 o superior**.

1. Descargar el proyecto:
   ```
   git clone https://github.com/Danielsuarez1-ops/suarez-madera-sbc.git
   cd suarez-madera-sbc
   ```
2. (Opcional) Crear un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate        # en Windows
   source venv/bin/activate     # en Mac/Linux
   ```
3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Cómo ejecutarlo

Desde la carpeta principal del proyecto:

```
streamlit run src/app.py
```

Se abre solo en el navegador en `http://localhost:8501`. Si no se abre, copiar esa dirección en el navegador.

Para correr los casos de prueba sin abrir la página:

```
python tests/probar_casos.py
```

Debe salir `10 de 10 casos salieron bien`.

## Cómo se usa (rápido)

1. Marcar las casillas de lo que está pasando y a quién afecta, o cargar un caso de prueba desde la barra de la izquierda.
2. Darle **Clasificar incidente**.
3. Ver el resultado (prioridad, impacto, categoría y qué hacer).
4. Bajar a **Explicación** para ver las reglas usadas y darle **¿Por qué?** para ver el detalle.
5. **Limpiar todo** para empezar otro incidente.

El manual completo está en `docs/manual_usuario.pdf`.

## Video de demo

Link: _(pendiente)_
