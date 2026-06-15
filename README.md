# Documentación MkDocs de la aplicación MRCDD

Este paquete contiene una propuesta completa de documentación para la web de la aplicación.

## Uso rápido

```bash
pip install mkdocs-material
mkdocs serve
```

Para publicar en GitHub Pages:

```bash
mkdocs gh-deploy
```
Para lanzarlo en local:
```bash
mkdocs serve
```

## Aplicacion de escritorio

Para ejecutar la aplicacion desde el repositorio:

```powershell
.\venv\Scripts\python.exe app.py
```

Para generar la version portable de Windows:

```powershell
.\build_portable.ps1
```

La salida se crea en `dist/EvaluacionCDD-portable`. Los resultados se guardan
en la carpeta `results` situada junto al ejecutable. Si esa ubicacion no es
escribible, se usa `%LOCALAPPDATA%\EvaluacionCDD\results`.

Antes de publicar, actualiza en `mkdocs.yml`:

- `site_url`
- `repo_url`
- `repo_name`
