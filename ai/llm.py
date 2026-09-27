import os
from typing import List, Optional
from dotenv import load_dotenv 
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - se importa solo si está disponible
    OpenAI = None

from ai.prompts import build_messages
load_dotenv() 

class FeatherlessAIClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("FEATHERLESS_API_KEY")
        self.base_url = base_url or os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
        self.model = model or os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.client = None

        if OpenAI is not None and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _fallback_response(self, user_input: str) -> str:
        user_input = (user_input or "").strip()
        if not user_input:
            return "MAYLLO: No recibí una entrada válida."
        return (
            "MAYLLO responde en modo local: "
            f"Entendí: '{user_input}'. "
            "Conecta Featherless AI para habilitar la respuesta real del modelo."
        )

    def chat(self, messages: List[dict], model: Optional[str] = None) -> str:
        model_name = model or self.model

        last_user_message = ""
        for message in reversed(messages):
          if message.get("role") == "user":
            last_user_message = message.get("content", "")
            break

        if self.client is None:
           return self._fallback_response(last_user_message)
    #nuestra guardia por alguna razon no se puede conectar a la IA no truene el programa
        try:
          response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
          return response.choices[0].message.content.strip()
        except Exception:
          print("ERROR FEATHERLESS:", repr(Exception))
          return self._fallback_response(last_user_message)


def generate_response(user_input: str, history=None, model: Optional[str] = None) -> str:
    history = history or []
    messages = build_messages(user_input, history)
    client = FeatherlessAIClient(model=model)
    return client.chat(messages, model=model)
