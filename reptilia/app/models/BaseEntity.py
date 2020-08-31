from pymysql import connect

import os

class BaseEntity:
    def __init__(self, db):
        if db == 'movistar':
            self.conn_params = {
                'host': os.getenv('ENTITY_HOST'),
                'user': os.getenv('ENTITY_USER'),
                'password': os.getenv('ENTITY_PASSWORD'),
                'db': db,
                'autocommit': True
            }
        else:
            self.conn_params = {
                'host': os.getenv('INIT_ENTITY_HOST'),
                'user': os.getenv('INIT_ENTITY_USER'),
                'password': os.getenv('INIT_ENTITY_PASSWORD'),
                'db': db,
                'autocommit': True
            }
        
        self.conn = connect(**self.conn_params)

    def __enter__(self):
        return self

    def __exit__(self, _type, value, traceback):
        if self.conn and self.conn.open: self.conn.close()