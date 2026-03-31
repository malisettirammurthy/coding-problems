"""
Singleton Connection Pool — module-level pattern
=================================================
Demonstrates:
  - Module-level singleton (simpler than __new__ + Lock)
  - Thread-safe acquire/release with threading.Semaphore
  - Context manager support (with pool.connection() as conn)
  - Integration with DatabaseProvider + CircuitBreaker from earlier patterns
"""

from __future__ import annotations

import threading
import time
import contextlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


# ─────────────────────────────────────────────
# Simulated connection (stands in for psycopg2,
# redis-py, pymongo, etc.)
# ─────────────────────────────────────────────

@dataclass
class Connection:
    db_url: str
    conn_id: int
    _closed: bool = field(default=False, repr=False)

    def execute(self, query: str) -> str:
        if self._closed:
            raise RuntimeError(f"Connection {self.conn_id} is closed")
        # simulate query latency
        time.sleep(0.01)
        return f"[conn-{self.conn_id}] OK: {query}"

    def close(self) -> None:
        self._closed = True

    @property
    def is_alive(self) -> bool:
        return not self._closed


# ─────────────────────────────────────────────
# Connection Pool
# ─────────────────────────────────────────────

class ConnectionPool:
    """
    Fixed-size connection pool.

    - Semaphore blocks callers when all connections are in use
      instead of failing immediately — correct back-pressure.
    - A separate Lock guards the free-list to prevent two threads
      from grabbing the same connection simultaneously.
    - Stale connection detection on every acquire.
    """

    def __init__(self, db_url: str, max_connections: int = 5):
        self._db_url = db_url
        self._max_connections = max_connections
        self._semaphore = threading.Semaphore(max_connections)
        self._lock = threading.Lock()
        self._all: list[Connection] = []
        self._free: list[Connection] = []
        self._conn_counter = 0
        self._initialized = True

        # pre-warm the pool
        for _ in range(max_connections):
            conn = self._create_connection()
            self._all.append(conn)
            self._free.append(conn)

        print(f"[Pool] Initialized: {max_connections} connections to {db_url}")

    # ── internal ──────────────────────────────

    def _create_connection(self) -> Connection:
        self._conn_counter += 1
        return Connection(db_url=self._db_url, conn_id=self._conn_counter)

    def _is_stale(self, conn: Connection) -> bool:
        return not conn.is_alive

    def _replace_stale(self, conn: Connection) -> Connection:
        self._all.remove(conn)
        conn.close()
        fresh = self._create_connection()
        self._all.append(fresh)
        print(f"[Pool] Replaced stale conn-{conn.conn_id} → conn-{fresh.conn_id}")
        return fresh

    # ── public API ────────────────────────────

    def acquire(self, timeout: float = 5.0) -> Connection:
        """
        Block until a connection is available (up to `timeout` seconds).
        Raises RuntimeError if pool is exhausted within the timeout.
        """
        acquired = self._semaphore.acquire(timeout=timeout)
        if not acquired:
            raise RuntimeError(
                f"[Pool] No connection available within {timeout}s "
                f"(pool size: {self._max_connections})"
            )
        with self._lock:
            conn = self._free.pop()
            if self._is_stale(conn):
                conn = self._replace_stale(conn)
            return conn

    def release(self, conn: Connection) -> None:
        """Return a connection to the pool."""
        with self._lock:
            self._free.append(conn)
        self._semaphore.release()

    @contextlib.contextmanager
    def connection(self, timeout: float = 5.0) -> Iterator[Connection]:
        """
        Context manager — preferred usage:

            with pool.connection() as conn:
                result = conn.execute("SELECT 1")
        """
        conn = self.acquire(timeout=timeout)
        try:
            yield conn
        finally:
            self.release(conn)

    # ── observability ─────────────────────────

    @property
    def available(self) -> int:
        return len(self._free)

    @property
    def in_use(self) -> int:
        return self._max_connections - len(self._free)

    def stats(self) -> dict:
        return {
            "db_url": self._db_url,
            "max_connections": self._max_connections,
            "available": self.available,
            "in_use": self.in_use,
        }


