class ConversationMemory:
    def __init__(self):
        self.messages = []

    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def add_assistant_message(self, text: str):
        self.messages.append({"role": "assistant", "content": text})

    def get_context(self):
        return list(self.messages)

    def clear(self):
        self.messages.clear()
