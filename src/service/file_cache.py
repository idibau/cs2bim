import json
import redis
import time


class FileCache:

    def __init__(self):
        self.file_cache = redis.Redis(host="redis", port=6379, db=2)

    def add(self, key, file_path: str, ttl: float = 3600):
        cache_entry = CacheEntry(file_path, ttl)
        self.file_cache.set(key, cache_entry.to_dict())

    def get(self, key):
        if self.file_cache.exists(key):
            data = json.loads(self.file_cache.get(key))
            return CacheEntry.from_dict(data)
        else:
            return None

    def delete(self, key):
        self.file_cache.delete(key)


class CacheEntry:
    def __init__(self, file_path: str, ttl: float):
        self.file_path = file_path
        self.expire_at = time.time() + ttl

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["file_path"], data["expire_at"])

    def to_dict(self):
        return json.dumps({"file_path": self.file_path, "expire_at": self.expire_at})
