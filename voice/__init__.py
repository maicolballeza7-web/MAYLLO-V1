"""Módulos de voz para entrada y salida de MAYLLO."""

from .speech_to_text import SpeechToText, transcribe_audio
from .text_to_speech import hablar_jarvis, speak

__all__ = ["SpeechToText", "transcribe_audio", "hablar_jarvis", "speak"]
