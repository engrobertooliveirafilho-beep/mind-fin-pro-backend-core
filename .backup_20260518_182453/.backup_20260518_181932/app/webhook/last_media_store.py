class LastMediaStore:

    _store = {}

    def save(self, sender_id, media_url, media_type):

        self._store[str(sender_id)] = {
            "media_url": media_url,
            "media_type": media_type
        }

    def get(self, sender_id):

        return self._store.get(str(sender_id))
