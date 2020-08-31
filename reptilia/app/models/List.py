from pymysql import cursors
from app.models.BaseVici import BaseVici

import datetime

class List(BaseVici):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def get_all(self):
       with self.conn.cursor(cursors.DictCursor) as cursor:
            query = "select * from vicidial_lists"
            cursor.execute(query)

            return cursor.fetchall()

    def get_actives(self):
       with self.conn.cursor(cursors.DictCursor) as cursor:
            query = "select list_id, list_name from vicidial_lists where active = 'Y'"
            cursor.execute(query)

            return cursor.fetchall()

    def add(self, list_id, list_name, campaign_id):
        with self.conn.cursor() as cursor:
            query = """insert into vicidial_lists(list_id, list_name, campaign_id, active, list_description, list_changedate,
                        time_zone_setting, inventory_report, expiration_date, local_call_time, user_new_lead_limit, default_xfer_group,
                        daily_reset_limit, resets_today, auto_active_list_rank, cache_count, cache_count_new) values('{0}', '{1}', '{2}', 'Y',
                        '{1}', '{3}', 'COUNTRY_AND_AREA_CODE', 'Y', '2099-12-31', 'campaign', -1, '---NONE---', -1, 0, 0, 0, 0)
                    """.format(list_id, list_name, campaign_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cursor.execute(query)

    def update_status(self, list_id, status):
        with self.conn.cursor() as cursor:
            query = f"update vicidial_lists set active = '{status}' where list_id = {list_id}"
            cursor.execute(query)
