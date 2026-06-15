# Arquitectura

La aplicación separa la interfaz, los datos de las pruebas y el guardado de resultados.

## Carpetas principales

```
assets/       Imágenes y recursos
core/         Rutas y guardado de resultados
data/         Escenarios de las pruebas en JSON
docs/         Documentación
ui/           Pantallas y componentes
unit_tests/   Pruebas automáticas
app.py        Inicio de la aplicación
```

## Cómo funciona

```
Se carga una prueba
        ↓
Se lee su archivo JSON
        ↓
El usuario completa la actividad
        ↓
La aplicación valida las respuestas
        ↓
Muestra feedback y guarda el resultado
```

## Escenarios JSON

Cada prueba tiene un archivo en `data/`. Allí se encuentran el escenario, las opciones, los criterios y los mensajes de feedback.

Esto permite modificar el contenido sin rehacer toda la aplicación.

## Recursos

Las imágenes y fichas simuladas están en `assets/`. La aplicación puede encontrarlas tanto durante el desarrollo como dentro de la versión portable.

## Resultados

Cada validación genera un archivo JSON dentro de `results/`, organizado por competencia y prueba.

## Versión portable

La carpeta portable incluye:

- `EvaluacionCDD-portable.exe`.
- La carpeta `_internal` con datos, recursos y dependencias.
- La carpeta `results`.

El `.exe` y `_internal` deben permanecer juntos.
