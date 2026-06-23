# Arquitectura

La aplicación está desarrollada en Python con Flet. Se organiza en una capa de interfaz, los datos de las pruebas, los recursos utilizados y el almacenamiento local de resultados.

## Estructura principal

| Ruta | Función |
|---|---|
| `app.py` | Configura la ventana e inicia la aplicación. |
| `ui/` | Contiene la navegación, los componentes visuales y las pantallas. |
| `ui/views/` | Incluye la portada de la aplicación y coordina el proceso completo de evaluación. |
| `ui/test_views/` | Contiene la interfaz y la validación de cada una de las doce pruebas. |
| `data/` | Contiene un archivo JSON por prueba con el escenario, las opciones y los criterios necesarios para evaluarla. |
| `assets/` | Contiene imágenes, documentos y recursos simulados utilizados por las actividades. |
| `core/paths.py` | Resuelve las rutas de recursos y la ubicación en la que se pueden guardar resultados. |
| `core/storage.py` | Guarda cada resultado como un archivo JSON. |
| `unit_tests/` | Contiene las pruebas automáticas de carga, validación, progresión y almacenamiento. |
| `docs/` | Contiene esta documentación, publicada con MkDocs. |

## Flujo de la aplicación

1. `app.py` crea la ventana de Flet y carga la estructura general definida en `ui/shell.py`.
2. La pantalla inicial permite comenzar o reiniciar la evaluación.
3. `ui/views/evaluation_view.py` mantiene el estado de la sesión, define el orden de las pruebas y determina cuál debe mostrarse.
4. La vista correspondiente de `ui/test_views/` carga su archivo JSON desde `data/`.
5. La persona completa la actividad y solicita su validación.
6. La propia vista aplica los criterios de la prueba, muestra el feedback y actualiza el estado de la evaluación.
7. `core/storage.py` guarda el resultado en formato JSON.
8. Al finalizar, la aplicación muestra el nivel alcanzado en cada competencia.

El estado de la evaluación se conserva en memoria mientras la aplicación permanece abierta. Los resultados validados sí se guardan en disco.

## Organización de las pruebas

Cada prueba se compone principalmente de dos archivos:

- Un JSON en `data/`, con el escenario y la información necesaria para construir y evaluar la actividad.
- Una vista Python en `ui/test_views/`, con los controles de Flet, la lógica de interacción y la validación.

Las pruebas se agrupan por competencia:

| Competencia | Datos | Interfaz |
|---|---|---|
| 2.1 | `data/p01_...json` a `data/p04_...json` | `ui/test_views/comp21/` |
| 2.2 | `data/p05_...json` a `data/p08_...json` | `ui/test_views/comp22/` |
| 2.3 | `data/p09_...json` a `data/p12_...json` | `ui/test_views/comp23/` |

El orden general y la progresión por niveles se definen en `TEST_FLOW`, dentro de `ui/views/evaluation_view.py`.

## Recursos

Las imágenes, los PDF y los materiales simulados se almacenan en `assets/`. `core/paths.py` proporciona rutas válidas tanto al ejecutar el proyecto desde el código como al utilizar la versión portable.

Durante el empaquetado, las carpetas `assets/` y `data/` se incorporan a la aplicación para que las pruebas puedan acceder a ellas sin depender del repositorio.

## Resultados

Cada validación crea un archivo JSON independiente con la respuesta, las comprobaciones realizadas y la puntuación obtenida. Los archivos se organizan por competencia y prueba:

```text
results/
└── comp21/
    └── p01/
        └── fecha__P01__escenario.json
```

La aplicación intenta guardar primero en la carpeta `results` situada junto al proyecto o al ejecutable. Si Windows no permite escribir en ella, utiliza:

```text
%LOCALAPPDATA%\EvaluacionCDD\results
```

También es posible indicar otra ubicación mediante la variable de entorno `CDD_RESULTS_DIR`.

## Versión portable

`build_portable.ps1` utiliza Flet y PyInstaller para generar una distribución de Windows en modo carpeta. El resultado contiene:

| Elemento | Contenido |
|---|---|
| `EvaluacionCDD-portable.exe` | Ejecutable principal. |
| `_internal/` | Python, Flet, dependencias, datos y recursos necesarios. |
| `results/` | Ubicación inicial para guardar las evaluaciones. |
| `LEEME.txt` | Instrucciones básicas de ejecución. |

El ejecutable no debe separarse de `_internal`. El script comprime la carpeta completa como `EvaluacionCDD-portable-windows.zip`.

Cuando se sube a GitHub una etiqueta cuyo nombre empieza por `v`, el flujo `.github/workflows/release.yml` construye el portable en Windows y publica ese ZIP en una nueva versión.
