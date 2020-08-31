from pymysql import connect

import os

class BaseRept:
    def __init__(self, conn_params):
        conn_params = {
            'host': os.getenv('ADMIN_HOST'),
            'user': os.getenv('ADMIN_USER'),
            'password': os.getenv('ADMIN_PASSWORD'),
            'db' : os.getenv('ADMIN_DB'),
            'autocommit' : True
        } if not conn_params else conn_params

        self.conn = connect(**conn_params)

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        if self.conn and self.conn.open: self.conn.close()