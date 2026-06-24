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

P02 evalúa la selección de contenidos con apoyo y asesoramiento. El usuario traduce un contexto concreto en requisitos observables, elige estrategias completas de búsqueda y compara candidatos plausibles con ventajas e incompatibilidades discretas.

**Indicadores evaluados**

- `2.1.A2.1`: identificación de requisitos para una situación concreta de aprendizaje, incluyendo compatibilidad con plataformas del centro.
- `2.1.A2.2`: uso de repositorios institucionales o del centro.

**Tareas**

| Fase | Acción del usuario | Evidencia generada |
|---|---|---|
| Requisitos | Distinguir condiciones necesarias de cualidades solo deseables | Requisitos seleccionados |
| Repositorios | Elegir los espacios institucionales y del centro por los que iniciar la búsqueda | Repositorios seleccionados |
| Estrategias | Seleccionar configuraciones de filtros ajustadas al caso | Estrategias seleccionadas |
| Contraste | Comparar al menos tres fichas con candidatos plausibles | Fichas consultadas |
| Selección | Elegir el recurso más adecuado | Recurso seleccionado |

Para superar P02, el usuario debe identificar requisitos derivados del grupo y del centro, priorizar repositorios adecuados, evitar filtros irrelevantes o excesivos, consultar al menos tres candidatos y seleccionar el recurso que mejor resuelve conjuntamente el objetivo, la accesibilidad, el tiempo, la conectividad y la compatibilidad con Moodle.

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

