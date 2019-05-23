from foundation.singleton import Singleton

import asyncpg


class DataBaseManager(metaclass=Singleton):
    """
    Singleton class for maintaining a pool to the database.
    """

    def __init__(self, db_type: str='postgres', db_server: str = None, user: str = None, password: str = None,
                 port: int = None, database_name: str = None, min_size: int=1, max_size: int=1 ):
        self.db_type = db_type
        self.db_server = db_server
        self.user = user
        self.password = password
        self.port = port
        self.database_name = database_name
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None

    async def connect(self):
        """
        Create a connection pool.
        :return:
        """
        if self.pool is None:
            if self.db_type == 'postgres':
                dsn = 'postgres://{user}:{password}@{host}:{port}/{database}'.format(user=self.user,
                                                                                 password=self.password,
                                                                                 host=self.db_server,
                                                                                 port=self.port,
                                                                                 database=self.database_name)

                self.pool = await asyncpg.create_pool(dsn=dsn, command_timeout=60)
            else:
                raise ValueError('Invalid database type provided')
        else:
            pass

    async def acquire(self) -> asyncpg.Connection:
        """
        acquires a connection from the pool
        :return:
        """
        if self.pool is None:
            await self.connect()

        return await self.pool.acquire()

    def release(self, con: asyncpg.Connection):
        """
        releases a connection
        :return:
        """
        if self.pool is None:
            raise ValueError("The pool is not defined")
        else:
            return self.pool.release(con)

    def close(self):
        """
        closes the pool of connections
        :return:
        """
        if self.pool is None:
            raise ValueError("The pool is not defined")
        else:
            return self.pool.close()
