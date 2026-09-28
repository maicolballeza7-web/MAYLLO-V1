# MAYLLO 2.0

MAYLLO is a personal multimodal AI assistant inspired by JARVIS, designed to run on a lightweight Windows desktop. It combines voice/text conversation, real actions on your computer, and hand-gesture control. Built for **GIBC V2, Track 03: Open**.

## What MAYLLO does

- **Text and voice conversation**, with a "brain" connected to Featherless AI (OpenAI-compatible API, open-source language models).
- **Speech-to-text and text-to-speech**, with an echo effect applied to the voice to sound closer to JARVIS.
- **Real function calling:** by voice or text, MAYLLO can open Spotify, VS Code, Word, Excel, PowerPoint and Google.
- **Gesture control (computer vision):** using the camera and MediaPipe, a thumb-index pinch gesture triggers a zoom-out (`Ctrl -`), with distance normalization, moving-average smoothing, two-threshold hysteresis, time cooldown and level limits to avoid erratic behavior. It works reliably in VS Code and is still being tuned for other apps.
- **Animated interface (Tkinter):** MAYLLO appears as a helmet-style icon in the corner of the screen, with a speech bubble showing the action it is executing.

## Technical research: custom LoRA model

As part of the project, a LoRA adapter was trained with Adaption Labs/AutoScientist using a hand-written dataset of 80 examples. The run on Llama-3.3-70B-Instruct reached a **0.76 win rate** against the unadapted base model. The dataset was then retrained on Llama-3.1-8B-Instruct to obtain a smaller adapter that could be served more easily.

**Transparency note:** the trained model is **not** integrated into MAYLLO's production runtime, because there is no server available to host it. The running assistant uses Featherless AI without adaptation as its brain. The dataset, training scripts and evaluation are in `adaption/`. The LoRA checkpoint (~2.5 GB) is not included in the repository because of its size.

## Project structure

- `main.py`: entry point (text mode or `--ui`).
- `core/`: assistant orchestration: `assistant.py` (main flow), `intent.py` (keyword-based intent detection), `memory.py` (in-RAM conversation memory).
- `ai/`: Featherless AI client (`llm.py`) and prompt building (`prompts.py`).
- `voice/`: speech recognition (`speech_to_text.py`) and speech synthesis with echo effect (`text_to_speech.py`).
- `tools/`: real actions: opening applications (`applications.py`), browser (`browser.py`), files (`files.py`).
- `vision/`: hand detection and pinch/zoom gesture (`hand_detector.py`, `gestures.py`, `camera.py`).
- `ui/`: animated interface with the MAYLLO character (`interface.py`).
- `adaption/`: dataset, training and evaluation scripts for the LoRA research; not part of the main runtime.

## Prerequisites

- Windows
- **Python 3.11**
- Microphone and webcam
- A Featherless AI API key

## Installation

From PowerShell, in the project root:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and add your real Featherless AI API key:

```
copy .env.example .env
```

## Usage

Text chat:

```
python main.py
```

Full animated interface:

```
python main.py --ui
```

Gesture control (computer vision), in a separate window:

```
python -m vision.hand_detector
```

Example commands (MAYLLO speaks Spanish): "abre Spotify", "abre Word", "abre VS Code".

## Known limitations

- The zoom gesture works reliably in VS Code; behavior in other applications is still being tuned.
- The LoRA adapter is not connected to the running assistant (see the transparency note above).
- Gesture control runs as a separate module and is not yet launched from the interface.

## Build an executable (optional)

```
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name Mayllo main.py
```

The executable does not include your `.env`; place it next to the `.exe` with your API key.

## Credits and AI tools used

This project was built using GitHub Copilot and Claude (Anthropic) as development assistants, and Adaption Labs/AutoScientist for training the experimental LoRA model.
