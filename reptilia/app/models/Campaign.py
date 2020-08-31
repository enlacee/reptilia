from pymysql import cursors
from app.models.BaseVici import BaseVici

class Campaign(BaseVici):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def get_campaign_by_list(self, list_id):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select campaign_id from vicidial_lists where list_id = {list_id} and active = 'Y'"
            cursor.execute(query)
            return cursor.fetchone()

    def get_all(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = "select * from vicidial_campaigns"
            cursor.execute(query)
            return cursor.fetchall()

    def update_status(self, campaign_id, status):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"update vicidial_campaigns set active = '{status}' where campaign_id = {campaign_id}"
            cursor.execute(query)