class VisionMemoryStore:

    _last_visual_context = {}

    def save(self, sender_id, analysis, media_type="image"):
        self._last_visual_context[sender_id] = {
            "media_type": media_type,
            "analysis": analysis
        }
        return True

    def get(self, sender_id):
        return self._last_visual_context.get(sender_id)