```
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

## Guía de respuestas y aprendizaje

Este apartado permite revisar todas las decisiones de las pruebas P01-P04. En las preguntas de selección se indican tanto las opciones correctas como los distractores. En las tareas abiertas se ofrece un modelo válido: no es la única redacción posible, pero sí muestra todos los elementos que la aplicación comprueba.

### Soluciones de P01

#### Clasificación de criterios de calidad

| Criterio | Respuesta correcta | Por qué |
|---|---|---|
| Fecha de actualización o revisión | Científico | Ayuda a valorar la vigencia de la información y si el contenido sigue siendo fiable. |
| Licencia de uso Creative Commons | Técnico | Determina las condiciones legales de acceso, reutilización y adaptación del archivo. |
| Autoría institucional o reconocida | Científico | Permite comprobar la procedencia, responsabilidad y autoridad de la fuente. |
| Nivel educativo o edad recomendada | Didáctico | Indica para qué alumnado y grado de desarrollo se ha diseñado el recurso. |
| Compatibilidad con lectores de pantalla o subtítulos | Técnico | Describe si el formato y su implementación permiten un acceso adecuado. |
| Objetivos de aprendizaje vinculados al currículo | Didáctico | Relaciona el recurso con lo que se pretende enseñar y aprender. |

La idea clave es distinguir tres preguntas: «¿es fiable?» corresponde a lo científico; «¿puede utilizarse y accederse correctamente?» a lo técnico; y «¿sirve para este alumnado y objetivo?» a lo didáctico.

#### Herramientas de búsqueda

- **Correctas:**
  - Google Académico.
  - DuckDuckGo.

  Google Académico prioriza literatura académica y DuckDuckGo reduce la personalización basada en perfiles, por lo que responden mejor al criterio planteado.

- **Incorrectas:**
  - Google.
  - Yahoo Search.

  Son buscadores generales útiles en otros contextos, pero en esta tarea se quieren reducir resultados condicionados por publicidad o perfil comercial. No son «malos buscadores» en términos absolutos; simplemente no son los preferentes para este propósito.

#### Metadatos

- **Correcta:** «Los metadatos: etiquetas de área, nivel, autoría y descripción». Los metadatos describen el contenido con campos recuperables y permiten que un buscador o catálogo lo indexe.

- **Incorrecta:** «El tamaño del archivo y su fecha de creación». Son propiedades técnicas, pero no explican de qué trata el recurso.

- **Incorrecta:** «El nombre del servidor». Informa sobre el alojamiento, no sobre el contenido educativo.

- **Incorrecta:** «La resolución de las imágenes». Afecta a la calidad visual, pero no aporta palabras clave para recuperar el recurso.

#### Organización de archivos

El nombre de la carpeta debe describir el contenido. Son válidos, por ejemplo, `Sostenibilidad_2ESO`, `UD_Sostenibilidad` o `Recursos_Biología_Sostenibilidad`. Nombres como `Nueva carpeta`, `Documentos` o `Cosas` no permiten reconocer ni recuperar con facilidad la unidad.

- **Deben incluirse:**
  - `Documento_01.pdf`.
  - `Enlace_recurso.url`.
  - `Video_actividad.mp4`.

  Los tres contienen materiales educativos sobre sostenibilidad.

- **No debe incluirse:** `Lista_Compra.pdf`, porque es un archivo personal ajeno a la unidad. Mezclar documentos personales y docentes dificulta la recuperación y puede provocar una compartición accidental.

### Soluciones de P02

#### Requisitos derivados del contexto

- **Correctos:**
  - Comprobación breve de productor, consumidor y descomponedor.
  - Ampliación y uso no exclusivo del color.
  - Apertura desde Moodle sin instalación ni registro.
  - Alternativa descargable o imprimible.

  Cada condición procede directamente del objetivo, la baja visión, la política técnica del centro o la conexión inestable.

- **Incorrecto:** exigir todos los archivos fuente. Serían útiles para una adaptación profunda, pero la actividad breve no los necesita.

- **Incorrecto:** registrar cada clic en una plataforma externa. No aporta la evidencia esencial y contradice la prohibición de crear cuentas externas.

- **Incorrecto:** maximizar vídeos, animaciones y sonidos. Más multimedia no significa mejor aprendizaje y puede aumentar carga cognitiva, consumo de datos y barreras de acceso.

#### Repositorios iniciales

- **Correctos:**
  - Repositorio de la Administración educativa.
  - Colección de Moodle revisada por Biología.

  El primero aporta catalogación institucional; el segundo ofrece recursos ya contrastados en el contexto técnico y pedagógico del centro.

- **Incorrecto:** comenzar por resultados patrocinados de un buscador general. Puede utilizarse para ampliar la búsqueda, pero desaprovecha las fuentes institucionales prioritarias.

- **Incorrecto:** elegir publicaciones de una red social por popularidad. La interacción social no acredita nivel, licencia, accesibilidad ni compatibilidad.

#### Estrategias de búsqueda

- **Correctas:**
  - `2.º ESO + cadenas tróficas + HTML/H5P + sin registro + accesibilidad documentada`.
  - `revisado por Biología + actividad breve + alternativa descargable`.

  Combinan tema, nivel, formato, acceso, duración y necesidades reales.

- **Incorrecta:** `solo SCORM + máxima interactividad + cualquier etapa`. Moodle no tiene habilitado SCORM y se pierde el ajuste al nivel.

- **Incorrecta:** `más abierto + más descargado + cualquier duración`. La popularidad no sustituye la adecuación didáctica ni temporal.

- **Incorrecta:** `2.º ESO + PDF exclusivamente + último mes`. Introduce límites no justificados: el recurso principal puede ser HTML o H5P y no necesita haberse publicado ese mes.

#### Comparación de recursos

La respuesta correcta es **C · Construye y comprueba una cadena trófica**. Se ajusta a 2.º de ESO, dura 22-25 minutos, funciona desde Moodle sin cuentas externas, es accesible, comprueba los tres roles y dispone de una ficha PDF equivalente si falla la conexión.

- **A · Red alimentaria interactiva:** incorrecta porque exige una cuenta externa, depende parcialmente del color y no tiene alternativa sin conexión, aunque su contenido y cuestionario sean valiosos.

- **B · Microdocumental:** incorrecta como recurso principal porque es accesible y compatible, pero no incluye una tarea que produzca la evidencia de aprendizaje solicitada.

- **D · Laboratorio virtual:** incorrecta porque requiere el complemento SCORM no habilitado y no comprueba el papel de los descomponedores.

Además de elegir C, deben abrirse al menos tres fichas. La consulta previa forma parte de la competencia: una elección acertada por azar no demuestra contraste de fuentes.

### Soluciones de P03

#### Consultas de búsqueda

Modelos válidos:

| Necesidad | Ejemplo de consulta | Elementos imprescindibles |
|---|---|---|
| PDF fiable | `cambio climático site:intef.es filetype:pdf` | Tema, `site:` y `filetype:pdf`. |
| Vídeo accesible | `vídeo cambio climático subtítulos transcripción` | Tema, formato audiovisual y alternativa accesible. |
| Imagen reutilizable | `infografía sostenibilidad Creative Commons` | Imagen o infografía, tema y licencia. |
| Actividad interactiva | `H5P actividad alumnado huella de carbono` | H5P/interactivo/simulación, participación y tema. |

Una consulta es incompleta si omite uno de esos grupos. Por ejemplo, `cambio climático PDF` no acota una fuente fiable; `vídeo cambio climático` no contempla accesibilidad; `infografía sostenibilidad` no comprueba la licencia; y `H5P cambio climático` no expresa la finalidad participativa.

#### Selección y catalogación del lote

| Recurso | Decisión, uso y etiqueta | Explicación |
|---|---|---|
| R1 · Vídeo subtitulado | Incorporar · Introducción común · `inicio-clima` | Es breve, activa conocimientos previos y presenta las causas de forma visual y accesible. Dificultad orientativa: básica. |
| R2 · Simulación H5P | Incorporar · Participación común · `participación` | Permite decidir por parejas y recibir feedback; funciona en Moodle, no exige cuentas y tiene alternativa ante fallos de conexión. Dificultad orientativa: media. |
| R3 · Informe científico | Descartar · No catalogar · `no catalogar` | Es fiable, pero está dirigido a Bachillerato, requiere unos 35 minutos y usa vocabulario no trabajado. Un recurso de calidad puede ser inadecuado para un contexto concreto. |
| R4 · Infografía accesible | Incorporar · Apoyo visual · `apoyo-visual` | Resume mediante iconos etiquetados, frases breves y texto equivalente; apoya al alumnado sin crear un itinerario segregado. Dificultad orientativa: básica. |
| R5 · Artículo avanzado | Incorporar · Ampliación · `ampliación-clima` | Su glosario, modo lectura y preguntas permiten ofrecer un reto autónomo a quien termina antes. Dificultad orientativa: alta. |
| R6 · Imagen viral | Descartar · No catalogar · `no catalogar` | No se pueden verificar autoría, licencia ni rigor; existen versiones contradictorias y no tiene alternativa textual. |

La dificultad es una estimación docente y no penaliza por sí sola. Sí deben coincidir la decisión, el uso didáctico y la etiqueta, porque son los datos que permiten formar y recuperar el lote.

#### Sistema de organización

- **Correcto:** registrar tema, nivel, área, uso, dificultad, formato, licencia, enlace y fecha de revisión en el catálogo compartido.

- **Correcto:** aplicar vocabulario acordado y nombres estables a archivos y enlaces.

- **Incorrecto:** conservarlo todo en `Descargas`. Esa carpeta no aporta clasificación, contexto ni mantenimiento.

- **Incorrecto:** confiar en el historial de un chat. Los mensajes se desplazan, los enlaces pueden quedar sin contexto y no existe una ficha común actualizable.

También deben revisarse las seis fichas y seleccionarse los cuatro formatos previstos. Esto demuestra análisis del conjunto y no una decisión superficial basada en el título.

### Soluciones de P04

#### Protocolo relacional

Las puntuaciones admiten un margen de un punto respecto a la referencia; una diferencia de dos puntos recibe crédito parcial y una mayor no se ajusta a la evidencia. Bloom y competencia también admiten las alternativas indicadas porque un mismo recurso puede sostener usos próximos si la decisión es coherente. Para recomendar, las tres puntuaciones deben ser al menos 3 y su media al menos 3,5; adaptar exige veracidad mínima 2, relevancia mínima 3 y media 2,5; descartar es coherente cuando técnica o veracidad son como máximo 2, o la media no supera 2,5.

| Recurso | Respuestas aceptadas | Puntuación de referencia | Por qué |
|---|---|---|---|
| A · Guía institucional | Analizar o Evaluar · Alfabetización mediática o Ciudadanía digital · Recomendar | Técnica 5 · Veracidad 5 · Relevancia 5 | Tiene autoría, fuentes, actualización, CC BY, accesibilidad y aplicación directa en 3.º de ESO. |
| B · Vídeo viral | Comprender o Analizar · Ciudadanía digital o Alfabetización mediática · Descartar | Técnica 1 · Veracidad 1 · Relevancia 2 | No tiene autoría, fuentes, fecha, licencia ni alternativas accesibles. Ser llamativo no compensa esas carencias. |
| C · H5P de titulares | Analizar o Evaluar · Comunicación o Alfabetización mediática · Adaptar o Recomendar | Técnica 4 · Veracidad 3 · Relevancia 4 | La base es accesible y útil, pero necesita contexto y criterios de verificación; por ello adaptar es la opción más prudente y recomendar con contextualización también es defendible. |
| D · Imágenes satíricas | Analizar o Evaluar · Alfabetización mediática o Comunicación · Descartar | Técnica 2 · Veracidad 2 · Relevancia 3 | El posible debate no resuelve la falta de procedencia, derechos de uso, contexto y textos alternativos. |

Son incoherentes, por ejemplo, recomendar B o D pese a no poder verificar derechos y procedencia; descartar A pese a cumplir todos los criterios; o asignar puntuaciones máximas de veracidad a materiales sin fuentes.

#### Asesoramiento sobre búsquedas

**Caso 1: guía institucional reutilizable**

- Consulta modelo: `desinformación site:intef.es filetype:pdf "Creative Commons"`.
- Justificación modelo: el dominio institucional reduce resultados de procedencia dudosa; el PDF facilita localizar una guía descargable y revisable; Creative Commons permite identificar materiales potencialmente reutilizables.
- Comprobación modelo: verificar autoría o institución, fecha y vigencia, licencia exacta, etiquetado del PDF, contraste y otras medidas de accesibilidad.

Una respuesta falla si solo propone palabras temáticas, si no explica el valor de los filtros o si confunde «estar en Internet» con permiso de reutilización.

**Caso 2: actividad interactiva educativa**

- Consulta modelo: `H5P desinformación actividad repositorio educativo`.
- Justificación modelo: H5P orienta hacia una práctica interactiva; el repositorio aporta catalogación educativa; el tema mantiene el ajuste al objetivo y al curso.
- Comprobación modelo: probar teclado, dispositivos y compatibilidad; revisar nivel, contenido y fuentes; confirmar licencia y permiso de adaptación.

No basta con encontrar un interactivo atractivo: debe comprobarse que funciona, que enseña contenido fiable y que puede usarse legalmente.

#### Plan proactivo de actualización

Modelos válidos:

- **Descubrimiento:** «Revisaré repositorios institucionales como INTEF y Procomún, y me suscribiré a sus boletines o alertas para descubrir periódicamente fuentes y colecciones educativas nuevas».

- **Revisión:** «Cada trimestre revisaré fecha y vigencia, licencia, accesibilidad y enlaces de los recursos, incorporando la valoración y los resultados obtenidos durante su uso en el aula».

- **Compartición y mejora:** «Registraré las novedades en el catálogo compartido y presentaré las conclusiones al departamento para ajustar criterios, reformular consultas y actualizar el protocolo de búsqueda».

Son insuficientes planes como «buscaré recursos cuando los necesite», porque no incluyen fuentes ni seguimiento; «los revisaré de vez en cuando», porque no fija periodicidad ni criterios; o «enviaré los enlaces al grupo», porque no crea memoria compartida ni mejora el protocolo.

## Feedback E Interfaz

Las pruebas P01-P04 ofrecen feedback contextual. Las opciones correctas e incorrectas se diferencian visualmente y, cuando la corrección podría ocupar demasiado espacio, se muestra en paneles compactos bajo el bloque correspondiente.

## Justificación MRCDD

- **P01** se alinea con `2.1.A1.1`, `2.1.A1.2` y `2.1.A1.3` porque solicita clasificar criterios científicos, técnicos y didácticos, elegir buscadores neutros o académicos, reconocer metadatos y organizar recursos básicos.
- **P02** se alinea con `2.1.A2.1` y `2.1.A2.2` porque convierte el contexto del grupo y del centro en requisitos operativos, elige repositorios institucionales y compara fichas antes de seleccionar el recurso más adecuado.
- **P03** se alinea con `2.1.B1.1`, `2.1.B1.2` y `2.1.B1.3` porque exige construir búsquedas, revisar fichas multimodales y catalogar recursos con criterios de finalidad, dificultad y etiqueta.
- **P04** se alinea con `2.1.B2.1`, `2.1.B2.2` y `2.1.B2.3` porque utiliza un protocolo relacional, genera asesoramiento basado en criterios justificables y propone una actualización proactiva del repositorio.

## Progresión A1-B2

| Nivel | Desempeño principal |
|---|---|
| A1 | Reconoce criterios básicos y organiza recursos sencillos |
| A2 | Selecciona con apoyo recursos ajustados a un contexto |
| B1 | Busca y cataloga de forma autónoma recursos variados |
| B2 | Aplica un protocolo, asesora a otros docentes y mejora el catálogo |

Esta progresión permite pasar de la identificación inicial de criterios a la curación avanzada de contenidos digitales con valor para el equipo docente.
