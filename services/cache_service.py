from diskcache import Cache

class CacheService:

    def __init__(self, cache_dir: str = "./cache"):
        self.cache = Cache(cache_dir)

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value, expire: int = None):
        self.cache.set(key, value, expire=expire)

    def delete(self, key: str):
        return self.cache.delete(key)

    def close(self):
        self.cache.close()