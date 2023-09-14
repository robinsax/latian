MODES = ('rep', 'timed')

class Exit(BaseException): pass

class ImplementationRegistry:
    _registry: dict = None

    def __init__(self):
        self._registry = dict()

    def implementation(self, name: str):
        def decorator(implementation):
            self._registry[name] = implementation

        return decorator

    @property
    def names(self):
        return list(self._registry.keys())

    def get(self, name):
        return self._registry.get(name)
