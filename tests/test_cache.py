"""
Cache Infrastructure Tests

测试缓存抽象层和内存缓存实现。
"""
import pytest
import time

from src.infrastructure.cache import CacheABC, MemoryCache


class TestMemoryCache:
    """测试内存缓存实现"""

    @pytest.fixture
    def cache(self):
        """创建测试缓存实例"""
        return MemoryCache(max_size=100, default_ttl=1)

    def test_set_and_get(self, cache):
        """测试设置和获取缓存"""
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

    def test_get_non_existent(self, cache):
        """测试获取不存在的键"""
        assert cache.get("non_existent") is None

    def test_delete(self, cache):
        """测试删除缓存"""
        cache.set("delete_key", "delete_value")
        assert cache.delete("delete_key") is True
        assert cache.get("delete_key") is None

    def test_delete_non_existent(self, cache):
        """测试删除不存在的键"""
        assert cache.delete("non_existent") is False

    def test_clear(self, cache):
        """测试清空缓存"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size() == 2

        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_exists(self, cache):
        """测试检查键是否存在"""
        assert not cache.exists("test_key")
        cache.set("test_key", "test_value")
        assert cache.exists("test_key")

    def test_get_many(self, cache):
        """测试批量获取"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        results = cache.get_many(["key1", "key2", "key4"])
        assert results == {
            "key1": "value1",
            "key2": "value2"
        }

    def test_set_many(self, cache):
        """测试批量设置"""
        cache.set_many({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_delete_many(self, cache):
        """测试批量删除"""
        cache.set_many({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        count = cache.delete_many(["key1", "key2", "key4"])
        assert count == 2
        assert cache.exists("key3")
        assert not cache.exists("key1")

    def test_incr(self, cache):
        """测试递增"""
        assert cache.incr("counter") == 1
        assert cache.incr("counter") == 2
        assert cache.incr("counter", 5) == 7

    def test_decr(self, cache):
        """测试递减"""
        cache.set("counter", 10)
        assert cache.decr("counter") == 9
        assert cache.decr("counter", 5) == 4

    def test_size(self, cache):
        """测试获取缓存大小"""
        assert cache.size() == 0
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.size() == 2

    def test_keys(self, cache):
        """测试获取所有键"""
        cache.set_many({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        keys = cache.keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys

    def test_values(self, cache):
        """测试获取所有值"""
        cache.set_many({
            "key1": "value1",
            "key2": "value2"
        })

        values = cache.values()
        assert len(values) == 2
        assert "value1" in values
        assert "value2" in values

    def test_items(self, cache):
        """测试获取所有键值对"""
        cache.set_many({
            "key1": "value1",
            "key2": "value2"
        })

        items = cache.items()
        assert len(items) == 2
        assert ("key1", "value1") in items or ("key2", "value2") in items

    def test_ttl_expiration(self, cache):
        """测试 TTL 过期"""
        cache.set("ttl_key", "ttl_value")

        # 等待过期
        time.sleep(1.5)

        # TTLCache 会自动清理过期项
        assert cache.get("ttl_key") is None

    def test_complex_values(self, cache):
        """测试复杂类型的值"""
        # 列表
        cache.set("list_key", [1, 2, 3])
        assert cache.get("list_key") == [1, 2, 3]

        # 字典
        cache.set("dict_key", {"name": "test", "value": 123})
        assert cache.get("dict_key") == {"name": "test", "value": 123}

        # 对象
        class TestObj:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        obj = TestObj(10, 20)
        cache.set("obj_key", obj)
        assert cache.get("obj_key").x == 10
        assert cache.get("obj_key").y == 20

    def test_update_existing_key(self, cache):
        """测试更新已存在的键"""
        cache.set("key", "value1")
        cache.set("key", "value2")
        assert cache.get("key") == "value2"


class TestCacheAbstraction:
    """测试缓存抽象层接口"""

    def test_cache_abc_is_abstract(self):
        """测试抽象基类不能直接实例化"""
        with pytest.raises(TypeError):
            CacheABC()
