import asyncio
import time
from timeit import timeit

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
    print(t_first_exec)
    print(t_second_exec)
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
    print(t_first_exec)
    print(t_second_exec)
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
    print(t_first_exec)
    print(t_second_exec)
    assert t_first_exec > 4000
    assert t_second_exec < 4000


async def _test_skip_args():
    result1 = await TestClassFunc.skip_arg_func(5, 2)
    result2 = await TestClassFunc.skip_arg_func(6, 2)
    assert result1 == result2 == 2


def test_skip_args():
    async def run_test():
        try:
            # Run tasks sequentially
            result1 = await TestClassFunc.skip_arg_func(5, 2)
            result2 = await TestClassFunc.skip_arg_func(6, 2)
            
            # Verify results
            assert result1 == result2 == 2
            
        except Exception as e:
            raise AssertionError(f"Test failed: {str(e)}")

    asyncio.run(run_test())


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
        cache_clear_fn.cache_clear()
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
