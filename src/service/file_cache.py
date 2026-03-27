import json
import logging
import time
from pathlib import Path

import redis

from config.configuration import config

logger = logging.getLogger(__name__)


class CacheEntry:
    """
    Represents a cached file entry with a file path and expiration timestamp

    Attributes:
        file_path: The absolute or relative path to the cached file.
        expire_at: Timestamp indicating when the cache entry expires.
    """

    def __init__(self, file_path: str, expire_at: float):
        self.file_path = file_path
        self.expire_at = expire_at

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        """
        Create a `CacheEntry` instance from a dictionary

        Args:
            data: A dictionary containing `"file_path"` and `"expire_at"` keys.

        Returns:
            A new cache entry created from the given dictionary.
        """
        return cls(data["file_path"], data["expire_at"])

    def to_dict(self) -> str:
        """Convert the cache entry to a JSON-formatted string

        Returns:
           A JSON string representation of the cache entry.
        """
        return json.dumps({"file_path": self.file_path, "expire_at": self.expire_at})


class FileCache:
    """
    A Redis-backed cache for storing and retrieving file paths

    Attributes:
        file_cache: Redis client instance used for storing cache entries.
    """

    def __init__(self):
        self.file_cache = redis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db.file_cache)

    def add(self, key: str, file_path: str, ttl: float = 3600):
        """
        Add a file entry to the cache

        Args:
            key: The unique key used to identify the cached file.
            file_path: Path to the file to be cached.
            ttl: Time-to-live for the cache entry in seconds. Defaults to 3600 (1 hour).
        """
        cache_entry = CacheEntry(file_path, time.time() + ttl)
        self.file_cache.set(key, cache_entry.to_dict())

    def get(self, key: str) -> CacheEntry | None:
        """
        Retrieve a cache entry if it exists, is valid, and the file is present

        Args:
           The cache key identifying the file entry.

        Returns:
           The corresponding cache entry if valid, otherwise `None`.
        """
        if self.file_cache.exists(key):
            data = json.loads(self.file_cache.get(key))
            entry = CacheEntry.from_dict(data)
            if entry.expire_at > time.time():
                if Path(entry.file_path).exists():
                    logger.debug(f"using cached file: {key}")
                    return entry
                else:
                    logger.debug(f"cached file not found: {key}")
                    self.file_cache.delete(key)
            else:
                logger.debug(f"remove expired file at cache fetch: {key}")
                self.file_cache.delete(key)
                Path(entry.file_path).unlink(missing_ok=True)
        return None
