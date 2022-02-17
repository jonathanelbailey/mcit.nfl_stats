import sqlalchemy
import pyodbc
import urllib

pyodbc.pooling = False


class DBConnect:
    def __init__(self, user, password, host, database, db_debug=False):
        self.username = user
        self.password = password
        self.db_host = host
        self.database = database
        self.db_debug = db_debug
        self.connection_string = 'mssql+pyodbc:///?odbc_connect={}'.format(
            urllib.parse.quote_plus(
                f'DSN={self.db_host};DATABASE={self.database};UID={self.username};PWD={self.password}'
            )
        )
        self.engine = sqlalchemy.create_engine(self.connection_string, echo=db_debug, fast_executemany=True)