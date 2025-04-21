import setuptools

setuptools.setup(
    name="async-cache",
    version="1.1.1",
    author="Rajat Singh",
    author_email="iamsinghrajat@gmail.com",
    description="An asyncio Cache",
    long_description="""
# A high-performance async caching solution for Python
A lightweight, efficient caching solution designed specifically for asyncio applications.
Supports both LRU (Least Recently Used) and TTL (Time To Live) caching strategies with a clean, decorator-based API.
""",
    long_description_content_type="text/x-rst",
    url="https://github.com/iamsinghrajat/async-cache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.3",
    keywords=["asyncio", "lru", "cache", "async", "cache", "lru-cache", "ttl"],
)
