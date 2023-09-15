'''
Runtimes control the top-level execution of the program.

They are implemented as asynchronous functions that take factories as
input.
'''
from .runtime import Runtime, runtimes

# Load runtime implementations.
from . import simple_runtime, multi_runtime
