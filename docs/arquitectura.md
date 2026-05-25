# Arquitectura

La aplicación se basa en una arquitectura modular que separa la interfaz de usuario, la lógica de evaluación y la gestión de datos.

## Estructura del proyecto

```text
tfm-cdd-evaluacion/
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

## Bloques principales

### `app.py`

Punto de entrada de la aplicación.

### `core/`

Contiene la lógica principal:

- Registro de pruebas.
- Runner de evaluación.
- Modelos comunes.
- Gestión de resultados.
- Funciones de validación.

### `ui/`

Contiene las vistas y componentes visuales desarrollados con Flet.

### `data/`

Contiene los escenarios de evaluación en formato JSON.

### `results/`

Almacena los resultados generados por las pruebas.

### `unit_tests/`

Incluye pruebas unitarias para validar la lógica de evaluación.

---

## Flujo general

```text
Inicio
  ↓
Selección de competencia
  ↓
Selección de nivel
  ↓
Carga de escenario JSON
  ↓
Interacción del usuario
  ↓
Evaluación automática
  ↓
Resultado
  ↓
Guardado de evidencias
```

---

## Arquitectura modular

Cada prueba funciona como un módulo independiente que incluye:

- Interfaz.
- Escenario.
- Lógica de evaluación.
- Criterios.
- Evidencias.

Esto permite añadir nuevas pruebas sin modificar la estructura principal de la aplicación.

---

## Escenarios JSON

Los escenarios JSON permiten separar los datos de la lógica del programa.

Ejemplo:

```json
{
  "id": "P01",
  "title": "Detectar recursos adecuados",
  "competence": "2.1",
  "level": "A1"
}
```

Esta separación facilita:

- El mantenimiento.
- La reutilización.
- La escalabilidad.
- La adaptación a distintos contextos educativos.

---

## Persistencia

Los resultados se almacenan automáticamente en archivos independientes dentro de `results/`.

La información almacenada puede incluir:

- ID de prueba.
- Nivel evaluado.
- Evidencias generadas.
- Criterios cumplidos.
- Resultado global.
- Fecha y hora.
