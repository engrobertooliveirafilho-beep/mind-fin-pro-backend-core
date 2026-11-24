_TOOL_REGISTRY = {}

def register_tool(name):
    def wrapper(func):
        if name in _TOOL_REGISTRY:
            raise ValueError('Duplicate tool')
        _TOOL_REGISTRY[name] = func
        return func
    return wrapper

def get_tool(name):
    return _TOOL_REGISTRY[name]

def list_tools():
    return {name: fn.__doc__ or '' for name, fn in _TOOL_REGISTRY.items()}
