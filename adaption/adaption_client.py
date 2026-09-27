class AdaptionClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url
        self.enabled = False

    def log_interaction(self, user_input: str, assistant_response: str):
        """Stub temporal para la fase 3 del MVP. No ejecuta lógica activa todavía."""
        return {
            "status": "stubbed",
            "user_input": user_input,
            "assistant_response": assistant_response,
            "enabled": self.enabled,
        }

    def refresh_profile(self):
        return {"status": "not_implemented", "enabled": self.enabled}

    def is_enabled(self):
        return self.enabled
