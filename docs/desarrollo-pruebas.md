# Desarrollo de pruebas

Cada prueba contiene:

- Un escenario.
- Una actividad observable.
- Criterios de evaluación.
- Feedback posterior a la validación.
- Un resultado guardado.

## Archivos

- Los datos se guardan en `data/`.
- La interfaz y la validación se guardan en `ui/test_views/`.
- Los recursos visuales se guardan en `assets/`.

## Buenas prácticas

- Evaluar acciones, no solo conocimientos.
- Evitar respuestas demasiado evidentes.
- Mostrar el feedback después de validar.
- Mantener una progresión clara entre A1, A2, B1 y B2.
- Añadir una prueba automática para la respuesta correcta y la respuesta vacía.

## Ejecutar las pruebas automáticas

```
.\venv\Scripts\python.exe -m unittest unit_tests.test_programmed_tests
```

La suite comprueba la carga, la validación y el guardado de resultados de las 12 pruebas.
