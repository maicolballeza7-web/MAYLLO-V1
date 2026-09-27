from .speech_to_text import transcribe_audio
from ai.llm import FeatherlessAIClient, generate_response 


def process_voice_command():
    user_text = transcribe_audio()

    if not user_text.strip():
        return ""

    response = generate_response(user_text)

    return response