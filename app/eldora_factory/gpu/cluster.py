NODES = []

def register(node):
    NODES.append(node)

def select():
    return NODES[0] if NODES else None
