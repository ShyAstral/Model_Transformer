## Requisitos previos
Asegúrate de tener instalado lo siguiente:

- Python 3.10 o superior  
- `pip` (administrador de paquetes de Python)

Puedes verificar la instalación con:

```bash
python --version
pip --version
```

> En algunos sistemas Linux puede ser necesario usar `python3` y `pip3`.

---

## 1. Crear y activar un entorno virtual

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows (CMD / Símbolo del sistema)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Después de activarlo, el terminal mostrará el nombre del entorno virtual, por ejemplo:

```bash
(.venv)
```

---

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Iniciar el servidor de desarrollo

```bash
fastapi dev
```

Por defecto, el backend escucha peticiones en:

```text
http://127.0.0.1:8000
```
