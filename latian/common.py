from typing import TypeVar, Generic, Callable

class Exit(BaseException):
    '''Exception indicating graceful exit.'''
    pass

class Reset(BaseException):
    '''Exception indicating graceful abort of action.'''
    pass

T = TypeVar('T')
class Implementations(Generic[T]):
    '''Registry for named implementations of an interface.'''
    _registry: dict[str, T]

    def __init__(self):
        self._registry = dict()

    def implementation(self, name: str) -> Callable:
        def decorator(implementation: T):
            self._registry[name] = implementation

        return decorator

    @property
    def names(self) -> list[str]:
        return list(self._registry.keys())

    def get(self, name) -> T:
        return self._registry.get(name)
