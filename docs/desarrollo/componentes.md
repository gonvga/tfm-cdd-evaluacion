# Componentes principales

## Registro de pruebas

El registro de pruebas define qué actividades están disponibles y en qué orden se presentan.

Su función principal es centralizar la información de las pruebas para que puedan cargarse de forma dinámica.

## Runner

El runner u orquestador coordina la ejecución de las pruebas. Se encarga de:

- Cargar la prueba seleccionada.
- Ejecutar su lógica.
- Recoger la respuesta.
- Generar el resultado.
- Guardar la evidencia.

## Modelos

Los modelos definen estructuras comunes para representar resultados, evidencias y metadatos de las pruebas.

Esto permite que todas las pruebas generen resultados con un formato coherente.

## Vistas

Las vistas contienen la interfaz de usuario de cada prueba. Cada vista debe mantener una complejidad baja y delegar la lógica de evaluación en funciones separadas.

## Escenarios

Los escenarios se definen en JSON y contienen los datos editables de cada actividad:

- Enunciado.
- Recursos.
- Opciones.
- Criterios de corrección.
- Retroalimentación.
