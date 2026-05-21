# Visión general de la arquitectura

La aplicación se basa en una arquitectura modular que separa tres responsabilidades principales:

1. **Interfaz de usuario**
2. **Núcleo de evaluación**
3. **Capa de datos**

Esta separación permite que cada prueba funcione como una unidad independiente, facilita el mantenimiento y permite incorporar nuevas actividades sin modificar toda la aplicación.

## Bloques principales

```text
Usuario
  ↓
Interfaz gráfica Flet
  ↓
Capa de presentación
  ↓
Núcleo del sistema
  ↓
Escenarios JSON / Resultados
```

## Principios de diseño

- Modularidad.
- Simplicidad técnica.
- Separación entre interfaz, lógica y datos.
- Validaciones automáticas sencillas.
- Escenarios editables mediante JSON.
- Resultados trazables en archivos independientes.
- Posibilidad de ampliar la herramienta con nuevas pruebas.
