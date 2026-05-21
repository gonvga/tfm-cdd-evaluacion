# Escenarios JSON

Los escenarios JSON permiten separar los datos de la lógica de la aplicación.

## Ventajas

- Facilitan la edición de pruebas.
- Evitan modificar código para cambiar textos o recursos.
- Permiten adaptar actividades a otros contextos educativos.
- Mejoran el mantenimiento.
- Favorecen la escalabilidad.

## Estructura orientativa

```json
{
  "id": "P01",
  "title": "Detectar recursos adecuados",
  "competence": "2.1",
  "level": "A1",
  "description": "Selecciona los recursos adecuados para trabajar hábitos saludables.",
  "resources": [],
  "criteria": [],
  "feedback": {
    "success": "Has seleccionado los recursos adecuados.",
    "error": "Revisa los criterios de calidad, accesibilidad y adecuación didáctica."
  }
}
```

## Recomendaciones

- Usar IDs estables.
- Mantener nombres claros.
- Evitar textos excesivamente largos en una misma propiedad.
- Separar recursos, opciones y criterios.
- Incluir feedback formativo siempre que sea posible.
