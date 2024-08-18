import pymysql

from pymysql.cursors import DictCursor
from typing import Union


class Database(object):

    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            charset='utf8mb4',
            cursorclass=DictCursor,
            autocommit=True
        )

    def query(self, query: str, return_output=False) -> Union[tuple, None]:
        with self.connection.cursor() as cursor:
            cursor.execute(query)

            if return_output:
                return cursor.fetchall()
