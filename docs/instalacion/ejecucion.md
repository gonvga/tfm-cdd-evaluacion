# Ejecución

## 1. Crear entorno virtual

```bash
python -m venv venv
```

## 2. Activar entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

En macOS o Linux:

```bash
source venv/bin/activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

```bash
python app.py
```

## 5. Ejecutar la documentación local

Para visualizar esta documentación con MkDocs Material:

```bash
pip install mkdocs-material
mkdocs serve
```

Después, abre en el navegador la dirección que indique la terminal, normalmente:

```text
http://127.0.0.1:8000/
```

## 6. Publicar en GitHub Pages

```bash
mkdocs gh-deploy
```

Antes de publicar, revisa en `mkdocs.yml` los campos `site_url`, `repo_url` y `repo_name`.
