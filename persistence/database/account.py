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


async def read(account_id: int) -> do.Account:
    sql, params = pyformat2psql(
        sql=fr"SELECT id, username, role, student_id, real_name"
            fr"  FROM account"
            fr" WHERE id = %(account_id)s",
        account_id=account_id
    )
    try:
        id_, username, role, student_id, real_name = await pool_handler.pool.fetchrow(sql, *params)
    except TypeError:
        raise exc.NotFound
    return do.Account(id=id_, username=username, role=RoleType(role),
                      student_id=student_id, real_name=real_name)


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


async def delete(account_id: int) -> None:
    sql, params = pyformat2psql(
        sql=fr"DELETE FROM account"
            fr" WHERE id = %(account_id)s",
        account_id=account_id
    )
    return await pool_handler.pool.execute(sql, *params)


async def browse_by_role(role: RoleType) -> Sequence[do.Account]:
    sql, params = pyformat2psql(
        sql=fr"SELECT id, username, role, student_id, real_name"
            fr"  FROM account"
            fr" WHERE role = %(role)s"
            fr" ORDER BY id ASC",
        role=role.value,
    )
    records = await pool_handler.pool.fetch(sql, *params)
    return [do.Account(id=id_, username=username, role=RoleType(role), real_name=real_name, student_id=student_id)
            for id_, username, role, real_name, student_id in records]
