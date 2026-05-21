# Validación y pruebas unitarias

Las pruebas unitarias permiten asegurar que la lógica de evaluación funciona correctamente.

## Qué conviene validar

- Carga correcta de escenarios.
- Evaluación de respuestas válidas.
- Evaluación de respuestas incompletas.
- Generación del resultado común.
- Guardado de evidencias.
- Registro correcto de nuevas pruebas.

## Ejecución

```bash
pytest
```

## Recomendaciones

- Mantener tests pequeños.
- Probar cada criterio de evaluación de forma aislada.
- No depender de la interfaz gráfica para validar la lógica.
- Usar datos de ejemplo sencillos.
