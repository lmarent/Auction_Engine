from foundation.singleton import Singleton

import asyncpg
from utils.auction_utils import log


class DataBaseManager(metaclass=Singleton):
    """
    Singleton class for maintaining a pool to the database.
    """

    def __init__(self, db_type: str = 'postgres', db_server: str = None, user: str = None, password: str = None,
                 port: int = None, database_name: str = None, min_size: int = 1, max_size: int = 1):
        self.db_type = db_type
        self.db_server = db_server
        self.user = user
        self.password = password
        self.port = port
        self.database_name = database_name
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None
        self.logger = log().get_logger()

        print('database manager in init')

    async def connect(self):
        """
        Create a connection pool.
        :return:
        """
        if self.pool is None:
            self.logger.info("connecting to the database server")
            if self.db_type == 'postgres':
                dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(user=self.user,
                                                                                     password=self.password,
                                                                                     host=self.db_server,
                                                                                     port=self.port,
                                                                                     database=self.database_name)

                self.logger.info("dsn: {0}".format(dsn))
                self.pool = await asyncpg.create_pool(dsn=dsn, command_timeout=60)
                if self.pool is not None:
                    self.logger.info("after connected pool was established")
                else:
                    self.logger.error("after connected pool was not established")
            else:
                raise ValueError('Invalid database type provided')
        else:
            pass

    async def acquire(self) -> asyncpg.Connection:
        """
        acquires a connection from the pool
        :return:
        """
        self.logger.info("pool values is {0}".format(str(self.pool is None)))
        if self.pool is None:
            await self.connect()
            self.logger.info("after database connection")

        assert self.pool is not None, "Datebase pool is still none"
        return await self.pool.acquire()

    def release(self, con: asyncpg.Connection):
        """
        releases a connection
        :return:
        """
        if self.pool is None:
            raise ValueError("The pool is not defined")
        else:
            self.logger.info("release connection")
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
