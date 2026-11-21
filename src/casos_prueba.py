# casos_prueba.py
# Casos de prueba del sistema. Se usan en dos partes:
#   1. En la pagina (app.py) como "casos precargados" para la demo.
#   2. En tests/probar_casos.py para revisar que el motor da lo que esperamos.
#
# En 'hechos' solo se ponen los que son verdaderos; los demas se toman como falsos.
# 'prioridad_esperada' = None quiere decir que NO debe salir conclusion.

CASOS = [
    {
        'id': 1,
        'nombre': 'Correo con virus en varios PCs de contabilidad',
        'hechos': ['sospecha_seguridad', 'varios_usuarios', 'sistema_critico'],
        'reglas_esperadas': ['R1', 'R5', 'R8', 'R10', 'R15'],
        'prioridad_esperada': 'critica',
    },
    {
        'id': 2,
        'nombre': 'Se cayó el sistema de facturación para todos',
        'hechos': ['servicio_caido', 'varios_usuarios', 'sistema_critico'],
        'reglas_esperadas': ['R4', 'R5', 'R9', 'R10', 'R15'],
        'prioridad_esperada': 'critica',
    },
    {
        'id': 3,
        'nombre': 'Se dañó la impresora del piso, pero hay otra',
        'hechos': ['falla_equipo', 'varios_usuarios', 'hay_alternativa'],
        'reglas_esperadas': ['R2', 'R6', 'R12'],
        'prioridad_esperada': 'media',
    },
    {
        'id': 4,
        'nombre': 'Usuario bloqueado por poner mal la clave',
        'hechos': ['problema_acceso'],
        'reglas_esperadas': ['R3', 'R7', 'R14'],
        'prioridad_esperada': 'baja',
    },
    {
        'id': 5,
        'nombre': 'Al gerente no le prende el monitor',
        'hechos': ['falla_equipo', 'usuario_vip'],
        'reglas_esperadas': ['R2', 'R7', 'R13'],
        'prioridad_esperada': 'media',
    },
    {
        'id': 6,
        'nombre': 'Sin conclusión: solo dicen que afecta a varios y es el gerente',
        'hechos': ['varios_usuarios', 'usuario_vip'],
        'reglas_esperadas': [],
        'prioridad_esperada': None,
    },
    {
        'id': 7,
        'nombre': 'Caso grande: cuenta hackeada, sistema caído para todos',
        'hechos': ['sospecha_seguridad', 'problema_acceso', 'servicio_caido',
                   'varios_usuarios', 'sistema_critico', 'usuario_vip'],
        'reglas_esperadas': ['R1', 'R3', 'R4', 'R5', 'R8', 'R9', 'R10', 'R15'],
        'prioridad_esperada': 'critica',
    },
    {
        'id': 8,
        'nombre': 'Borde: programa caído para varios, no es crítico y no hay otra forma',
        'hechos': ['servicio_caido', 'varios_usuarios'],
        'reglas_esperadas': ['R4', 'R6', 'R11'],
        'prioridad_esperada': 'alta',
    },
    {
        'id': 9,
        'nombre': 'Borde: virus en un solo PC (salen dos prioridades, gana la más alta)',
        'hechos': ['sospecha_seguridad'],
        'reglas_esperadas': ['R1', 'R7', 'R8', 'R14', 'R15'],
        'prioridad_esperada': 'critica',
    },
    {
        'id': 10,
        'nombre': 'Borde: PC dañado y por eso no abre el programa',
        'hechos': ['falla_equipo', 'servicio_caido'],
        'reglas_esperadas': ['R2', 'R7', 'R14'],
        'prioridad_esperada': 'baja',
    },
]
