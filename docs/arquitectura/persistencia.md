# Persistencia y resultados

La aplicación almacena los resultados de las pruebas en archivos independientes dentro de `results/`.

## Objetivo de la persistencia

El guardado de resultados permite:

- Mantener trazabilidad de las pruebas realizadas.
- Revisar posteriormente las respuestas del usuario.
- Analizar el grado de cumplimiento de los criterios.
- Conservar evidencias de desempeño.
- Facilitar futuras mejoras de la herramienta.

## Información habitual de un resultado

Un resultado puede incluir:

- ID de la prueba.
- Competencia evaluada.
- Nivel evaluado.
- Respuestas del usuario.
- Criterios cumplidos.
- Criterios no cumplidos.
- Puntuación o valoración global.
- Fecha y hora de realización.
- Retroalimentación generada.

## Ejemplo orientativo

```json
{
  "test_id": "P01",
  "competence": "2.1",
  "level": "A1",
  "passed": true,
  "score": 0.85,
  "evidence": {
    "selected_ids": ["R01", "R03"]
  },
  "timestamp": "2026-05-21T12:00:00"
}
```
