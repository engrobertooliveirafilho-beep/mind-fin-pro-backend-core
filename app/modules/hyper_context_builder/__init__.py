from copy import deepcopy

class HyperContextBuilder:
    def __init__(self):
        self.layers = []

    def add_layer(self, name: str, data: dict):
        if not isinstance(name, str) or not name.strip() or not isinstance(data, dict):
            raise ValueError('Invalid layer')
        if any(layer['name'] == name for layer in self.layers):
            raise ValueError('Duplicate layer')
        self.layers.append({'name': name, 'data': deepcopy(data)})

    def build(self) -> dict:
        return {layer['name']: deepcopy(layer['data']) for layer in self.layers}