# ─────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────
#
# Why this beats __new__ + Lock:
#   - Python's import system guarantees a module is executed exactly
#     once — sys.modules caches it. Concurrent importers block on the
#     import lock, so there is no race condition at initialisation.
#   - No metaclass machinery, no _initialized guard, no double-checked
#     locking — the runtime gives you all of that for free.
#   - Still fully testable: call reset_pool() between tests.

_pool: ConnectionPool | None = None
_pool_lock = threading.Lock()          # guards first-time creation only


def get_pool(
    db_url: str = "postgres://localhost:5432/provisioning",
    max_connections: int = 5,
) -> ConnectionPool:
    """
    Return the shared ConnectionPool, creating it on first call.

    Subsequent calls ignore `db_url` and `max_connections` —
    the pool is already configured.  This mirrors how a real
    application passes config once at startup and relies on the
    singleton thereafter.
    """
    global _pool
    if _pool is None:                  # fast path — no lock needed after init
        with _pool_lock:
            if _pool is None:          # re-check after acquiring lock
                _pool = ConnectionPool(db_url=db_url, max_connections=max_connections)
    return _pool


def reset_pool() -> None:
    """
    Tear down the singleton — use in tests only.
    Closes all connections and clears the module-level reference.
    """
    global _pool
    with _pool_lock:
        if _pool is not None:
            for conn in _pool._all:
                conn.close()
            _pool = None
    print("[Pool] Reset — singleton cleared")


# ─────────────────────────────────────────────
# DatabaseProvider (from Factory pattern)
# integrated with the singleton pool
# ─────────────────────────────────────────────

class DatabaseProvider(ABC):
    @abstractmethod
    def provision(self, name: str) -> str: ...

    @abstractmethod
    def backup(self) -> str: ...


class PostgresProvider(DatabaseProvider):
    """Uses the shared pool — doesn't own connections."""

    def provision(self, name: str) -> str:
        pool = get_pool()
        with pool.connection() as conn:
            return conn.execute(f"CREATE DATABASE {name}")

    def backup(self) -> str:
        pool = get_pool()
        with pool.connection() as conn:
            return conn.execute("SELECT pg_start_backup('base')")


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

def _demo_sequential() -> None:
    print("\n── Sequential usage ──────────────────────")
    provider = PostgresProvider()

    result = provider.provision("payments_db")
    print(f"provision → {result}")

    result = provider.backup()
    print(f"backup    → {result}")

    print(f"Pool stats: {get_pool().stats()}")


def _demo_concurrent() -> None:
    print("\n── Concurrent usage (10 threads, pool size 5) ──")
    errors: list[str] = []
    results: list[str] = []
    lock = threading.Lock()

    def task(thread_id: int) -> None:
        try:
            pool = get_pool()
            with pool.connection(timeout=3.0) as conn:
                r = conn.execute(f"SELECT now() -- thread {thread_id}")
                with lock:
                    results.append(r)
                    print(f"  thread-{thread_id:02d} → {r}")
        except Exception as e:
            with lock:
                errors.append(str(e))
                print(f"  thread-{thread_id:02d} ERROR: {e}")

    threads = [threading.Thread(target=task, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nCompleted: {len(results)} ok, {len(errors)} errors")
    print(f"Pool stats: {get_pool().stats()}")


def _demo_same_instance() -> None:
    print("\n── Singleton identity check ──────────────")
    pool_a = get_pool()
    pool_b = get_pool()
    pool_c = get_pool(db_url="postgres://other-host/ignored")  # config ignored

    print(f"pool_a is pool_b: {pool_a is pool_b}")   # True
    print(f"pool_b is pool_c: {pool_b is pool_c}")   # True
    print(f"id(pool_a): {id(pool_a)}")
    print(f"id(pool_b): {id(pool_b)}")


def _demo_reset_for_tests() -> None:
    print("\n── Test isolation with reset_pool() ──────")
    pool1 = get_pool(db_url="postgres://host-a/db", max_connections=3)
    print(f"Before reset — url: {pool1._db_url}, max: {pool1._max_connections}")

    reset_pool()

    pool2 = get_pool(db_url="postgres://host-b/test_db", max_connections=2)
    print(f"After reset  — url: {pool2._db_url}, max: {pool2._max_connections}")
    print(f"Different instances: {pool1 is not pool2}")


if __name__ == "__main__":
    _demo_sequential()
    _demo_concurrent()
    _demo_same_instance()
    _demo_reset_for_tests()