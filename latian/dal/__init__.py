'''
Persistant storage is comprised of two parts:

`DAL`, the domain-aware Data Access Layer used by application logic.
`StorageBackend`s, the schema-aware persistance mechanisms.
'''
from .dal import DAL
from .storage_backend import storage_backends

# Load StorageBackend implementations.
from . import file_system_backend
