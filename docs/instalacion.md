# Instalación y estado actual

## Requisitos

- Python 3.10 o superior.
- Entorno virtual recomendado.
- Dependencias de `requirements.txt`.

Compatible con:

- Windows
- Linux
- macOS

---

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación

```bash
python app.py
```

---

## Ejecutar documentación

```bash
pip install mkdocs-material
mkdocs serve
```

---

## Publicar documentación

```bash
mkdocs gh-deploy
```

---

## Estado actual del proyecto

La herramienta se encuentra actualmente en una fase inicial de desarrollo.

La versión actual:

- Evalúa únicamente el Área 2 del MRCDD.
- Contempla los niveles A1-B2.
- Utiliza validaciones automáticas sencillas.
- No ha sido validada todavía con docentes en activo.

---

## Futuras mejoras

- Incorporar nuevas áreas del MRCDD.
- Añadir niveles C1 y C2.
- Implementar nuevas actividades.
- Mejorar el feedback formativo.
- Desarrollar una versión web.
- Validar la herramienta en contextos educativos reales.
