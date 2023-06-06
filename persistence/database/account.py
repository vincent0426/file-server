from base import do
from base.enums import RoleType
from typing import Sequence
import exceptions as exc

import asyncpg

from .util import pyformat2psql
from . import pool_handler
import uuid

async def add(username: str, password: str, pub_key: str) -> int:
    userID = uuid.uuid4()
    sql, params = pyformat2psql(
        sql=fr'INSERT INTO users'
            fr'            (id, username, password, pub_key)'
            fr'     VALUES (%(userID)s, %(username)s, %(password)s, %(pub_key)s)'
            fr'  RETURNING id',
        userID=userID,
        username=username,
        password=password,
        pub_key=pub_key
    )
    try:
        id_, = await pool_handler.pool.fetchrow(sql, *params)
    except asyncpg.exceptions.UniqueViolationError:
        raise exc.UniqueViolationError
    return id_


async def read_by_username(username: str) -> tuple[str, str]:
    # Object of type UUID is not JSON serializable
    sql, params = pyformat2psql(
        sql=fr"SELECT id, password"
            fr"  FROM users"
            fr" WHERE username = %(username)s",
        username=username,
    )
    id_, password = await pool_handler.pool.fetchrow(sql, *params)
    return str(id_), password


async def is_duplicate_username(username: str) -> bool:
    sql, params = pyformat2psql(
        sql=fr"SELECT COUNT(*)"
            fr"  FROM users"
            fr" WHERE username = %(username)s",
        username=username,
    )
    count, = await pool_handler.pool.fetchrow(sql, *params)
    return count > 0
