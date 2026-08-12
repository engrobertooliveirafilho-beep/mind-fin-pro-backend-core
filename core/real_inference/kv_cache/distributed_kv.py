class DistributedKVCache:
    def __init__(self):
        self.cache = {}

    def write(self, key, value):
        self.cache[key] = value

    def read(self, key):
        return self.cache.get(key)
