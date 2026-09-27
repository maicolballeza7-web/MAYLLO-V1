# MAYLLO 2.0

MAYLLO es un asistente de IA multimodal personal, inspirado en JARVIS, pensado para
correr en un entorno de escritorio ligero (Windows). Combina conversación por voz/texto,
ejecución de acciones reales en la computadora, y control por gestos de mano.

## Qué hace MAYLLO

- **Conversación por texto y voz**, con un "cerebro" conectado a Featherless AI
  (API compatible con OpenAI, modelos de lenguaje open-source).
- **Reconocimiento de voz (STT)** y **síntesis de voz (TTS)**, con un efecto de eco
  aplicado a la voz para acercarla al sonido de JARVIS.
- **Function calling real**: por voz o texto, MAYLLO puede abrir Spotify, VS Code,
  Word, Excel, PowerPoint y realizar búsquedas en Google.
- **Control gestual por visión computacional**: usando la cámara y MediaPipe, un
  gesto de pellizco (pulgar-índice) controla el zoom de la aplicación activa
  (`Ctrl +` / `Ctrl -`), con normalización de distancia, suavizado por promedio
  móvil, histéresis de dos umbrales, cooldown de tiempo y límites de nivel para
  evitar comportamiento errático.
- **Interfaz visual animada** (Tkinter/CustomTkinter): MAYLLO aparece como un ícono
  tipo casco en la esquina de la pantalla, con una burbuja que indica la acción que
  está ejecutando.

## Investigación técnica: modelo propio con LoRA

Como parte del proyecto, se entrenó un adaptador LoRA sobre Llama-3.1-8B-Instruct
(con un dataset propio de 80 ejemplos curados a mano, vía Adaption Labs/AutoScientist),
logrando un win rate de 0.76 contra el modelo base sin adaptar.

**Nota de transparencia:** este modelo entrenado NO está integrado en el runtime de
producción de MAYLLO por limitaciones de infraestructura (no se cuenta con servidor
propio para servirlo de forma persistente). El asistente en producción usa Featherless
AI sin adaptar como cerebro. El checkpoint, el proceso de entrenamiento y las métricas
de evaluación están documentados en `adaption/` como evidencia del trabajo técnico
realizado.

## Estructura

- `main.py` — punto de entrada (modo texto o `--ui`).
- `core/` — orquestación del asistente: `assistant.py` (flujo principal),
  `intent.py` (detección de intención por palabras clave), `memory.py`
  (memoria conversacional en RAM).
- `ai/` — cliente de Featherless AI (`llm.py`) y construcción de prompts (`prompts.py`).
- `voice/` — reconocimiento de voz (`speech_to_text.py`), síntesis de voz con efecto
  de eco (`text_to_speech.py`).
- `tools/` — ejecución de acciones reales: apertura de aplicaciones (`applications.py`),
  navegador (`browser.py`), archivos (`files.py`).
- `vision/` — detección de manos y gesto de pellizco/zoom (`hand_detector.py`,
  `gestures.py`, `camera.py`).
- `ui/` — interfaz gráfica animada con el personaje MAYLLO (`interface.py`).
- `adaption/` — scripts de entrenamiento e investigación con Adaption Labs
  (dataset, entrenamiento, evaluación); no forma parte del runtime principal.

## Instalación

Desde PowerShell, en la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuración

Copia `.env.example` a `.env` y completa tu API key real de Featherless AI:

```powershell
copy .env.example .env
```

## Ejecución

**Chat por texto:**
```powershell
python main.py
```

**Interfaz animada completa:**
```powershell
python main.py --ui
```

**Control por gestos (visión), en una ventana aparte:**
```powershell
python -m vision.hand_detector
```

## Generar ejecutable (opcional)

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name Mayllo main.py
```

## Créditos y herramientas de IA usadas

Este proyecto fue construido usando GitHub Copilot y Claude (Anthropic) como
asistentes de desarrollo, y Adaption Labs/AutoScientist para el entrenamiento
del modelo LoRA experimental.
