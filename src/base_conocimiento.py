# base_conocimiento.py
# Aqui esta todo el "conocimiento" del sistema experto:
# los predicados (lo que el sistema sabe preguntar o concluir),
# las reglas (SI ... ENTONCES ...) y unas tablas de recomendaciones.
#
# Dominio: clasificacion y priorizacion de incidentes de soporte TI.
# La idea es que la mesa de ayuda marque lo que esta pasando con el
# incidente y el sistema diga que tipo de incidente es, que tanto
# afecta y con que prioridad se debe atender.


# ---------------------------------------------------------------
# 1. PREDICADOS
# ---------------------------------------------------------------
# Los primeros 8 son de ENTRADA (los marca el usuario, son Verdadero/Falso).
# Los ultimos 4 son DERIVADOS (los saca el motor usando las reglas).

PREDICADOS = {
    # --- Entrada: que esta pasando ---
    'servicio_caido': 'El programa o servicio no funciona para nada',
    'falla_equipo': 'Hay una falla física del equipo (PC, impresora, cable, etc.)',
    'problema_acceso': 'Es un problema de acceso (clave, usuario bloqueado, permisos)',
    'sospecha_seguridad': 'Hay sospecha de virus, correo falso o robo de información',

    # --- Entrada: a quien afecta ---
    'varios_usuarios': 'Afecta a más de un usuario',
    'sistema_critico': 'Es un sistema importante para el negocio (facturación, correo, ERP)',
    'usuario_vip': 'Lo reporta un gerente o directivo',
    'hay_alternativa': 'El usuario puede seguir trabajando de otra forma mientras tanto',

    # --- Derivados (conclusiones) ---
    'categoria': 'Tipo de incidente (seguridad, hardware, acceso o software)',
    'impacto': 'Qué tanto afecta a la empresa (alto, medio o bajo)',
    'prioridad': 'Qué tan rápido se debe atender (crítica, alta, media o baja)',
    'escalar_coordinador': 'Hay que avisarle al coordinador de soporte',
}

# Lista de los predicados de entrada, en el orden en que salen en el formulario
ENTRADAS_QUE_PASA = ['servicio_caido', 'falla_equipo', 'problema_acceso', 'sospecha_seguridad']
ENTRADAS_A_QUIEN = ['varios_usuarios', 'sistema_critico', 'usuario_vip', 'hay_alternativa']
ENTRADAS = ENTRADAS_QUE_PASA + ENTRADAS_A_QUIEN

# Valor especial para decir "con que tenga cualquier valor me sirve".
# Ej: ('categoria', CUALQUIERA) se cumple si ya se sabe la categoria, sea cual sea.
CUALQUIERA = '*'


# ---------------------------------------------------------------
# 2. REGLAS
# ---------------------------------------------------------------
# Cada regla tiene:
#   nombre, grupo, descripcion,
#   condiciones -> lista de (predicado, valor). TODAS se deben cumplir (es un Y).
#       valor True  = el hecho debe ser verdadero
#       valor False = el hecho NO debe ser verdadero
#       otro valor  = el predicado debe tener ese valor (ej. ('impacto', 'alto'))
#   conclusion -> (predicado, valor) que se agrega si la regla se cumple
#   certeza -> que tan seguros estamos de la regla (0 a 1)
#
# Ojo con la prioridad: cada regla dice la prioridad MINIMA que debe tener
# el incidente. Si varias reglas dan prioridades distintas, al final se deja
# la mas alta (en soporte es mejor pasarse que quedarse corto).

