import setuptools

setuptools.setup(
    name="async-cache-ext",
    version="1.1.1",
    author="doubledare704",
    author_email="doubledare704@github.com",
    description="A high-performance async caching solution for Python with extended features",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/doubledare704/async-cache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    keywords=["asyncio", "lru", "cache", "async", "cache", "lru-cache", "ttl"],
)
