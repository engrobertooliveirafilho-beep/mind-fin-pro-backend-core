
class MemoryProvider:
    def __init__(self):
        self.store = {}

    def get_recent_context(self, user_id: str):
        return self.store.get(user_id, [])[-10:]

    def append_memory(self, user_id: str, content: str):
        self.store.setdefault(user_id, []).append(content)
        return {"status": "memory_appended", "items": len(self.store[user_id])}

    def summarize_memory(self, user_id: str):
        items = self.get_recent_context(user_id)
        return " | ".join(items[-3:]) if items else "sem memória anterior"
