try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None

from .text_to_speech import speak


PAUSA_FINAL_FRASE = 1.8
SILENCIO_INICIAL = 0.5
UMBRAL_FRASE = 0.3


class SpeechToText:
    def __init__(self, language: str = "es-MX"):
        self.language = language

    def listen_once(
        self,
        timeout: float = 10,
        phrase_time_limit: float | None = None,
        pause_threshold: float = PAUSA_FINAL_FRASE,
    ) -> str:
        if sr is None:
            raise RuntimeError("speech_recognition no está instalado. Instálalo desde requirements.txt.")

        recognizer = sr.Recognizer()
        recognizer.pause_threshold = pause_threshold
        recognizer.non_speaking_duration = SILENCIO_INICIAL
        recognizer.phrase_threshold = UMBRAL_FRASE
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        try:
            return recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            raise RuntimeError(f"No se pudo contactar a la API de voz: {exc}") from exc


def transcribe_audio(
    timeout: float = 10,
    phrase_time_limit: float | None = None,
    language: str = "es-MX",
    pause_threshold: float = PAUSA_FINAL_FRASE,
) -> str:
    return SpeechToText(language=language).listen_once(
        timeout=timeout,
        phrase_time_limit=phrase_time_limit,
        pause_threshold=pause_threshold,
    )
