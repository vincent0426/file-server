from base import do

from .util import pyformat2psql
from . import pool_handler
import uuid

from fastapi import UploadFile

async def add(file_id: uuid.UUID, from_uid: uuid.UUID, to_uid: uuid.UUID) -> uuid.UUID:
    t_id = uuid.uuid4()
    sql, params = pyformat2psql(
        sql=fr"INSERT INTO transactions (id, file_id, from_uid, to_uid)"
            fr" VALUES (%(t_id)s, %(file_id)s, %(from_uid)s, %(to_uid)s)"
            fr" RETURNING id",
        t_id=t_id, file_id=file_id, from_uid=from_uid, to_uid=to_uid
    )
    t_id = await pool_handler.pool.fetchval(sql, *params)
    return t_id

async def get_all(to_uid: uuid.UUID) -> list:
    sql, params = pyformat2psql(
        sql=fr"SELECT id, file_id, from_uid, to_uid"
            fr" FROM transactions"
            fr" WHERE to_uid = %(to_uid)s",
        to_uid=to_uid
    )
    transactions = await pool_handler.pool.fetch(sql, *params)
    return transactions

async def get(transaction_id: uuid.UUID) -> dict:
    sql, params = pyformat2psql(
        sql=fr"SELECT id, file_id, from_uid, to_uid"
            fr" FROM transactions"
            fr" WHERE id = %(transaction_id)s",
        transaction_id=transaction_id
    )
    transaction = await pool_handler.pool.fetchrow(sql, *params)
    return dict(transaction)