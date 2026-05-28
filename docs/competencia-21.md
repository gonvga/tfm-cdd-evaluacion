# Competencia 2.1: Búsqueda y selección de contenidos digitales

La competencia 2.1 del MRCDD se evalúa mediante cuatro pruebas progresivas: P01, P02, P03 y P04. Todas están planteadas como actividades de desempeño y generan evidencias observables: selecciones, consultas de búsqueda, fichas revisadas, catalogaciones y decisiones justificadas.

## Visión General

| Prueba | Nivel | Foco de evaluación | Archivo de datos | Vista |
|---|---|---|---|---|
| P01 | A1 | Reconocimiento de criterios básicos, buscadores, metadatos y organización inicial | `data/p01_comp21_a1.json` | `ui/test_views/comp21/p01_identificar_recursos.py` |
| P02 | A2 | Selección guiada de contenidos según requisitos, repositorios y compatibilidad | `data/p02_comp21_a2.json` | `ui/test_views/comp21/p02_seleccionar_recurso.py` |
| P03 | B1 | Búsqueda práctica, revisión de fichas simuladas y catalogación autónoma | `data/p03_comp21_b1.json` | `ui/test_views/comp21/p03_banco_recursos.py` |
| P04 | B2 | Protocolo relacional de curación, asesoramiento y actualización de repositorios | `data/p04_comp21_b2.json` | `ui/test_views/comp21/p04_curacion_contenidos.py` |

## P01 · Nivel A1

P01 evalúa el acceso inicial a la competencia 2.1. La prueba comprueba si el usuario reconoce criterios básicos de calidad y organización de contenidos digitales.

**Indicadores evaluados**

- `2.1.A1.1`: conocimiento de criterios didácticos, técnicos y científicos.
- `2.1.A1.2`: uso básico de buscadores neutros y conocimiento de metadatos.
- `2.1.A1.3`: uso inicial de sistemas de organización de recursos.

**Tareas**

| Fase | Acción del usuario | Evidencia generada |
|---|---|---|
| Clasificación | Clasificar etiquetas en criterios científicos, técnicos o didácticos | Categoría asignada a cada criterio |
| Buscadores | Seleccionar herramientas de búsqueda adecuadas | Buscadores marcados |
| Metadatos | Resolver una situación sobre recuperación de recursos | Respuesta seleccionada |
| Organización | Nombrar una carpeta y seleccionar archivos educativos | Nombre de carpeta y archivos movidos |

Para superar P01, el usuario debe clasificar correctamente los criterios, seleccionar los buscadores esperados, identificar los metadatos y organizar solo los archivos pertinentes.

## P02 · Nivel A2

P02 evalúa la selección de contenidos con apoyo y asesoramiento. El usuario traduce un contexto concreto en requisitos, repositorios, filtros y una decisión final.

**Indicadores evaluados**

- `2.1.A2.1`: identificación de requisitos para una situación concreta de aprendizaje, incluyendo compatibilidad con plataformas del centro.
- `2.1.A2.2`: uso de repositorios institucionales o del centro.

**Tareas**

| Fase | Acción del usuario | Evidencia generada |
|---|---|---|
| Requisitos | Marcar requisitos del contenido digital | Requisitos seleccionados |
| Repositorios | Elegir fuentes preferentes de búsqueda | Repositorios seleccionados |
| Filtros | Seleccionar filtros compatibles con el entorno virtual | Filtros marcados |
| Ficha | Abrir fichas de recursos candidatos | Fichas consultadas |
| Selección | Elegir el recurso más adecuado | Recurso seleccionado |

Para superar P02, el usuario debe identificar requisitos del grupo y del centro, priorizar repositorios adecuados, aplicar filtros técnicos y seleccionar el recurso que mejor se ajusta al contexto.

## P03 · Nivel B1

P03 evalúa la autonomía en la búsqueda y catalogación de contenidos. El usuario no solo reconoce opciones: construye consultas de búsqueda y organiza recursos revisados.

**Indicadores evaluados**

- `2.1.B1.1`: aplicación autónoma de criterios didácticos, técnicos y científicos.
- `2.1.B1.2`: uso de búsquedas para localizar distintos formatos de contenido.
- `2.1.B1.3`: organización sistemática de contenidos educativos digitales.

**Tareas**

| Fase | Acción del usuario | Evidencia generada |
|---|---|---|
| Búsquedas | Escribir consultas con operadores y criterios | Queries introducidas |
| Revisión | Abrir fichas simuladas de recursos | Recursos revisados |
| Catalogación | Clasificar recursos por finalidad, dificultad y etiqueta | Catálogo generado |
| Sistema | Seleccionar sistemas de organización recuperables | Sistemas seleccionados |

La prueba valida consultas que incorporan criterios como `site:`, `filetype:pdf`, licencia, Creative Commons, vídeo, subtítulos, transcripción, infografía, H5P, simulación o actividad interactiva.

P03 utiliza fichas Markdown ubicadas en:

```text
assets/simulated_resources/comp21_p03/
```

Para superar P03, el usuario debe construir consultas válidas, revisar un número mínimo de fichas, catalogar los recursos con la finalidad esperada y seleccionar sistemas de organización recuperables.

## P04 · Nivel B2

P04 evalúa un desempeño más avanzado: el usuario aplica un protocolo relacional de curación, formula asesoramiento para otros docentes y selecciona acciones de actualización de repositorios.

**Indicadores evaluados**

- `2.1.B2.1`: uso de un instrumento de evaluación y catalogación relacional de contenidos digitales.
- `2.1.B2.2`: asesoramiento informal a otros docentes sobre estrategias de búsqueda en Internet.
- `2.1.B2.3`: actitud proactiva para localizar y mantener repositorios de contenidos digitales.

**Tareas**

| Fase | Acción del usuario | Evidencia generada |
|---|---|---|
| Protocolo relacional | Evaluar recursos con Bloom, competencia, decisión y puntuaciones | Matriz de catalogación |
| Asesoramiento | Escribir consultas recomendables para otra docente | Queries de asesoramiento |
| Actualización | Seleccionar acciones de mantenimiento del catálogo | Acciones seleccionadas |

El protocolo de P04 combina nivel cognitivo de Bloom, competencia trabajada, decisión de curación, calidad técnica, veracidad y relevancia didáctica. Esto diferencia B2 de B1: no solo se catalogan recursos, sino que se aplica un protocolo reutilizable para mejorar la selección y asesorar al equipo docente.

Para superar P04, el usuario debe completar correctamente la matriz relacional, formular consultas con operadores y criterios útiles para asesorar, y seleccionar acciones proactivas de actualización del catálogo.

## Feedback E Interfaz

Las pruebas P01-P04 ofrecen feedback contextual. Las opciones correctas e incorrectas se diferencian visualmente y, cuando la corrección podría ocupar demasiado espacio, se muestra en paneles compactos bajo el bloque correspondiente.

## Progresión A1-B2

| Nivel | Desempeño principal |
|---|---|
| A1 | Reconoce criterios básicos y organiza recursos sencillos |
| A2 | Selecciona con apoyo recursos ajustados a un contexto |
| B1 | Busca y cataloga de forma autónoma recursos variados |
| B2 | Aplica un protocolo, asesora a otros docentes y mejora el catálogo |

Esta progresión permite pasar de la identificación inicial de criterios a la curación avanzada de contenidos digitales con valor para el equipo docente.
