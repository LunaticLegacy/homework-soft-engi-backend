from setuptools import setup, find_packages

setup(
    name="db_io_lib",
    version="0.1.0",
    author="Klima",
    author_email="1161863146@qq.com",
    description="A unified library for asynchronous database and cache I/O operations.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Climate455/homework-soft-engi-backend",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
    ],
    python_requires=">=3.13",
    install_requires=[
        "asyncpg>=0.27.0",
        "redis>=4.5.0",
    ],
)