import aiomysql
from aiomysql import Pool

import os

async def get_pool(autocommit: bool = True) -> Pool:
    database_host = os.getenv('database_host')
    database_user = os.getenv('database_user')
    database_password = os.getenv('database_password')   
    database_name = os.getenv('database_name')

    host, port = database_host.split(':')
    return await aiomysql.create_pool(
        host=host,
        port=int(port),
        user=database_user,
        password=database_password,
        db=database_name,
        autocommit=autocommit
    )     