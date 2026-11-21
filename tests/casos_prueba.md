# Casos de prueba

Aquí están los casos que usamos para probar el sistema. Los mismos casos están en `src/casos_prueba.py`, y se pueden cargar desde la página (barra de la izquierda, "Casos de prueba").

Para correrlos todos de una vez y ver si dan lo esperado:

```
python tests/probar_casos.py
```

En "Hechos iniciales" solo ponemos lo que se marca como verdadero. Lo que no aparece se toma como falso.

| Caso | Descripción | Hechos iniciales | Reglas esperadas | Conclusión esperada | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| 1 | Correo con virus en varios PCs de contabilidad | sospecha_seguridad, varios_usuarios, sistema_critico | R1, R5, R8, R10, R15 | Seguridad, impacto alto, prioridad crítica, avisar al coordinador | R1, R5, R8, R10, R15 → crítica | ✓ |
| 2 | Se cayó el sistema de facturación para todos | servicio_caido, varios_usuarios, sistema_critico | R4, R5, R9, R10, R15 | Software, impacto alto, prioridad crítica, avisar al coordinador | R4, R5, R9, R10, R15 → crítica | ✓ |
| 3 | Se dañó la impresora del piso, pero hay otra | falla_equipo, varios_usuarios, hay_alternativa | R2, R6, R12 | Hardware, impacto medio, prioridad media | R2, R6, R12 → media | ✓ |
| 4 | Usuario bloqueado por poner mal la clave | problema_acceso | R3, R7, R14 | Acceso, impacto bajo, prioridad baja | R3, R7, R14 → baja | ✓ |
| 5 | Al gerente no le prende el monitor | falla_equipo, usuario_vip | R2, R7, R13 | Hardware, impacto bajo, prioridad media (sube por ser gerente) | R2, R7, R13 → media | ✓ |
| 6 | **Sin conclusión:** solo dicen que afecta a varios y que es el gerente | varios_usuarios, usuario_vip | Ninguna | No se puede clasificar | Ninguna regla → sin conclusión | ✓ |
| 7 | **Activa la mayoría de reglas:** cuenta hackeada y sistema caído para todos | sospecha_seguridad, problema_acceso, servicio_caido, varios_usuarios, sistema_critico, usuario_vip | R1, R3, R4, R5, R8, R9, R10, R15 (8 de 15) | Seguridad + acceso + software, impacto alto, prioridad crítica | R1, R3, R4, R5, R8, R9, R10, R15 → crítica | ✓ |
| 8 | **Borde:** programa caído para varios, no es crítico y no hay otra forma de trabajar | servicio_caido, varios_usuarios | R4, R6, R11 | Software, impacto medio, prioridad alta | R4, R6, R11 → alta | ✓ |
| 9 | **Borde:** virus en un solo PC | sospecha_seguridad | R1, R7, R8, R14, R15 | Salen dos prioridades (crítica y baja), debe quedar crítica | R1, R7, R8, R14, R15 → crítica | ✓ |
| 10 | **Borde:** el PC está dañado y por eso no abre el programa | falla_equipo, servicio_caido | R2, R7, R14 | Solo hardware (R4 no se debe activar porque la falla es del equipo), prioridad baja | R2, R7, R14 → baja | ✓ |

**Resultado: 10 de 10 casos salieron como esperábamos.**

## Qué revisamos con cada caso

- Entre todos los casos se usan las 15 reglas por lo menos una vez.
- El caso 6 es el que no tiene conclusión. Como no se dice qué está pasando (no hay categoría), no se puede calcular ni el impacto ni la prioridad.
- El caso 7 activa 8 de las 15 reglas, o sea la mayoría.
- El caso 9 prueba qué pasa cuando dos reglas dan prioridades distintas: R8 dice crítica y R14 dice baja. El sistema se queda con la más alta.
- El caso 10 prueba una regla con negación: R4 solo se cumple si NO hay falla del equipo.
- En los casos 2 y 7 la prioridad crítica sale por dos reglas distintas (R8 y R9). La segunda solo la confirma, no se agrega dos veces.
- También probamos desde la página darle "Clasificar incidente" sin marcar nada. Sale el mensaje "Marca por lo menos una opción antes de clasificar." y no se ejecuta el motor.
