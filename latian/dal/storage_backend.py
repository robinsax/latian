'''
Abstract base and implementation registry of storage backends.

Storage backends connect in the context of a user.
'''
from enum import Enum
from typing import TypeVar, Union, Type, Any

from ..cli import CLIArgs
from ..model import Model
from ..common import ImplementationRegistry

storage_backends = ImplementationRegistry()

class Aggregation(Enum):
    sum = 'sum'

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
        filter: dict[str, Any] = None,
        aggregation: tuple[Aggregation, str] = None
    ) -> Union[list[T], int]:
        raise NotImplementedError()

    async def create(self, model: Model):
        raise NotImplementedError()
    
    async def delete(
        self, Target: Type[T], filter: dict[str, Any] = None
    ):
        raise NotImplementedError()
