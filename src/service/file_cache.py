import json
import logging
import time
from pathlib import Path

import redis

from config.configuration import config

logger = logging.getLogger(__name__)


class CacheEntry:
    def __init__(self, file_path: str, expire_at: float):
        self.file_path = file_path
        self.expire_at = expire_at

    @classmethod
    def from_dict(cls, data: dict) -> "CacheEntry":
        return cls(data["file_path"], data["expire_at"])

    def to_dict(self) -> str:
        return json.dumps({"file_path": self.file_path, "expire_at": self.expire_at})


class FileCache:
    def __init__(self):
        self.file_cache = redis.Redis(host=config.redis.host, port=config.redis.port, db=config.redis.db.file_cache)

    def add(self, key: str, file_path: str, ttl: float = 3600):
        cache_entry = CacheEntry(file_path, time.time() + ttl)
        self.file_cache.set(key, cache_entry.to_dict())

    def get(self, key: str) -> CacheEntry | None:
        if self.file_cache.exists(key):
            data = json.loads(self.file_cache.get(key))
            entry = CacheEntry.from_dict(data)
            if entry.expire_at > time.time():
                if Path(entry.file_path).exists():
                    logger.debug(f"Using cached file: {key}")
                    return entry
                else:
                    logger.debug(f"Cached file not found: {key}")
                    self.file_cache.delete(key)
            else:
                logger.debug(f"Remove expired file at cache fetch: {key}")
                self.file_cache.delete(key)
                Path(entry.file_path).unlink(missing_ok=True)
        return None

    def delete(self, key):
        self.file_cache.delete(key)
