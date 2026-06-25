class ConcurrencyController:
    def lock(self, resource):
        return f"locked:{resource}"

    def unlock(self, resource):
        return f"unlocked:{resource}"
