# Descargar y abrir la aplicación

## Versión portable de Windows

Esta es la opción recomendada. Funciona en Windows 10 y 11 y no necesita instalación, Python ni una cuenta de GitHub.

[Descargar la versión más reciente](https://github.com/gonvga/tfm-cdd-evaluacion/releases/latest/download/EvaluacionCDD-portable-windows.zip){ .md-button .md-button--primary }

## Instrucciones paso a paso

1. Cuando termine la descarga, abre la carpeta **Descargas**.
2. Haz clic derecho sobre `EvaluacionCDD-portable-windows.zip`.
3. Selecciona **Extraer todo** y después **Extraer**.
4. Abre la carpeta `EvaluacionCDD-portable`.
5. Haz doble clic en `EvaluacionCDD-portable.exe`.

!!! warning "No abras el programa dentro del ZIP"
    Primero debes extraer todo el contenido. El archivo `.exe` necesita permanecer junto a la carpeta `_internal`.

## Si Windows muestra «Windows protegió su PC»

La aplicación todavía no está firmada digitalmente, por lo que Windows puede mostrar una advertencia la primera vez:

1. Pulsa **Más información**.
2. Comprueba que aparece `EvaluacionCDD-portable.exe`.
3. Pulsa **Ejecutar de todas formas**.

Esta advertencia no significa que sea necesario instalar nada. Puedes consultar el [código fuente del proyecto](https://github.com/gonvga/tfm-cdd-evaluacion).

## Mover la aplicación

Puedes guardar la aplicación en el Escritorio, en otra carpeta o en una memoria USB. Mueve siempre la carpeta `EvaluacionCDD-portable` completa, no solamente el ejecutable.

## Dónde se guardan los resultados

Normalmente se guardan en:

```
EvaluacionCDD-portable/results/
```

Si esa carpeta no permite escribir, se utiliza:

```
%LOCALAPPDATA%/EvaluacionCDD/results/
```

## Solución de problemas

**Hago doble clic y no se abre**

Comprueba que has extraído el ZIP y que la carpeta `_internal` está junto al ejecutable.

**No encuentro mis resultados**

Busca primero la carpeta `results` junto al programa. Si no aparece, pega `%LOCALAPPDATA%\EvaluacionCDD\results` en la barra de direcciones del Explorador de archivos.

**Quiero empezar de nuevo**

Cierra la aplicación y vuelve a abrirla. Conserva o elimina los archivos de `results` según necesites.

---

## Información para desarrollo

Las siguientes instrucciones son únicamente para personas que quieran ejecutar o modificar el código fuente.

### Ejecutar desde el código

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

### Crear de nuevo el portable

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build_portable.ps1
```

La carpeta y el ZIP generados estarán en:

```
dist/EvaluacionCDD-portable/
dist/EvaluacionCDD-portable-windows.zip
```

### Ver esta documentación

```powershell
.\venv\Scripts\python.exe -m mkdocs serve
```

Después abre `http://127.0.0.1:8000`.
