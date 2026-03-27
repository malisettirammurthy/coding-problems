"""
Decorator Pattern: Add behavior without sub classing.
Use when: you want to wrap an object to add cross cutting behavior like retry, caching and logging.
"""
from abc import ABC, abstractmethod
import time

class DatabaseProvider(ABC):
    @abstractmethod
    def provision(self, name):
        pass

    def backup(self):
        pass

class PostgresProvider(DatabaseProvider):
    def provision(self, name):
        raise Exception("Test Exception")
        return f"PostgreSQL cluster {name} provisioned"

    def backup(self):
        return "pg_basebackup + WAL archiving"

class DatabaseProviderWithRetry(DatabaseProvider):
    def __init__(self, provider, max_retries=3):
        self._provider = provider
        self._max_retries = max_retries

    def provision(self, name):
        for attempt in range(self._max_retries +1):
            try:
                return self._provider.provision(name)
            except Exception as e:
                if attempt == self._max_retries:
                    raise
                wait = 2** attempt
                print(f"Attempt {attempt} failed, retrying in {wait}s")
                time.sleep(wait)

    def backup(self):
        self._provider.backup()

provider = PostgresProvider()
provider = DatabaseProviderWithRetry(provider, max_retries=10)
# Here we've wrapped PostgresProvider with exponential retries.
# Can also wrap with a caching layer, logging layer, etc.

print(provider.provision("redis"))

