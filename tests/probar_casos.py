# probar_casos.py
# Corre todos los casos de prueba y muestra si el motor da lo esperado.
# Se ejecuta desde la carpeta principal del proyecto:
#     python tests/probar_casos.py

import os
import sys
import logging

# Para poder importar los archivos que estan en src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from base_conocimiento import REGLAS, ENTRADAS
from motor_inferencia import encadenamiento_adelante, obtener_resultado
from casos_prueba import CASOS

logging.disable(logging.INFO)  # para que no salga todo el log del motor

bien = 0
for caso in CASOS:
    hechos = {e: (e in caso['hechos']) for e in ENTRADAS}
    hechos_finales, reglas_aplicadas = encadenamiento_adelante(REGLAS, hechos)
    resultado = obtener_resultado(hechos_finales)

    reglas = [r['regla']['nombre'] for r in reglas_aplicadas]
    prioridad = resultado['prioridad'][0] if resultado else None

    ok = (reglas == caso['reglas_esperadas'] and prioridad == caso['prioridad_esperada'])
    if ok:
        bien += 1
    estado = 'OK ' if ok else 'MAL'
    print(f"[{estado}] Caso {caso['id']}: {caso['nombre']}")
    print(f"      reglas: {', '.join(reglas) or 'ninguna'} | prioridad: {prioridad or 'sin conclusión'}")

print(f'\n{bien} de {len(CASOS)} casos salieron bien')
print(f'Reglas en la base: {len(REGLAS)}')
sys.exit(0 if bien == len(CASOS) else 1)
