class DependencyContainer:
    def __init__(self):
        self.services = {}

    def register(self, name: str, service):
        self.services[name] = service
        return True

    def get(self, name: str, default=None):
        return self.services.get(name, default)

container = DependencyContainer()
