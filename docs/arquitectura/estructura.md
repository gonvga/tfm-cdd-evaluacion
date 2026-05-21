# Estructura del proyecto

La estructura recomendada del repositorio es la siguiente:

```text
TFM-FORM-PROF-2025-26/
├─ assets/
├─ core/
├─ data/
├─ docs/
├─ results/
├─ ui/
├─ unit_tests/
├─ app.py
├─ mkdocs.yml
├─ README.md
└─ requirements.txt
```

## `app.py`

Punto de entrada de la aplicación. Inicializa Flet y delega la construcción de la interfaz en los módulos correspondientes.

## `core/`

Contiene la lógica principal de la aplicación:

- Registro de pruebas.
- Ejecución de pruebas.
- Modelos comunes de datos.
- Almacenamiento de resultados.
- Funciones de evaluación.

## `ui/`

Contiene las vistas y componentes visuales construidos con Flet.

## `data/`

Contiene los escenarios de evaluación en formato JSON. Esta carpeta permite modificar el contenido de las pruebas sin cambiar la lógica principal del programa.

## `results/`

Almacena los resultados generados por las pruebas.

## `unit_tests/`

Incluye pruebas unitarias para validar la lógica de evaluación y evitar regresiones al modificar la aplicación.

## `docs/`

Contiene la documentación de la web generada con MkDocs Material.
