# MAYLLO 2.0

MAYLLO 2.0 es un asistente de IA multimodal personal pensado para un entorno de escritorio ligero. La prioridad del MVP es validar el flujo principal en el orden correcto:

1. Core + API de IA en texto
2. Reconocimiento y respuesta por voz
3. Integración con Adaption Labs

La interfaz de tkinter y la detección de mano existente se mantienen como parte del proyecto, pero quedan fuera del camino principal del MVP.

## Estructura

- `main.py` — punto de entrada.
- `core/` — orquestación del flujo del asistente.
- `ai/` — cliente Featherless AI compatible con OpenAI.
- `voice/` — STT y TTS.
- `adaption/` — stub para la fase 3.
- `vision/` — módulo de detección manual ya existente, mantenido para post-MVP.
- `ui/` — interfaz tkinter con el personaje animado.
- `tools/` — integraciones básicas para apps, navegador y archivos.

## Ejecución

### Chat por texto

```bash
python main.py
```

### Interfaz animada

```bash
python main.py --ui
```

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores reales:

```bash
copy .env.example .env
```

## Dependencias

```bash
pip install -r requirements.txt
```

## Instalación y compilación completa en Windows

Desde PowerShell, situado en la raíz del proyecto:

```powershell
cd "C:\Users\Conne\OneDrive\Documentos\MAYLLO-2.0"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Python no genera un ejecutable nativo al "compilar" los archivos `.py`. Para
validar que todos los módulos compilan a bytecode:

```powershell
python -m compileall -q .
```

Para ejecutar la aplicación completa:

```powershell
python main.py --ui
```

La visión se prueba en una ventana independiente:

```powershell
python -m vision.hand_detector
```

Opcionalmente, para generar ejecutables de Windows instala PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name Mayllo main.py
python -m PyInstaller --noconfirm --clean --windowed --name MaylloVision vision\hand_detector.py
```

Los ejecutables quedan en `dist\Mayllo\Mayllo.exe` y
`dist\MaylloVision\MaylloVision.exe`. Ejecuta ambos si quieres usar la
interfaz y la cámara al mismo tiempo. El zoom actúa sobre la ventana que tenga
el foco.

Si ya estaba instalada una versión 1.x de MediaPipe, reinstala la versión
compatible con el detector de manos:

```bash
python -m pip install --upgrade "mediapipe==0.10.21"
```

## Nota sobre la API

El cliente en `ai/llm.py` usa el formato compatible con OpenAI y puede responder con un fallback local si no hay clave activa de Featherless AI. Esto facilita probar el flujo sin romper la demo cuando la clave no esté configurada.
