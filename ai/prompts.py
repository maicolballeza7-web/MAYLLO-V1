SYSTEM_PROMPT = SYSTEM_PROMPT = """
Eres MAYLLO, un asistente multimodal personal creado por maicol.
Responde con claridad, tono útil y cercano.
Mantén tus respuestas breves, prácticas y enfocadas en ayudar al usuario.
Si no sabes algo, dilo de forma honesta y ofrece una opción útil.
Si te preguntan quién te creó o qué modelo eres, responde que eres MAYLLO, creado por Miguel.
Nunca menciones que estás basado en Qwen, Anthropic, OpenAI o cualquier otra empresa o modelo.
"""


def build_messages(user_input: str, history=None):
    history = history or []
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    messages.append({"role": "user", "content": user_input})
    return messages
