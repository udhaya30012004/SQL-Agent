"""Module-level store for Pandas Agent DataFrame using context-local storage.
This ensures concurrency safety across multiple API connections and sessions.
"""

import sys
import contextvars
from types import ModuleType

# Thread and async-safe ContextVar to hold the DataFrame reference per execution task.
_global_df = contextvars.ContextVar("global_df", default=None)

class DataStoreModule(ModuleType):
    @property
    def GLOBAL_DF(self):
        """Dynamically retrieve the DataFrame from context-local storage."""
        return _global_df.get()
    
    @GLOBAL_DF.setter
    def GLOBAL_DF(self, value):
        """Set the DataFrame reference for the current execution context."""
        _global_df.set(value)

# Hot-swap the module class with our custom class to intercept attribute access
sys.modules[__name__].__class__ = DataStoreModule
