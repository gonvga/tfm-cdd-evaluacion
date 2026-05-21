# Flujo de evaluación

El flujo de uso de la aplicación sigue una secuencia progresiva:

1. El usuario selecciona una competencia del Área 2.
2. La aplicación muestra los niveles disponibles.
3. El usuario accede al nivel correspondiente.
4. Se carga el escenario de evaluación.
5. El usuario resuelve la tarea práctica.
6. La aplicación evalúa automáticamente la respuesta.
7. Se genera un resultado.
8. El resultado se guarda en `results/`.
9. Si procede, el usuario avanza a la siguiente prueba o nivel.

## Diagrama textual

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
Resultado de evaluación
  ↓
Guardado de resultados
  ↓
Siguiente prueba o fin
```

## Progresión

La progresión respeta la lógica competencial del MRCDD:

```text
A1 → A2 → B1 → B2
```

El objetivo es evitar que el usuario realice tareas avanzadas sin haber demostrado previamente las competencias básicas.
