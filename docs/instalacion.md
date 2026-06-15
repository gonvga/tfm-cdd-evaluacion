# Ejecutar la aplicación

## Versión portable de Windows

Esta es la opción recomendada. No necesita instalar Python.

1. Descomprime `EvaluacionCDD-portable-windows.zip`.
2. Abre la carpeta `EvaluacionCDD-portable`.
3. Haz doble clic en `EvaluacionCDD-portable.exe`.

No muevas solamente el `.exe`: debe permanecer junto a la carpeta `_internal`.

Windows puede mostrar una advertencia porque la aplicación no está firmada. Selecciona **Más información** y **Ejecutar de todas formas**.

## Dónde se guardan los resultados

Normalmente se guardan en:

```
EvaluacionCDD-portable/results/
```

Si esa carpeta no permite escribir, se utiliza:

```
%LOCALAPPDATA%/EvaluacionCDD/results/
```

## Ejecutar desde el código

Esta opción está pensada para desarrollo:

```
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

## Crear de nuevo el portable

```
.\venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_portable.ps1
```

La carpeta generada estará en:

```
dist/EvaluacionCDD-portable/
```

## Ver esta documentación

```
.\venv\Scripts\python.exe -m mkdocs serve
```

Después abre `http://127.0.0.1:8000`.
