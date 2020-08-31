from pymysql import cursors
from app.models.BaseRept import BaseRept

class Entity(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def get_all(self):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_entity"
            cursor.execute(query)
            return cursor.fetchall()

    def by_prefix(self, prefix):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"select * from tbl_entity where prefix = '{prefix}'"
            cursor.execute(query)
            return cursor.fetchone()

    def by_user(self, user_id):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"""
                    select e.id, e.name, e.prefix from tbl_user_entity ue INNER JOIN tbl_entity e on e.id = ue.entity_id
                    where ue.user_id = {user_id} and e.status = '1'
                """
            cursor.execute(query)
            rows = cursor.fetchall()

        return rows