REGLAS = [
    # ----- Grupo 1: Categoria (que tipo de incidente es) -----
    {
        'nombre': 'R1',
        'grupo': 'Categoría',
        'descripcion': 'Si hay sospecha de virus o robo de información, es de seguridad',
        'condiciones': [('sospecha_seguridad', True)],
        'conclusion': ('categoria', 'seguridad'),
        'certeza': 0.95,
    },
    {
        'nombre': 'R2',
        'grupo': 'Categoría',
        'descripcion': 'Si hay una falla física del equipo, es de hardware',
        'condiciones': [('falla_equipo', True)],
        'conclusion': ('categoria', 'hardware'),
        'certeza': 0.90,
    },
    {
        'nombre': 'R3',
        'grupo': 'Categoría',
        'descripcion': 'Si es un tema de clave, usuario o permisos, es de acceso',
        'condiciones': [('problema_acceso', True)],
        'conclusion': ('categoria', 'acceso'),
        'certeza': 0.90,
    },
    {
        'nombre': 'R4',
        'grupo': 'Categoría',
        'descripcion': 'Si el servicio está caído y no es por el equipo, es de software',
        'condiciones': [('servicio_caido', True), ('falla_equipo', False)],
        'conclusion': ('categoria', 'software'),
        'certeza': 0.80,
    },

    # ----- Grupo 2: Impacto (que tanto afecta) -----
    # Solo se calcula si ya se sabe la categoria (si no sabemos que pasa, no clasificamos)
    {
        'nombre': 'R5',
        'grupo': 'Impacto',
        'descripcion': 'Si afecta a varios usuarios en un sistema crítico, el impacto es alto',
        'condiciones': [('categoria', CUALQUIERA), ('varios_usuarios', True), ('sistema_critico', True)],
        'conclusion': ('impacto', 'alto'),
        'certeza': 0.90,
    },
    {
        'nombre': 'R6',
        'grupo': 'Impacto',
        'descripcion': 'Si afecta a varios usuarios pero no es un sistema crítico, el impacto es medio',
        'condiciones': [('categoria', CUALQUIERA), ('varios_usuarios', True), ('sistema_critico', False)],
        'conclusion': ('impacto', 'medio'),
        'certeza': 0.85,
    },
    {
        'nombre': 'R7',
        'grupo': 'Impacto',
        'descripcion': 'Si afecta a un solo usuario, el impacto es bajo',
        'condiciones': [('categoria', CUALQUIERA), ('varios_usuarios', False)],
        'conclusion': ('impacto', 'bajo'),
        'certeza': 0.85,
    },

    # ----- Grupo 3: Prioridad (que tan rapido se atiende) -----
    {
        'nombre': 'R8',
        'grupo': 'Prioridad',
        'descripcion': 'Todo incidente de seguridad es de prioridad crítica',
        'condiciones': [('categoria', 'seguridad')],
        'conclusion': ('prioridad', 'critica'),
        'certeza': 0.95,
    },
    {
        'nombre': 'R9',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es alto y el servicio está caído, la prioridad es crítica',
        'condiciones': [('impacto', 'alto'), ('servicio_caido', True)],
        'conclusion': ('prioridad', 'critica'),
        'certeza': 0.95,
    },
    {
        'nombre': 'R10',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es alto, la prioridad es por lo menos alta',
        'condiciones': [('impacto', 'alto')],
        'conclusion': ('prioridad', 'alta'),
        'certeza': 0.85,
    },
    {
        'nombre': 'R11',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es medio y no hay otra forma de trabajar, la prioridad es alta',
        'condiciones': [('impacto', 'medio'), ('hay_alternativa', False)],
        'conclusion': ('prioridad', 'alta'),
        'certeza': 0.80,
    },
    {
        'nombre': 'R12',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es medio pero hay otra forma de trabajar, la prioridad es media',
        'condiciones': [('impacto', 'medio'), ('hay_alternativa', True)],
        'conclusion': ('prioridad', 'media'),
        'certeza': 0.80,
    },
    {
        'nombre': 'R13',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es bajo pero lo reporta un gerente, la prioridad es media',
        'condiciones': [('impacto', 'bajo'), ('usuario_vip', True)],
        'conclusion': ('prioridad', 'media'),
        'certeza': 0.75,
    },
    {
        'nombre': 'R14',
        'grupo': 'Prioridad',
        'descripcion': 'Si el impacto es bajo y no es un gerente, la prioridad es baja',
        'condiciones': [('impacto', 'bajo'), ('usuario_vip', False)],
        'conclusion': ('prioridad', 'baja'),
        'certeza': 0.85,
    },

    # ----- Grupo 4: Accion -----
    {
        'nombre': 'R15',
        'grupo': 'Acción',
        'descripcion': 'Si la prioridad es crítica, hay que avisarle al coordinador',
        'condiciones': [('prioridad', 'critica')],
        'conclusion': ('escalar_coordinador', True),
        'certeza': 1.0,
    },
]


# ---------------------------------------------------------------
# 3. TABLAS DE RECOMENDACIONES
# ---------------------------------------------------------------
# Esto no son reglas, es solo el texto que se le muestra al usuario
# segun lo que haya concluido el motor.

