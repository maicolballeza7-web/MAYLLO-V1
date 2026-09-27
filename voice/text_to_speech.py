"""Síntesis y reproducción de voz con el perfil sonoro de MAYLLO."""

import asyncio
import os
import tempfile
import wave
from array import array
from pathlib import Path

try:
    import edge_tts
except ImportError:  # pragma: no cover
    edge_tts = None

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None


VOZ_JARVIS = "es-ES-AlvaroNeural"
VELOCIDAD_JARVIS = "-12%"
_ECO_MS = 85
_ECO_MEZCLA = 0.22


async def _generate_audio(texto: str, ruta_salida: str) -> None:
    if edge_tts is None:
        raise RuntimeError("edge-tts no está instalado. Instálalo desde requirements.txt.")

    communicate = edge_tts.Communicate(
        texto,
        VOZ_JARVIS,
        rate=VELOCIDAD_JARVIS,
    )
    await communicate.save(ruta_salida)


def _apply_lab_echo(
    audio: bytes,
    frecuencia: int,
    canales: int,
    sample_width: int,
) -> bytes:
    """Añade un eco corto y discreto para dar sensación de altavoz de laboratorio."""
    if sample_width != 2:
        raise RuntimeError("pygame debe entregar audio PCM de 16 bits.")

    muestras = array("h")
    muestras.frombytes(audio)
    if os.sys.byteorder != "little":
        muestras.byteswap()

    retraso_frames = max(1, int(frecuencia * _ECO_MS / 1000))
    retraso_muestras = retraso_frames * canales
    resultado = array("h", muestras)
    for indice in range(retraso_muestras, len(muestras)):
        eco = int(muestras[indice - retraso_muestras] * _ECO_MEZCLA)
        mezclada = muestras[indice] + eco
        resultado[indice] = max(-32768, min(32767, mezclada))

    if os.sys.byteorder != "little":
        resultado.byteswap()
    return resultado.tobytes()


def _write_wav(ruta: str, audio: bytes, frecuencia: int, canales: int, sample_width: int) -> None:
    with wave.open(ruta, "wb") as archivo:
        archivo.setnchannels(canales)
        archivo.setsampwidth(sample_width)
        archivo.setframerate(frecuencia)
        archivo.writeframes(audio)


async def hablar_jarvis(texto: str) -> None:
    """Genera, procesa y reproduce una respuesta con voz institucional en español."""
    limpio = (texto or "").strip()
    if not limpio:
        return
    if pygame is None:
        raise RuntimeError("pygame no está instalado. Instálalo desde requirements.txt.")

    mp3_path = None
    wav_path = None
    canal = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temporal:
            mp3_path = temporal.name
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporal:
            wav_path = temporal.name

        await _generate_audio(limpio, mp3_path)

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        fuente = pygame.mixer.Sound(mp3_path)
        frecuencia, formato, canales = pygame.mixer.get_init()
        sample_width = abs(formato) // 8
        audio_procesado = _apply_lab_echo(
            fuente.get_raw(),
            frecuencia,
            canales,
            sample_width,
        )
        _write_wav(wav_path, audio_procesado, frecuencia, canales, sample_width)

        canal = pygame.mixer.Sound(wav_path).play()
        while canal.get_busy():
            await asyncio.sleep(0.02)
    finally:
        if canal is not None:
            canal.stop()
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.quit()
        for ruta in (mp3_path, wav_path):
            if ruta:
                Path(ruta).unlink(missing_ok=True)


def speak(text: str, language: str = "es") -> None:
    """Compatibilidad síncrona con la interfaz actual de MAYLLO."""
    limpio = (text or "").strip()
    if not limpio:
        return

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(hablar_jarvis(limpio))
    else:
        asyncio.create_task(hablar_jarvis(limpio))
