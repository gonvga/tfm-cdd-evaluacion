# Criterios y evidencias

## Qué es una evidencia

Una evidencia es una acción observable del usuario que permite valorar su desempeño.

Ejemplos:

- Recursos seleccionados.
- Carpetas creadas.
- Texto corregido.
- Campos completados.
- Permisos configurados.
- Metadatos publicados.
- Licencias seleccionadas.

## Criterios de evaluación

Los criterios definen las condiciones mínimas para considerar superada una prueba.

Deben ser:

- Claros.
- Observables.
- Automatizables.
- Coherentes con los indicadores MRCDD.
- Fáciles de mantener.

## Ejemplo de criterio

```json
{
  "criterion": "Selecciona una licencia compatible con reutilización educativa",
  "required": true,
  "accepted_values": ["CC BY", "CC BY-SA"]
}
```

## Resultado

El resultado debe indicar:

- Si la prueba está superada.
- Qué criterios se han cumplido.
- Qué criterios no se han cumplido.
- Qué evidencia ha generado el usuario.
- Qué feedback recibe.
