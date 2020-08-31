from pymysql import cursors
from app.models.Campaign import Campaign
from app.models.BaseRept import BaseRept

class Carrier(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def list_carriers(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = "select * from tbl_carrier"
            cursor.execute(query)
            return cursor.fetchall()
