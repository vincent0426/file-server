from base import do

from .util import pyformat2psql
from . import pool_handler
import exceptions as exc

import uuid

async def get_by_uid(uid: str) -> str:
    sql, params = pyformat2psql(
        sql=fr"SELECT pub_key"
            fr" FROM users"
            fr" WHERE id = %(uid)s",
        uid=uid
    )
    
    pub_key = await pool_handler.pool.fetchval(sql, *params)
    # Any exception that is not caught will be handled by the default exception handler
    if pub_key is None:
        print("pub_key is None")
        raise exc.NotFound
    return pub_key
