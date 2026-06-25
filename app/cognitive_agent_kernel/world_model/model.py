class WorldModel:
    def __init__(self):
        self.state = {}

    def update(self, event):
        self.state["last_event"] = event
        return self.state
