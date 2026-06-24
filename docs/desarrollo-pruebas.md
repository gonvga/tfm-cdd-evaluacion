# Cómo colaborar

Este proyecto está pensado como una base ampliable para evaluar la competencia digital docente mediante tareas prácticas. La versión actual se centra en el Área 2 del MRCDD, pero la arquitectura permite incorporar nuevas pruebas, adaptar escenarios a otros contextos educativos o extender el modelo a otras áreas del marco.

La idea principal es mantener una evaluación basada en desempeño: no preguntar solo qué sabe declarar una persona, sino proponer una situación docente concreta y recoger evidencias observables de lo que decide, selecciona, adapta, publica o documenta.

## Qué se puede ampliar

Las contribuciones pueden orientarse a:

- Añadir nuevas pruebas para otros indicadores del Área 2.
- Crear itinerarios equivalentes para otras áreas del MRCDD.
- Adaptar escenarios a etapas, materias o contextos institucionales concretos.
- Mejorar feedback, accesibilidad, redacción o claridad de las pruebas existentes.
- Añadir recursos visuales, datos de ejemplo o documentación pedagógica.
- Reforzar las pruebas automáticas que validan el comportamiento de la aplicación.

## Principios de diseño

Una nueva prueba debería conservar estos criterios:

- Evaluar acciones reales o verosímiles de la práctica docente.
- Partir de un escenario contextualizado, no de preguntas aisladas.
- Alinear cada tarea con indicadores de logro del MRCDD.
- Recoger evidencias concretas de desempeño.
- Separar los datos de la prueba, la interfaz y la lógica de validación.
- Ofrecer feedback formativo después de validar.
- Mantener una progresión clara entre niveles cuando forme parte de un itinerario.
- Evitar dependencias externas que dificulten ejecutar la herramienta sin conexión.

## Estructura de una prueba

Cada prueba suele combinar:

- Un archivo JSON en `data/` con el escenario, opciones, textos y criterios esperados.
- Un módulo en `ui/test_views/` que construye la interfaz y evalúa la respuesta.
- Recursos complementarios en `assets/`, si la actividad necesita imágenes u otros materiales.
- Una salida estructurada en `results/` con evidencias, puntuación y checks superados.
- Pruebas automáticas en `unit_tests/test_programmed_tests.py`.

Esta separación facilita modificar escenarios sin reescribir toda la interfaz y permite añadir nuevas pruebas sin rediseñar la aplicación completa.

## Cómo proponer una prueba nueva

Antes de implementar, conviene definir:

- Competencia y nivel que se quiere evaluar.
- Indicadores de logro concretos.
- Situación docente que da sentido a la tarea.
- Acciones observables que debe realizar el usuario.
- Criterios mínimos para superar la prueba.
- Feedback que recibirá el usuario al validar.
- Evidencias que se guardarán en el resultado.

Después, se puede crear el JSON de datos, implementar la vista, registrar la prueba en el flujo de evaluación y añadir tests de respuesta correcta y respuesta vacía.

## Validación

Antes de enviar cambios, ejecuta:

```powershell
.\venv\Scripts\python.exe -m unittest unit_tests.test_programmed_tests
```

Si modificas la documentación, comprueba también:

```powershell
.\venv\Scripts\python.exe -m mkdocs build
```

La suite comprueba la carga, la validación y el guardado de resultados de las pruebas implementadas. Al añadir o modificar una prueba, es importante que los tests cubran tanto la superación como una respuesta insuficiente.

## Modo de pruebas manuales

Durante el desarrollo puede ser útil avanzar aunque una prueba no esté superada:

```powershell
$env:CDD_ALLOW_FAILED_ADVANCE="1"
.\venv\Scripts\python.exe app.py
```

Sin esa variable, la evaluación mantiene el bloqueo normal cuando una competencia queda no superada.
