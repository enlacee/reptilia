from pymysql import connect, cursors

from app.models.BaseRept import BaseRept

class Module(BaseRept):
    def __init__(self, conn_params = None):
        super().__init__(conn_params)

    def by_user(self, user_id):
        with self.conn.cursor(cursors.DictCursor) as cursor:
            query = f"""
                    select m.* from tbl_role_user ru inner join tbl_module_role mr on ru.role_id = mr.role_id
                    inner join tbl_module m on m.id = mr.module_id where ru.user_id = {user_id} and m.status = '1'
                """
            cursor.execute(query)

            return cursor.fetchall()
