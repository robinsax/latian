'''
User I/O is comprised of two parts:

`IO`, the user I/O provider used by application logic.
`IOSource`s, the underlying sources of user I/O occurs.
'''
from .io import IO, IOWriter
from .io_source import io_sources

# Load IOSource implementations.
from . import std_source, ws_source
