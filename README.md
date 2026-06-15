# Evaluación CDD

Aplicación de evaluación práctica del Área 2 del MRCDD.

## Usar la versión portable

1. Descomprime `dist/EvaluacionCDD-portable-windows.zip`.
2. Abre la carpeta `EvaluacionCDD-portable`.
3. Ejecuta `EvaluacionCDD-portable.exe`.

El `.exe` debe permanecer junto a la carpeta `_internal`.

## Ejecutar desde el código

```
.\venv\Scripts\python.exe app.py
```

## Crear el portable

```
.\venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_portable.ps1
```

La salida se crea en `dist/EvaluacionCDD-portable`.

## Ver la documentación

```
.\venv\Scripts\python.exe -m mkdocs serve
```

Después abre `http://127.0.0.1:8000`.
