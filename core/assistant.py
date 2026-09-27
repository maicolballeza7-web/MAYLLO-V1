from ai.llm import generate_response
from core.intent import interpret_intent
from core.memory import ConversationMemory
from tools.applications import open_application
from tools.browser import open_browser


class Assistant:
    def __init__(self):
        self.memory = ConversationMemory()

    def respond(self, user_input: str) -> str:
        text = (user_input or "").strip()
        if not text:
            return "No te escuché. ¿Puedes repetirlo?"

        self.memory.add_user_message(text)

        intent = interpret_intent(text)

        if intent["action"] == "open_application" and intent.get("app"):
            resultado = open_application(intent["app"])
            response = f"Abriendo {intent['app']}." if resultado["status"] == "ok" else f"No pude abrir {intent['app']}."

        elif intent["action"] == "web_search":
            resultado = open_browser("https://www.google.com")
            response = "Abriendo Google." if resultado["status"] == "ok" else "No pude abrir el buscador."

        else:
            response = generate_response(text, history=self.memory.get_context())

        self.memory.add_assistant_message(response)
        return response