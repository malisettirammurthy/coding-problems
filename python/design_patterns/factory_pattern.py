"""
Factory Pattern: Create objects without specifying exact class.
Use when: you need to create different types based on input, without the caller caring about the concrete class.
"""

from abc import ABC, abstractmethod

class DatabaseProvider(ABC):
    @abstractmethod
    def provision(self, name):
        pass

    def backup(self):
        pass

class PostgresProvider(DatabaseProvider):
    def provision(self, name):
        return f"PostgreSQL cluster {name} provisioned"

    def backup(self):
        return "pg_basebackup + WAL archiving"

class RedisProvider(DatabaseProvider):
    def provision(self, name):
        return f"Redis cluster {name} provisioned"

    def backup(self):
        return "RDB snapshot"

class MySQLProvider(DatabaseProvider):
    def provision(self, name):
        return f"MySQL cluster {name} provisioned"

    def backup(self):
        return "mysqldump + binlog"

class DatabaseProviderFactory():
    _registry = {
        'postgres': PostgresProvider,
        'redis': RedisProvider,
        'mysql': MySQLProvider,
    }
    
    @classmethod
    def create(cls, db_type):
        provider_cls = cls._registry.get(db_type.lower())
        if not provider_cls:
            raise ValueError(f"Unsupport database type: {db_type}")
        return provider_cls()

    @classmethod
    def register(cls, db_type, provider_class):
        cls._registry[db_type] = provider_class


# DatabaseProviderFactory.register('mongodb', MongoDBProvider)
database_obj = DatabaseProviderFactory.create('redis')
print(database_obj.provision('cache_cluster'))
print(database_obj.backup())
