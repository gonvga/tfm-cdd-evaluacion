# Desarrollo de pruebas

Las pruebas siguen una estructura común para mantener la coherencia del sistema de evaluación.

## Elementos principales de una prueba

Cada prueba incluye:

- Escenario.
- Interfaz.
- Evidencias.
- Criterios de evaluación.
- Feedback.
- Resultado.

---

## Evidencias

Una evidencia es una acción observable del usuario.

Ejemplos:

- Recursos seleccionados.
- Texto corregido.
- Licencias elegidas.
- Carpetas creadas.
- Permisos configurados.

---

## Criterios de evaluación

Los criterios definen las condiciones mínimas necesarias para superar una prueba.

Deben ser:

- Claros.
- Observables.
- Automatizables.
- Coherentes con el MRCDD.

Ejemplo:

```json
{
  "criterion": "Selecciona una licencia reutilizable",
  "required": true
}
```

---

## Crear una nueva prueba

### 1. Definir la actividad

Documentar:

- ID.
- Competencia.
- Nivel.
- Indicadores.
- Escenario.
- Evidencias.
- Criterios.

### 2. Crear el escenario JSON

Añadir el archivo correspondiente en `data/`.

### 3. Crear la vista

Añadir una vista independiente en `ui/`.

### 4. Implementar la evaluación

La lógica debe mantenerse sencilla y automática.

### 5. Registrar la prueba

Registrar la actividad en el sistema central de pruebas.

### 6. Añadir pruebas unitarias

Validar:

- Casos correctos.
- Casos incorrectos.
- Resultados generados.

---

## Validación

Las pruebas unitarias permiten comprobar:

- La carga de escenarios.
- La evaluación de respuestas.
- La generación de resultados.
- El almacenamiento de evidencias.

Ejecución:

```bash
pytest
```

---

## Actualización de contenidos

La arquitectura permite modificar:

- Escenarios.
- Recursos.
- Feedback.
- Criterios.
- Nuevas pruebas.

Sin necesidad de rediseñar toda la aplicación.
