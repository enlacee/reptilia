from pymysql import connect

import os

class BaseReport:
    def __init__(self, db):
        self.conn_params = {
            'host': os.getenv('REPORT_HOST'),
            'user': os.getenv('REPORT_USER'),
            'password': os.getenv('REPORT_PASSWORD'),
            'db': db,
            'autocommit': True
        }
        
        self.conn = connect(**self.conn_params)

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        if self.conn and self.conn.open: self.conn.close()