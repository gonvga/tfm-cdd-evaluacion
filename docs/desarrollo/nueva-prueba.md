# Añadir una nueva prueba

Para añadir una nueva prueba se recomienda seguir siempre el mismo patrón.

## 1. Definir la prueba

Antes de programar, documenta:

- ID de prueba.
- Competencia.
- Nivel.
- Indicadores MRCDD.
- Objetivo.
- Escenario.
- Evidencia esperada.
- Criterios de evaluación.

## 2. Crear el escenario JSON

Añade un archivo en `data/` con los datos de la prueba.

## 3. Crear la vista

Añade una vista independiente en `ui/` siguiendo el estilo de las pruebas existentes.

## 4. Implementar la lógica de evaluación

La lógica debe ser sencilla, automática y coherente con los criterios definidos.

## 5. Registrar la prueba

Incluye la prueba en el sistema de registro para que la aplicación pueda cargarla.

## 6. Añadir pruebas unitarias

Crea pruebas en `unit_tests/` para comprobar:

- Respuestas correctas.
- Respuestas incorrectas.
- Casos límite.
- Formato del resultado generado.

## 7. Actualizar documentación

Añade o completa la página correspondiente en `docs/pruebas/`.
