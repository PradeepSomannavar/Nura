"""Cache service interface with a NoOp implementation.

Phase 1 provides a no-op cache; a Redis-backed implementation is added in a
later phase.  Consumers depend on this interface, never on a concrete impl.
"""

from __future__ import annotations

from typing import Any


class BaseCache:
    """Abstract cache interface."""

    def get(self, key: str) -> Any | None:
        """Return the cached value for ``key`` or ``None``."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store ``value`` under ``key`` with an optional TTL."""
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """Remove ``key`` from the cache."""
        raise NotImplementedError


class NoOpCache(BaseCache):
    """Cache that stores nothing (fallback / default)."""

    def get(self, key: str) -> Any | None:
        return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        return None

    def delete(self, key: str) -> None:
        return None


_cache: BaseCache = NoOpCache()


def get_cache_service() -> BaseCache:
    """Return the configured cache service singleton."""
    return _cache
