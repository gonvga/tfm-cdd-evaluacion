# Evaluación CDD

Aplicación de evaluación práctica del Área 2 del MRCDD.

## Descargar para Windows

[Descargar la versión portable más reciente](https://github.com/gonvga/tfm-cdd-evaluacion/releases/latest/download/EvaluacionCDD-portable-windows.zip)

No requiere instalación ni Python:

1. Descomprime `EvaluacionCDD-portable-windows.zip`.
2. Abre la carpeta `EvaluacionCDD-portable`.
3. Ejecuta `EvaluacionCDD-portable.exe`.

El `.exe` debe permanecer junto a la carpeta `_internal`.

Consulta la [guía detallada](https://gonvga.github.io/tfm-cdd-evaluacion/instalacion/) si Windows muestra una advertencia.

## Ejecutar desde el código

```powershell
.\venv\Scripts\python.exe app.py
```

## Crear el portable

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_portable.ps1
```

La salida se crea en:

- `dist/EvaluacionCDD-portable/`
- `dist/EvaluacionCDD-portable-windows.zip`

## Publicar una nueva versión

Al subir una etiqueta con formato `vX.Y.Z`, GitHub Actions crea el portable y lo adjunta automáticamente a una nueva Release:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

El enlace de descarga de esta página y de la documentación apuntará siempre a la Release más reciente.

## Ver la documentación

```powershell
.\venv\Scripts\python.exe -m mkdocs serve
```

Después abre `http://127.0.0.1:8000`.