# Orden de las prioridades, de la mas baja a la mas alta
ORDEN_PRIORIDAD = ['baja', 'media', 'alta', 'critica']

TIEMPO_ATENCION = {
    'critica': 'Atender de inmediato (máximo 30 minutos)',
    'alta': 'Atender en máximo 2 horas',
    'media': 'Atender en máximo 8 horas (mismo día)',
    'baja': 'Atender en máximo 2 días hábiles',
}

QUE_HACER = {
    'seguridad': 'Desconectar el equipo de la red, no borrar nada y pasar el caso al equipo de seguridad informática.',
    'hardware': 'Programar visita del técnico de soporte en sitio para revisar el equipo.',
    'acceso': 'Mesa de ayuda (nivel 1) valida la identidad del usuario y desbloquea o ajusta permisos.',
    'software': 'Pasar a soporte nivel 2 para revisar el programa o servicio (logs, servidor, reinicio).',
}


# ---------------------------------------------------------------
# 4. AYUDAS PARA EL USUARIO
# ---------------------------------------------------------------

# Ejemplos que salen al pasar el mouse por el signo (?) de cada casilla
AYUDA = {
    'servicio_caido': 'Ej: el correo no abre, el sistema de facturación no carga, la página sale en error.',
    'falla_equipo': 'Ej: el PC no prende, la impresora se atasca, el monitor se ve negro, el cable está roto.',
    'problema_acceso': 'Ej: se bloqueó el usuario, olvidó la clave, no tiene permiso para entrar a una carpeta.',
    'sospecha_seguridad': 'Ej: llegó un correo raro pidiendo la clave, el PC muestra mensajes extraños, se perdieron archivos.',
    'varios_usuarios': 'Márcalo si le pasa a más de una persona (por ejemplo, a toda un área).',
    'sistema_critico': 'Sistemas sin los que la empresa no puede trabajar: facturación, correo, ERP, nómina.',
    'usuario_vip': 'Márcalo si quien reporta es gerente, director o alguien de la alta dirección.',
    'hay_alternativa': 'Ej: puede imprimir en otra impresora o trabajar desde otro PC mientras se arregla.',
}

# Que quiere decir cada prioridad, en palabras sencillas
SIGNIFICADO_PRIORIDAD = {
    'critica': 'Hay que atenderlo YA, dejando lo demás.',
    'alta': 'Es urgente, se atiende antes que los casos normales.',
    'media': 'Se atiende hoy mismo, en orden.',
    'baja': 'Se puede atender en orden de llegada, no es urgente.',
}

# Palabras que, si aparecen en la descripcion, sugieren marcar una casilla.
# Esto NO clasifica nada: solo marca casillas para que el usuario las revise.
# La clasificacion la siguen haciendo las reglas.
PALABRAS_CLAVE = {
    'servicio_caido': ['no abre', 'no le abre', 'no me abre', 'no les abre',
                       'no funciona', 'no le funciona', 'no me funciona', 'no les funciona',
                       'no carga', 'no le carga', 'no me carga', 'no responde', 'no sirve',
                       'caido', 'se cayo', 'error', 'no deja entrar al sistema', 'no hay sistema'],
    'falla_equipo': ['no prende', 'no enciende', 'impresora', 'monitor', 'pantalla', 'teclado',
                     'mouse', 'cable', 'se dano', 'danado', 'danada', 'se quemo', 'computador', 'portatil'],
    'problema_acceso': ['clave', 'contrasena', 'bloque', 'permiso', 'acceso',
                        'no puedo entrar', 'login', 'credencial'],
    'sospecha_seguridad': ['virus', 'hacke', 'phishing', 'correo raro', 'correo sospechoso',
                           'link raro', 'enlace raro', 'robo', 'ransomware', 'malware', 'sospech', 'secuestr'],
    'varios_usuarios': ['todos', 'varios', 'toda el area', 'todo el piso', 'toda la oficina',
                        'companeros', 'nadie puede', 'toda la empresa', 'muchos'],
    'sistema_critico': ['facturacion', 'correo', 'erp', 'nomina', 'contabilidad', 'cartera', 'sap'],
    'usuario_vip': ['gerente', 'director', 'presidente', 'vicepresidente'],
    'hay_alternativa': ['otra impresora', 'otro pc', 'otro equipo', 'otro computador', 'mientras tanto',
                        'puede seguir', 'alterna'],
}
