import asyncio
import time

from cache import AsyncLRU, AsyncTTL


@AsyncLRU(maxsize=128)
async def func(wait: int):
    await asyncio.sleep(wait)


@AsyncLRU(maxsize=128)
async def cache_clear_fn(wait: int):
    await asyncio.sleep(wait)


class TestClassFunc:
    @AsyncLRU(maxsize=128)
    async def obj_func(self, wait: int):
        await asyncio.sleep(wait)

    @staticmethod
    @AsyncTTL(maxsize=128, time_to_live=60, skip_args=1)
    async def skip_arg_func(arg: int, wait: int):
        await asyncio.sleep(wait)
        return wait

    @classmethod
    @AsyncLRU(maxsize=128)
    async def class_func(cls, wait: int):
        await asyncio.sleep(wait)


def test():
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(func(4))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(func(4))
    t3 = time.time()
    t_first_exec = (t2 - t1) * 1000
    t_second_exec = (t3 - t2) * 1000
    assert t_first_exec > 4000
    assert t_second_exec < 4000


def test_obj_fn():
    t1 = time.time()
    obj = TestClassFunc()
    asyncio.get_event_loop().run_until_complete(obj.obj_func(4))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(obj.obj_func(4))
    t3 = time.time()
    t_first_exec = (t2 - t1) * 1000
    t_second_exec = (t3 - t2) * 1000
    assert t_first_exec > 4000
    assert t_second_exec < 4000


def test_class_fn():
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(TestClassFunc.class_func(4))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(TestClassFunc.class_func(4))
    t3 = time.time()
    t_first_exec = (t2 - t1) * 1000
    t_second_exec = (t3 - t2) * 1000
    assert t_first_exec > 4000
    assert t_second_exec < 4000


async def _test_skip_args():
    result1 = await TestClassFunc.skip_arg_func(5, 2)
    result2 = await TestClassFunc.skip_arg_func(6, 2)
    assert result1 == result2 == 2


def test_skip_args():
    async def run_test():
        # First call with arg=5
        t1 = time.time()
        result1 = await TestClassFunc.skip_arg_func(5, 2)
        t2 = time.time()
        
        # Second call with different first arg but same second arg
        result2 = await TestClassFunc.skip_arg_func(6, 2)
        t3 = time.time()
        
        # Verify results and timing
        assert result1 == result2 == 2, f"Expected both results to be 2, got {result1} and {result2}"
        
        # First call should take ~2 seconds (cache miss)
        assert t2 - t1 >= 1.9, f"First call took {t2-t1}s, expected ~2s"
        
        # Second call should be fast (cache hit)
        assert t3 - t2 < 0.1, f"Second call took {t3-t2}s, expected < 0.1s"

    # Use a timeout to prevent hanging
    try:
        asyncio.run(asyncio.wait_for(run_test(), timeout=6.0))
    except asyncio.TimeoutError:
        raise AssertionError("Test timed out after 6 seconds")
    except Exception as e:
        raise AssertionError(f"Test failed: {str(e)}")


def test_cache_refreshing_lru():
    async def run_test():
        obj = TestClassFunc()
        # First call - cache miss
        t1 = time.time()
        await obj.obj_func(1)
        t2 = time.time()
        
        # Second call - cache hit
        await obj.obj_func(1)
        t3 = time.time()
        
        # Third call - bypass cache
        await obj.obj_func(1, use_cache=False)
        t4 = time.time()
        
        return t2 - t1, t3 - t2, t4 - t3

    # Run the async test
    t_first, t_second, t_third = asyncio.run(run_test())
    
    # Verify timing expectations
    assert t_first > t_second, "Cache miss should take longer than cache hit"
    assert abs(t_first - t_third) <= 0.1, "Cache bypass should take similar time to first call"


def test_cache_clear():
    async def run_test():
        # First call - cache miss
        t1 = time.time()
        await cache_clear_fn(1)
        t2 = time.time()
        first_duration = t2 - t1
        
        # Second call - cache hit
        await cache_clear_fn(1)
        t3 = time.time()
        second_duration = t3 - t2
        
        # Clear cache
        await cache_clear_fn.cache_clear()  # Now properly awaiting the coroutine
        await asyncio.sleep(0.1)  # Ensure cache clear takes effect
        
        # Third call - should be cache miss
        t4 = time.time()
        await cache_clear_fn(1)
        t5 = time.time()
        third_duration = t5 - t4
        
        return first_duration, second_duration, third_duration

    # Run the async test
    t_first, t_second, t_third = asyncio.run(run_test())
    
    # More precise assertions
    assert t_first >= 1, f"First call (cache miss) should take >= 1s, took {t_first}s"
    assert t_second < 0.1, f"Second call (cache hit) should be fast, took {t_second}s"
    assert t_third >= 1, f"Third call (after cache clear) should take >= 1s, took {t_third}s"


def test_cache_deep_copy():
    async def run_test():
        # Create a mutable object to cache
        data = {'count': 0}
        
        @AsyncLRU(maxsize=128)
        async def get_data():
            return data
        
        # First call - get the original data
        result1 = await get_data()
        
        # Modify the returned data
        result1['count'] += 1
        
        # Second call - should get a fresh copy
        result2 = await get_data()
        
        # Verify that the modification to result1 didn't affect result2
        assert result1['count'] == 1
        assert result2['count'] == 0
        
        # Modify original data
        data['count'] = 5
        
        # Third call - should still get the originally cached copy
        result3 = await get_data()
        assert result3['count'] == 0

    asyncio.run(run_test())


def test_skip_args_lru():
    async def run_test():
        class TestClass:
            @AsyncLRU(maxsize=128, skip_args=1)
            async def method(self, value: int) -> int:
                await asyncio.sleep(1)  # Simulate work
                return value

        obj = TestClass()
        obj2 = TestClass()

        # First call with first object
        t1 = time.time()
        result1 = await obj.method(42)
        t2 = time.time()

        # Second call with different object but same value
        result2 = await obj2.method(42)
        t3 = time.time()

        # Verify results and timing
        assert result1 == result2 == 42
        assert t2 - t1 >= 0.9, "First call should take ~1s"
        assert t3 - t2 < 0.1, "Second call should be cached"

    asyncio.run(run_test())


def test_cache_stats():
    async def run_test():
        @AsyncLRU(maxsize=128)
        async def cached_func(value: int) -> int:
            await asyncio.sleep(0.1)
            return value

        # First call - should be a miss
        await cached_func(1)
        info1 = await cached_func.cache_info()
        assert info1.hits == 0
        assert info1.misses == 1
        assert info1.currsize == 1

        # Second call with same value - should be a hit
        await cached_func(1)
        info2 = await cached_func.cache_info()
        assert info2.hits == 1
        assert info2.misses == 1
        assert info2.currsize == 1

        # Call with different value - should be a miss
        await cached_func(2)
        info3 = await cached_func.cache_info()
        assert info3.hits == 1
        assert info3.misses == 2
        assert info3.currsize == 2

        # Clear cache and verify stats reset
        await cached_func.cache_clear()
        info4 = await cached_func.cache_info()
        assert info4.hits == 0
        assert info4.misses == 0
        assert info4.currsize == 0

    asyncio.run(run_test())
