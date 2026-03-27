"""
Use when you have multiple ways to do something and want to pick at runtime without using if/else chains.
Example: Switching between backup strategies - FullBackupStrategy / IncrBackupStrategy.
"""

from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def backup(src, dest):
        pass

class FullBackupStrategy(Strategy):
    def backup(self, src, dest):
        print("Backup using Full strategy.")

class IncrBackupStrategy(Strategy):
    def backup(self, src, dest):
        print("Backup using Incr strategy.")


class BackupManager():
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def run(self, src, dest):
        self.strategy.backup(src, dest)

m = BackupManager(FullBackupStrategy())
m.run("db-id", "s3://bucket")
m.set_strategy(IncrBackupStrategy())
m.run("db-id", "s3://bucket")


