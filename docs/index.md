# Documentación de la aplicación

Esta web documenta la herramienta desarrollada para evaluar la competencia digital docente en el Área 2: Contenidos digitales del MRCDD (2022).

La aplicación ha sido desarrollada en Python mediante la librería Flet y plantea un modelo de evaluación basado en tareas prácticas orientadas a la obtención de evidencias de desempeño docente.

## Objetivo

La herramienta busca complementar los cuestionarios tradicionales de autopercepción mediante actividades que permitan evaluar acciones observables relacionadas con el uso de contenidos digitales educativos.

## Competencias evaluadas

La aplicación evalúa las tres competencias del Área 2 del MRCDD:

| Competencia | Descripción |
|---|---|
| 2.1 | Búsqueda y selección de contenidos digitales |
| 2.2 | Creación y modificación de contenidos digitales |
| 2.3 | Protección, gestión y compartición de contenidos digitales |

## Niveles

La evaluación se organiza siguiendo la progresión competencial del MRCDD:

```text
A1 → A2 → B1 → B2
```

El usuario debe superar cada nivel antes de acceder al siguiente.

## Estructura de pruebas

La herramienta se organiza en 12 pruebas prácticas:

| Competencia | A1 | A2 | B1 | B2 |
|---|---|---|---|---|
| 2.1 | P01 | P02 | P03 | P04 |
| 2.2 | P05 | P06 | P07 | P08 |
| 2.3 | P09 | P10 | P11 | P12 |

## Enfoque pedagógico

La aplicación se basa en un enfoque de evaluación orientado al desempeño. Las pruebas plantean situaciones relacionadas con la práctica docente real:

- Selección de recursos.
- Corrección de materiales.
- Adaptación de contenidos.
- Organización de archivos.
- Configuración de permisos.
- Publicación de recursos.

Las acciones realizadas por el usuario son analizadas automáticamente mediante criterios previamente definidos.

## Características principales

- Arquitectura modular.
- Escenarios editables mediante JSON.
- Evaluación automática.
- Resultados trazables.
- Aplicación autocontenida.
- Compatibilidad multiplataforma.

## Aplicación autocontenida

La herramienta ha sido diseñada como un entorno de evaluación autocontenido, de manera que las actividades puedan ejecutarse sin depender de servicios externos, plataformas en la nube o programas de terceros instalados en el sistema.

Esto simplifica la instalación, facilita el mantenimiento y permite mantener un mayor control sobre el proceso de evaluación.
