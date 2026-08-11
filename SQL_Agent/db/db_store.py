'''used to execute query in the data base that can be accesed globally
'''
"""Module-level store for SQL Agent database engine using context-local storage.
This ensures concurrency safety across multiple API connections.
"""

import sys
import contextvars
from types import ModuleType

# Thread and async-safe ContextVar to hold the engine reference per execution task.
_global_engine = contextvars.ContextVar("global_engine", default=None)

class DBStoreModule(ModuleType):
    @property
    def GLOBAL_ENGINE(self):
        """Dynamically retrieve the engine from context-local storage."""
        return _global_engine.get()
    
    @GLOBAL_ENGINE.setter
    def GLOBAL_ENGINE(self, value):
        """Set the engine reference for the current execution context."""
        _global_engine.set(value)

# Hot-swap the module class with our custom class to intercept attribute access
sys.modules[__name__].__class__ = DBStoreModule
