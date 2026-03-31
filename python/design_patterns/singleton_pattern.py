"""
Singleton — one instance shared across the application
Use for: registries, connection pools, config managers.
"""
import threading

class ConnectionPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:           # double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, max_connections: int = 10):
        if hasattr(self, '_initialized'):
            return
        self._max_connections = max_connections
        self._pool: list = []
        self._initialized = True