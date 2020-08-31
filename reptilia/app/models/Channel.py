from pymysql import cursors
from app.models.BaseRept import BaseRept

class Channel(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def list_channels(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = "select * from tbl_channel"
            cursor.execute(query)
            return cursor.fetchall()
        
    def by_id(self, _id):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_channel where id = {_id}"
            cursor.execute(query)
            return cursor.fetchone()