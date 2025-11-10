from pathlib import Path

from service.file_cache import FileCache, CacheEntry
import service.file_cache as fc


class DummyRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def exists(self, key):
        return key in self.store

    def delete(self, key):
        self.store.pop(key, None)


class TestFileCache:

    def test_add_and_get_with_expiry_and_file_presence(self, monkeypatch, tmp_path):
        dummy = DummyRedis()
        monkeypatch.setattr(fc.redis, "Redis", lambda host, port, db: dummy)

        class DummyRedisCfg:
            def __init__(self):
                class DB:
                    file_cache = 0

                self.host = "localhost"
                self.port = 6379
                self.db = DB()

        class DummyCfg:
            def __init__(self):
                self.redis = DummyRedisCfg()

        monkeypatch.setattr(fc, "config", DummyCfg())

        cache = FileCache()

        file_path = tmp_path / "f.txt"
        file_path.write_text("x")
        cache.add("k1", str(file_path), ttl=1.0)

        entry = cache.get("k1")
        assert isinstance(entry, CacheEntry)
        assert Path(entry.file_path) == file_path

        file_path.unlink()
        assert cache.get("k1") is None
