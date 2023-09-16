'''
Abstract base and implementation registry of storage backends.

Storage backends connect in the context of a user.
'''
from typing import TypeVar, Type, Any

from ..cli import CLIArgs
from ..model import Model
from ..common import Implementations

# TODO: Update support.
T = TypeVar('T')
class StorageBackend:
    schema: dict[str, Type[Model]]
    args: CLIArgs

    def __init__(self, schema: dict[str, Type[Model]], args: CLIArgs):
        self.schema = schema
        self.args = args

    async def initialize(self):
        raise NotImplementedError()

    async def connect(self, user: str):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()

    async def commit(self):
        raise NotImplementedError()

    async def query(
        self,
        Target: Type[T],
        filter: dict[str, Any] = None
    ) -> list[T]:
        raise NotImplementedError()

    async def create(self, model: Model):
        raise NotImplementedError()
    
    async def delete(
        self, Target: Type[T], filter: dict[str, Any] = None
    ):
        raise NotImplementedError()

storage_backends = Implementations[Type[StorageBackend]]()
