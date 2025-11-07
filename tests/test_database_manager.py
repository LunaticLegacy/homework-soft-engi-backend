import asyncio
import json
import os
import pytest

from modules.database.database_manager import DatabaseManager


TEST_DIR = os.path.join(os.path.dirname(__file__), "configs")


class DummyConnection:
    def __init__(self):
        self.closed = False

    async def fetchrow(self, query: str):
        return {"now": "dummy"}


class DummyPool:
    def __init__(self):
        self._acquired = False

    async def acquire(self, timeout: float = 5.0):
        self._acquired = True
        return DummyConnection()

    async def release(self, connection):
        self._acquired = False

    async def close(self):
        self._acquired = False


@pytest.mark.asyncio
async def test_init_pool_and_connection_flow(monkeypatch):
    # load valid config
    cfg_path = os.path.join(TEST_DIR, 'db_config_valid.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    created = {}

    def fake_create_pool(*args, **kwargs):
        # record that create_pool was called with expected keys
        created.update(kwargs)
        return DummyPool()

    monkeypatch.setattr('asyncpg.create_pool', fake_create_pool)

    db = DatabaseManager(
        db_url=cfg['db_url'],
        db_username=cfg['db_username'],
        db_password=cfg['db_password'],
        db_database_name=cfg['db_database_name'],
        db_port=cfg['db_port'],
        minconn=cfg.get('minconn', 1),
        maxconn=cfg.get('maxconn', 20),
    )

    # init pool should call our fake_create_pool
    await db.init_pool()
    assert db.connection_pool is not None
    # Check if create_pool was called with correct parameters
    assert 'user' in created and created['user'] == cfg['db_username']
    assert 'password' in created and created['password'] == cfg['db_password']
    assert 'database' in created and created['database'] == cfg['db_database_name']
    assert 'host' in created and created['host'] == cfg['db_url']
    assert 'port' in created and created['port'] == cfg['db_port']

    # get connection
    conn = await db.get_connection()
    assert hasattr(conn, 'fetchrow')

    # fetch some data
    row = await conn.fetchrow("SELECT 1")
    assert row == {"now": "dummy"} or row is not None

    # release and close
    await db.release_connection(conn)
    await db.close_all_connections()
    assert db.connection_pool is None


@pytest.mark.asyncio
async def test_init_pool_failure(monkeypatch):
    # load invalid config
    cfg_path = os.path.join(TEST_DIR, 'db_config_invalid.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    def fake_create_pool_error(*args, **kwargs):
        raise Exception('unable to reach host')

    monkeypatch.setattr('asyncpg.create_pool', fake_create_pool_error)

    db = DatabaseManager(
        db_url=cfg['db_url'],
        db_username=cfg['db_username'],
        db_password=cfg['db_password'],
        db_database_name=cfg['db_database_name'],
        db_port=cfg['db_port'],
        minconn=cfg.get('minconn', 1),
        maxconn=cfg.get('maxconn', 1),
    )

    # This should raise a ConnectionError
    with pytest.raises(ConnectionError):
        await db.init_pool()


# Test for get_connection without init
@pytest.mark.asyncio
async def test_get_connection_without_init():
    db = DatabaseManager(
        db_url="127.0.0.1",
        db_username="test",
        db_password="test",
        db_database_name="test",
        db_port=5432
    )
    with pytest.raises(ConnectionError):
        await db.get_connection()