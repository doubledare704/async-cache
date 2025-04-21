import asyncio
import time

from cache import AsyncTTL


@AsyncTTL(time_to_live=60)
async def long_expiration_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@AsyncTTL(time_to_live=5)
async def short_expiration_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@AsyncTTL(time_to_live=3)
async def short_cleanup_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@AsyncTTL(time_to_live=3)
async def cache_clear_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


def cache_hit_test():
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(long_expiration_fn(4))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(long_expiration_fn(4))
    t3 = time.time()
    t_first_exec = (t2 - t1) * 1000
    t_second_exec = (t3 - t2) * 1000
    assert t_first_exec > 4000
    assert t_second_exec < 4000


def cache_expiration_test():
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
    t3 = time.time()
    time.sleep(5)
    t4 = time.time()
    asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
    t5 = time.time()
    t_first_exec = (t2 - t1) * 1000
    t_second_exec = (t3 - t2) * 1000
    t_third_exec = (t5 - t4) * 1000
    assert t_first_exec > 1000
    assert t_second_exec < 1000
    assert t_third_exec > 1000


def test_cache_refreshing_ttl():
    async def run_test():
        # First call - cache miss
        t1 = time.time()
        await short_cleanup_fn(1)
        t2 = time.time()

        # Second call - cache hit
        await short_cleanup_fn(1)
        t3 = time.time()

        # Third call - bypass cache
        await short_cleanup_fn(1, use_cache=False)
        t4 = time.time()

        return t2 - t1, t3 - t2, t4 - t3

    # Run the async test
    t_first, t_second, t_third = asyncio.run(run_test())

    # Verify timing expectations
    assert t_first > t_second, "Cache miss should take longer than cache hit"
    assert abs(t_first - t_third) <= 0.1, (
        "Cache bypass should take similar time to first call"
    )


def cache_clear_test():
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
    t2 = time.time()
    asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
    t3 = time.time()
    cache_clear_fn.cache_clear()
    asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
    t4 = time.time()

    assert t2 - t1 > 1, t2 - t1  # Cache miss
    assert t3 - t2 < 1, t3 - t2  # Cache hit
    assert t4 - t3 > 1, t4 - t3  # Cache miss


if __name__ == "__main__":
    cache_hit_test()
    cache_expiration_test()
    test_cache_refreshing_ttl()
    cache_clear_test()
